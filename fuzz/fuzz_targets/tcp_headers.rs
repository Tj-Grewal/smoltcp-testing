#![no_main]
use libfuzzer_sys::fuzz_target;
use smoltcp::phy::ChecksumCapabilities;
use smoltcp::wire::{IpAddress, TcpPacket, TcpRepr};

fuzz_target!(|data: &[u8]| {
    if let Ok(packet) = TcpPacket::new_checked(data) {
        let src = IpAddress::v4(127, 0, 0, 1);
        let dst = IpAddress::v4(127, 0, 0, 2);
        if let Ok(repr) = TcpRepr::parse(&packet, &src, &dst, &ChecksumCapabilities::ignored()) {
            let mut buffer = vec![0u8; repr.buffer_len()];
            let mut new_packet = TcpPacket::new_unchecked(&mut buffer);
            repr.emit(&mut new_packet, &src, &dst, &ChecksumCapabilities::ignored());
        }
    }
});
