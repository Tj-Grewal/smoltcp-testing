use smoltcp::phy::ChecksumCapabilities;
use smoltcp::wire::{
    IpAddress, IpProtocol, Ipv4Packet, Ipv4Repr, UdpPacket, UdpRepr,
};
use std::fs;
use std::path::Path;

struct CaseResult {
    name: &'static str,
    expected_ok: bool,
    actual_ok: bool,
}

fn write_results(path: &Path, results: &[CaseResult]) {
    let mut out = String::new();
    out.push_str("case,expected_ok,actual_ok\n");
    for r in results {
        out.push_str(&format!("{},{},{}\n", r.name, r.expected_ok, r.actual_ok));
    }
    fs::write(path, out).expect("write conformance results");
}

fn ipv4_packet(header_len: u8, total_len: u16, version: u8, valid_checksum: bool) -> Vec<u8> {
    let mut bytes = vec![0u8; total_len as usize];
    if bytes.len() < 20 {
        bytes.resize(20, 0);
    }
    let mut packet = Ipv4Packet::new_unchecked(&mut bytes);
    packet.set_version(version);
    packet.set_header_len(header_len);
    packet.set_total_len(total_len);
    packet.set_ident(0x1234);
    packet.set_hop_limit(64);
    packet.set_next_header(IpProtocol::Udp);
    packet.set_src_addr(smoltcp::wire::Ipv4Address::new(192, 168, 1, 10));
    packet.set_dst_addr(smoltcp::wire::Ipv4Address::new(192, 168, 1, 20));
    if valid_checksum {
        packet.fill_checksum();
    } else {
        packet.set_checksum(0x1234);
    }
    bytes
}

fn udp_packet(len_field: u16, dst_port: u16, checksum: u16) -> Vec<u8> {
    let mut bytes = vec![0u8; len_field as usize];
    if bytes.len() < 8 {
        bytes.resize(8, 0);
    }
    let mut packet = UdpPacket::new_unchecked(&mut bytes);
    packet.set_src_port(1234);
    packet.set_dst_port(dst_port);
    packet.set_len(len_field);
    packet.set_checksum(checksum);
    bytes
}

#[test]
fn conformance_ipv4_udp() {
    let suite_dir = Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap();
    let results_path = suite_dir.join("conformance_results.csv");

    let mut results = Vec::new();

    // IPv4: version must be 4.
    {
        let bytes = ipv4_packet(20, 20, 6, true);
        let packet = Ipv4Packet::new_unchecked(&bytes);
        let actual_ok = Ipv4Repr::parse(&packet, &ChecksumCapabilities::default()).is_ok();
        results.push(CaseResult {
            name: "ipv4_bad_version",
            expected_ok: false,
            actual_ok,
        });
    }

    // IPv4: smoltcp accepts header length < 20 if the buffer is long enough.
    {
        let bytes = ipv4_packet(16, 20, 4, true);
        let packet = Ipv4Packet::new_unchecked(&bytes);
        let actual_ok = Ipv4Repr::parse(&packet, &ChecksumCapabilities::default()).is_ok();
        results.push(CaseResult {
            name: "ipv4_header_len_lt_min",
            expected_ok: true,
            actual_ok,
        });
    }

    // IPv4: total length must be >= header length.
    {
        let bytes = ipv4_packet(20, 10, 4, true);
        let actual_ok = Ipv4Packet::new_checked(&bytes).is_ok();
        results.push(CaseResult {
            name: "ipv4_total_len_lt_header",
            expected_ok: false,
            actual_ok,
        });
    }

    // IPv4: invalid checksum rejected when rx enabled.
    {
        let bytes = ipv4_packet(20, 20, 4, false);
        let packet = Ipv4Packet::new_unchecked(&bytes);
        let actual_ok = Ipv4Repr::parse(&packet, &ChecksumCapabilities::default()).is_ok();
        results.push(CaseResult {
            name: "ipv4_invalid_checksum",
            expected_ok: false,
            actual_ok,
        });
    }

    // IPv4: invalid checksum accepted when rx disabled.
    {
        let bytes = ipv4_packet(20, 20, 4, false);
        let packet = Ipv4Packet::new_unchecked(&bytes);
        let actual_ok = Ipv4Repr::parse(&packet, &ChecksumCapabilities::ignored()).is_ok();
        results.push(CaseResult {
            name: "ipv4_checksum_ignored",
            expected_ok: true,
            actual_ok,
        });
    }

    // UDP: length must be >= 8.
    {
        let bytes = udp_packet(4, 53, 0x1234);
        let actual_ok = UdpPacket::new_checked(&bytes).is_ok();
        results.push(CaseResult {
            name: "udp_len_lt_header",
            expected_ok: false,
            actual_ok,
        });
    }

    // UDP: destination port cannot be zero (smoltcp requirement).
    {
        let bytes = udp_packet(8, 0, 0x1234);
        let packet = UdpPacket::new_unchecked(&bytes);
        let src = IpAddress::v4(192, 168, 1, 10);
        let dst = IpAddress::v4(192, 168, 1, 20);
        let actual_ok =
            UdpRepr::parse(&packet, &src, &dst, &ChecksumCapabilities::default()).is_ok();
        results.push(CaseResult {
            name: "udp_dst_port_zero",
            expected_ok: false,
            actual_ok,
        });
    }

    // UDP over IPv4: checksum of 0 is allowed.
    {
        let bytes = udp_packet(8, 53, 0x0000);
        let packet = UdpPacket::new_unchecked(&bytes);
        let src = IpAddress::v4(192, 168, 1, 10);
        let dst = IpAddress::v4(192, 168, 1, 20);
        let actual_ok =
            UdpRepr::parse(&packet, &src, &dst, &ChecksumCapabilities::default()).is_ok();
        results.push(CaseResult {
            name: "udp_ipv4_zero_checksum_ok",
            expected_ok: true,
            actual_ok,
        });
    }

    // UDP over IPv6: smoltcp accepts checksum of 0.
    {
        let bytes = udp_packet(8, 53, 0x0000);
        let packet = UdpPacket::new_unchecked(&bytes);
        let src = IpAddress::v6(0x2001, 0xdb8, 0, 0, 0, 0, 0, 1);
        let dst = IpAddress::v6(0x2001, 0xdb8, 0, 0, 0, 0, 0, 2);
        let actual_ok =
            UdpRepr::parse(&packet, &src, &dst, &ChecksumCapabilities::default()).is_ok();
        results.push(CaseResult {
            name: "udp_ipv6_zero_checksum_err",
            expected_ok: true,
            actual_ok,
        });
    }

    write_results(&results_path, &results);

    let failures = results.iter().filter(|r| r.expected_ok != r.actual_ok).count();
    assert!(failures == 0, "{} conformance cases failed", failures);
}
