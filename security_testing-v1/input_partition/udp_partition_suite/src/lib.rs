use smoltcp::phy::ChecksumCapabilities;
use smoltcp::wire::{IpAddress, UdpPacket, UdpRepr};
use std::fs;
use std::path::Path;

const UDP_HEADER_LEN: usize = 8;

#[derive(Clone, Copy, Debug)]
enum ChecksumMode {
    Valid,
    Zero,
    Invalid,
}

#[derive(Clone, Copy, Debug)]
enum IpFamily {
    V4,
    V6,
}

#[derive(Clone, Copy, Debug)]
struct Case {
    buf_len: usize,
    len_field: usize,
    dst_port: u16,
    checksum_mode: ChecksumMode,
    ip_family: IpFamily,
    rx_on: bool,
}

fn generate_cases() -> Vec<Case> {
    let buf_lens = [0usize, 7, 8, 12];
    let len_fields = [0usize, 4, 8, 12, 20];
    let dst_ports = [0u16, 53u16];
    let checksum_modes = [ChecksumMode::Valid, ChecksumMode::Zero, ChecksumMode::Invalid];
    let ip_families = [IpFamily::V4, IpFamily::V6];
    let rx_on = [true, false];

    let mut cases = Vec::new();
    for &buf_len in &buf_lens {
        for &len_field in &len_fields {
            for &dst_port in &dst_ports {
                for &checksum_mode in &checksum_modes {
                    for &ip_family in &ip_families {
                        for &rx in &rx_on {
                            cases.push(Case {
                                buf_len,
                                len_field,
                                dst_port,
                                checksum_mode,
                                ip_family,
                                rx_on: rx,
                            });
                        }
                    }
                }
            }
        }
    }
    cases
}

fn len_ok(case: &Case) -> bool {
    case.buf_len >= UDP_HEADER_LEN
        && case.len_field >= UDP_HEADER_LEN
        && case.len_field <= case.buf_len
}

fn expected_parse_ok(case: &Case) -> bool {
    if !len_ok(case) {
        return false;
    }
    if case.dst_port == 0 {
        return false;
    }
    if !case.rx_on {
        return true;
    }

    match (case.checksum_mode, case.ip_family) {
        (ChecksumMode::Valid, _) => true,
        (ChecksumMode::Invalid, _) => false,
        (ChecksumMode::Zero, _) => true,
    }
}

fn build_packet(case: &Case) -> Vec<u8> {
    let mut buffer = vec![0u8; case.buf_len];
    if case.buf_len < UDP_HEADER_LEN {
        return buffer;
    }

    let src = match case.ip_family {
        IpFamily::V4 => IpAddress::v4(192, 168, 1, 10),
        IpFamily::V6 => IpAddress::v6(0x2001, 0xdb8, 0, 0, 0, 0, 0, 1),
    };
    let dst = match case.ip_family {
        IpFamily::V4 => IpAddress::v4(192, 168, 1, 20),
        IpFamily::V6 => IpAddress::v6(0x2001, 0xdb8, 0, 0, 0, 0, 0, 2),
    };

    let mut packet = UdpPacket::new_unchecked(&mut buffer);
    packet.set_src_port(1234);
    packet.set_dst_port(case.dst_port);
    packet.set_len(case.len_field as u16);

    if len_ok(case) {
        let payload_len = case.len_field - UDP_HEADER_LEN;
        if payload_len > 0 {
            packet.payload_mut()[..payload_len].fill(0xaa);
        }
    }

    match case.checksum_mode {
        ChecksumMode::Valid => {
            if len_ok(case) {
                packet.fill_checksum(&src, &dst);
            } else {
                packet.set_checksum(0x1234);
            }
        }
        ChecksumMode::Zero => packet.set_checksum(0),
        ChecksumMode::Invalid => packet.set_checksum(0x1234),
    }

    buffer
}

fn write_cases_csv(cases: &[Case], rows: &[(bool, bool, bool, bool)], path: &Path) {
    let mut out = String::new();
    out.push_str("case_id,buf_len,len_field,dst_port,checksum_mode,ip_family,rx_on,expected_new_checked,actual_new_checked,expected_parse,actual_parse\n");

    for (i, (case, result)) in cases.iter().zip(rows.iter()).enumerate() {
        let (exp_new, act_new, exp_parse, act_parse) = *result;
        out.push_str(&format!(
            "{},{},{},{},{:?},{:?},{},{},{},{},{}\n",
            i + 1,
            case.buf_len,
            case.len_field,
            case.dst_port,
            case.checksum_mode,
            case.ip_family,
            case.rx_on,
            exp_new,
            act_new,
            exp_parse,
            act_parse
        ));
    }

    fs::write(path, out).expect("write cases csv");
}

#[test]
fn udp_input_partitioning() {
    let cases = generate_cases();
    let suite_dir = Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap();
    let cases_path = suite_dir.join("udp_cases.csv");

    let mut rows = Vec::with_capacity(cases.len());
    let mut failures = 0usize;

    for case in &cases {
        let buffer = build_packet(case);
        let new_checked_ok = UdpPacket::new_checked(&buffer).is_ok();
        let exp_new_checked = len_ok(case);

        let parse_ok = if let Ok(packet) = UdpPacket::new_checked(&buffer) {
            let caps = if case.rx_on {
                ChecksumCapabilities::default()
            } else {
                ChecksumCapabilities::ignored()
            };
            let src = match case.ip_family {
                IpFamily::V4 => IpAddress::v4(192, 168, 1, 10),
                IpFamily::V6 => IpAddress::v6(0x2001, 0xdb8, 0, 0, 0, 0, 0, 1),
            };
            let dst = match case.ip_family {
                IpFamily::V4 => IpAddress::v4(192, 168, 1, 20),
                IpFamily::V6 => IpAddress::v6(0x2001, 0xdb8, 0, 0, 0, 0, 0, 2),
            };
            UdpRepr::parse(&packet, &src, &dst, &caps).is_ok()
        } else {
            false
        };

        let exp_parse = expected_parse_ok(case);
        if exp_new_checked != new_checked_ok || exp_parse != parse_ok {
            failures += 1;
            eprintln!(
                "Mismatch: case={:?} exp_new={} act_new={} exp_parse={} act_parse={}",
                case, exp_new_checked, new_checked_ok, exp_parse, parse_ok
            );
        }

        rows.push((exp_new_checked, new_checked_ok, exp_parse, parse_ok));
    }

    write_cases_csv(&cases, &rows, &cases_path);

    assert!(failures == 0, "{} cases failed", failures);
}
