use smoltcp::phy::ChecksumCapabilities;
use smoltcp::wire::{IpProtocol, Ipv4Address, Ipv4Packet, Ipv4Repr};
use std::fs;
use std::path::Path;
use std::sync::OnceLock;

const BUFFER_LEN: usize = 64;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Version {
    V4,
    V5,
}

impl Version {
    fn as_u8(self) -> u8 {
        match self {
            Version::V4 => 4,
            Version::V5 => 5,
        }
    }
}

#[derive(Clone, Copy, Debug)]
enum TotalLenMode {
    Exact,
    LessThanHeader,
    BeyondBuffer,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum ChecksumMode {
    Valid,
    Invalid,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum FragmentMode {
    None,
    MoreFrags,
}

#[derive(Clone, Copy, Debug)]
enum ProtocolKind {
    Icmp,
    Udp,
    Tcp,
}

impl ProtocolKind {
    fn as_proto(self) -> IpProtocol {
        match self {
            ProtocolKind::Icmp => IpProtocol::Icmp,
            ProtocolKind::Udp => IpProtocol::Udp,
            ProtocolKind::Tcp => IpProtocol::Tcp,
        }
    }
}

#[derive(Clone, Copy, Debug)]
struct Case {
    version: Version,
    header_len: usize,
    total_len_mode: TotalLenMode,
    total_len: usize,
    checksum: ChecksumMode,
    fragment: FragmentMode,
    protocol: ProtocolKind,
}

fn expected_new_checked(case: &Case) -> bool {
    if BUFFER_LEN < 20 {
        return false;
    }
    if BUFFER_LEN < case.header_len {
        return false;
    }
    if case.header_len > case.total_len {
        return false;
    }
    if case.total_len > BUFFER_LEN {
        return false;
    }
    true
}

fn expected_parse_ok(case: &Case) -> bool {
    if !expected_new_checked(case) {
        return false;
    }
    if case.version != Version::V4 {
        return false;
    }
    if case.checksum != ChecksumMode::Valid {
        return false;
    }
    if case.fragment != FragmentMode::None && !fragments_supported() {
        return false;
    }
    true
}

fn fragments_supported() -> bool {
    static SUPPORT: OnceLock<bool> = OnceLock::new();
    *SUPPORT.get_or_init(|| {
        let mut buffer = vec![0u8; BUFFER_LEN];
        let mut packet = Ipv4Packet::new_unchecked(&mut buffer);
        packet.set_version(4);
        packet.set_header_len(20);
        packet.set_total_len(28);
        packet.set_ident(0x1234);
        packet.set_hop_limit(64);
        packet.set_next_header(IpProtocol::Udp);
        packet.set_src_addr(Ipv4Address::new(192, 168, 1, 10));
        packet.set_dst_addr(Ipv4Address::new(192, 168, 1, 20));
        packet.clear_flags();
        packet.set_more_frags(true);
        packet.set_dont_frag(false);
        packet.set_frag_offset(0);
        packet.fill_checksum();

        let packet = Ipv4Packet::new_unchecked(&buffer);
        Ipv4Repr::parse(&packet, &ChecksumCapabilities::default()).is_ok()
    })
}

fn generate_cases() -> Vec<Case> {
    let versions = [Version::V4, Version::V5];
    let header_lens = [20usize, 16, 24];
    let total_len_modes = [
        TotalLenMode::Exact,
        TotalLenMode::LessThanHeader,
        TotalLenMode::BeyondBuffer,
    ];
    let checksums = [ChecksumMode::Valid, ChecksumMode::Invalid];
    let fragments = [FragmentMode::None, FragmentMode::MoreFrags];
    let protocols = [ProtocolKind::Icmp, ProtocolKind::Udp, ProtocolKind::Tcp];

    let mut cases = Vec::new();
    for &version in &versions {
        for &header_len in &header_lens {
            for &total_mode in &total_len_modes {
                for &checksum in &checksums {
                    for &fragment in &fragments {
                        for &protocol in &protocols {
                            let total_len = match total_mode {
                                TotalLenMode::Exact => header_len + 8,
                                TotalLenMode::LessThanHeader => header_len.saturating_sub(1),
                                TotalLenMode::BeyondBuffer => BUFFER_LEN + 1,
                            };
                            cases.push(Case {
                                version,
                                header_len,
                                total_len_mode: total_mode,
                                total_len,
                                checksum,
                                fragment,
                                protocol,
                            });
                        }
                    }
                }
            }
        }
    }
    cases
}

fn build_packet(case: &Case) -> Vec<u8> {
    let mut buffer = vec![0u8; BUFFER_LEN];
    let mut packet = Ipv4Packet::new_unchecked(&mut buffer);
    packet.set_version(case.version.as_u8());
    packet.set_header_len(case.header_len as u8);
    packet.set_total_len(case.total_len as u16);
    packet.set_ident(0x1234);
    packet.set_hop_limit(64);
    packet.set_next_header(case.protocol.as_proto());
    packet.set_src_addr(Ipv4Address::new(192, 168, 1, 10));
    packet.set_dst_addr(Ipv4Address::new(192, 168, 1, 20));
    packet.clear_flags();
    packet.set_more_frags(case.fragment == FragmentMode::MoreFrags);
    packet.set_dont_frag(false);
    packet.set_frag_offset(0);

    match case.checksum {
        ChecksumMode::Valid => packet.fill_checksum(),
        ChecksumMode::Invalid => packet.set_checksum(0x1234),
    }

    buffer
}

fn write_cases_csv(cases: &[Case], rows: &[(bool, bool, bool, bool)], path: &Path) {
    let mut out = String::new();
    out.push_str("case_id,version,header_len,total_len_mode,total_len,checksum,fragment,protocol,expected_new_checked,actual_new_checked,expected_parse,actual_parse\n");

    for (i, (case, result)) in cases.iter().zip(rows.iter()).enumerate() {
        let (exp_new, act_new, exp_parse, act_parse) = *result;
        out.push_str(&format!(
            "{},{:?},{},{:?},{},{:?},{:?},{:?},{},{},{},{}\n",
            i + 1,
            case.version,
            case.header_len,
            case.total_len_mode,
            case.total_len,
            case.checksum,
            case.fragment,
            case.protocol,
            exp_new,
            act_new,
            exp_parse,
            act_parse
        ));
    }

    fs::write(path, out).expect("write cases csv");
}

#[test]
fn ipv4_combinatorial_partition() {
    let cases = generate_cases();
    let suite_dir = Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap();
    let platform = std::env::var("SEC_TEST_PLATFORM").unwrap_or_else(|_| "unknown".to_string());
    let cases_path = suite_dir.join(format!("ipv4_cases_{}.csv", platform));

    let mut rows = Vec::with_capacity(cases.len());
    let mut failures = 0usize;
    let mut matched = 0usize;

    for case in &cases {
        let buffer = build_packet(case);
        let new_checked_ok = Ipv4Packet::new_checked(&buffer).is_ok();
        let exp_new_checked = expected_new_checked(case);

        let parse_ok = if let Ok(packet) = Ipv4Packet::new_checked(&buffer) {
            Ipv4Repr::parse(&packet, &ChecksumCapabilities::default()).is_ok()
        } else {
            false
        };

        let exp_parse = expected_parse_ok(case);
        if exp_new_checked == new_checked_ok && exp_parse == parse_ok {
            matched += 1;
        } else {
            failures += 1;
            eprintln!(
                "Mismatch: case={:?} exp_new={} act_new={} exp_parse={} act_parse={}",
                case, exp_new_checked, new_checked_ok, exp_parse, parse_ok
            );
        }

        rows.push((exp_new_checked, new_checked_ok, exp_parse, parse_ok));
    }

    write_cases_csv(&cases, &rows, &cases_path);

    println!("generated_cases={}", cases.len());
    println!("matched_expectation={}", matched);

    assert!(failures == 0, "{} cases failed", failures);
}
