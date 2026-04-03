use smoltcp::phy::ChecksumCapabilities;
use smoltcp::storage::RingBuffer;
use smoltcp::wire::{IpAddress, IpProtocol, Ipv4Address, Ipv4Packet, Ipv4Repr, UdpPacket, UdpRepr};
use std::hint::black_box;
use std::time::Instant;

fn iters_from_env() -> u64 {
    std::env::var("MICROBENCH_ITERS")
        .ok()
        .and_then(|v| v.parse::<u64>().ok())
        .unwrap_or(10000)
}

fn run_metric(name: &str, iters: u64, mut f: impl FnMut()) {
    let start = Instant::now();
    for _ in 0..iters {
        f();
    }
    let duration = start.elapsed();
    let total_ns = duration.as_nanos();
    let ns_per_iter = total_ns as f64 / iters as f64;
    println!(
        "METRIC,{},{},{},{}",
        name, iters, total_ns, format!("{:.4}", ns_per_iter)
    );
}

fn make_ipv4_packet() -> Vec<u8> {
    let repr = Ipv4Repr {
        src_addr: Ipv4Address::new(192, 168, 1, 10),
        dst_addr: Ipv4Address::new(192, 168, 1, 20),
        next_header: IpProtocol::Udp,
        payload_len: 8,
        hop_limit: 64,
    };
    let mut bytes = vec![0u8; repr.buffer_len() + repr.payload_len];
    let mut packet = Ipv4Packet::new_unchecked(&mut bytes);
    repr.emit(&mut packet, &ChecksumCapabilities::default());
    bytes
}

fn make_udp_packet(payload: &[u8]) -> Vec<u8> {
    let repr = UdpRepr {
        src_port: 1234,
        dst_port: 8080,
    };
    let mut bytes = vec![0u8; repr.header_len() + payload.len()];
    let mut packet = UdpPacket::new_unchecked(&mut bytes);
    let src = IpAddress::v4(192, 168, 1, 10);
    let dst = IpAddress::v4(192, 168, 1, 20);
    repr.emit(
        &mut packet,
        &src,
        &dst,
        payload.len(),
        |buf| buf.copy_from_slice(payload),
        &ChecksumCapabilities::default(),
    );
    bytes
}

#[test]
fn performance_microbench() {
    let iters = iters_from_env();

    let ipv4_bytes = make_ipv4_packet();
    run_metric("ipv4_parse", iters, || {
        let packet = Ipv4Packet::new_checked(&ipv4_bytes).unwrap();
        let repr = Ipv4Repr::parse(&packet, &ChecksumCapabilities::default()).unwrap();
        black_box(repr);
    });

    let payload = vec![0xa5u8; 32];
    let udp_bytes = make_udp_packet(&payload);
    let src = IpAddress::v4(192, 168, 1, 10);
    let dst = IpAddress::v4(192, 168, 1, 20);
    let mut emit_buf = vec![0u8; udp_bytes.len()];

    run_metric("udp_parse_emit", iters, || {
        let packet = UdpPacket::new_checked(&udp_bytes).unwrap();
        let repr = UdpRepr::parse(&packet, &src, &dst, &ChecksumCapabilities::default()).unwrap();
        let mut out = UdpPacket::new_unchecked(&mut emit_buf);
        repr.emit(
            &mut out,
            &src,
            &dst,
            payload.len(),
            |buf| buf.copy_from_slice(&payload),
            &ChecksumCapabilities::default(),
        );
        black_box(out.checksum());
    });

    let mut ring = RingBuffer::new(vec![0u8; 256]);
    let data = vec![0x11u8; 64];
    let mut out = vec![0u8; 64];

    run_metric("ring_buffer_cycle", iters, || {
        let added = ring.enqueue_slice(&data);
        let removed = ring.dequeue_slice(&mut out);
        black_box(added);
        black_box(removed);
    });
}
