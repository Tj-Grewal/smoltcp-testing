use smoltcp::iface::{Config, Interface, SocketSet};
use smoltcp::phy::{Loopback, Medium};
use smoltcp::socket::tcp;
use smoltcp::time::Instant;
use smoltcp::wire::{EthernetAddress, IpAddress, IpCidr};
use std::cmp;

const AMOUNT: usize = 128 * 1024 * 1024;
const CHUNK: usize = 4096;

fn main() {
    let device = Loopback::new(Medium::Ethernet);
    let mut device = device;

    let mut config = Config::new(EthernetAddress([0x02, 0x00, 0x00, 0x00, 0x00, 0x01]).into());
    config.random_seed = 0x1234_5678;

    let mut iface = Interface::new(config, &mut device, Instant::now());
    iface.update_ip_addrs(|ip_addrs| {
        ip_addrs
            .push(IpCidr::new(IpAddress::v4(127, 0, 0, 1), 8))
            .unwrap();
    });

    let server_socket = {
        let tcp_rx_buffer = tcp::SocketBuffer::new(vec![0; 65536]);
        let tcp_tx_buffer = tcp::SocketBuffer::new(vec![0; 65536]);
        tcp::Socket::new(tcp_rx_buffer, tcp_tx_buffer)
    };

    let client_socket = {
        let tcp_rx_buffer = tcp::SocketBuffer::new(vec![0; 65536]);
        let tcp_tx_buffer = tcp::SocketBuffer::new(vec![0; 65536]);
        tcp::Socket::new(tcp_rx_buffer, tcp_tx_buffer)
    };

    let mut sockets = SocketSet::new(vec![]);
    let server_handle = sockets.add(server_socket);
    let client_handle = sockets.add(client_socket);

    let start_time = Instant::now();
    let mut did_listen = false;
    let mut did_connect = false;
    let mut sent = 0usize;
    let mut received = 0usize;
    let buffer = [0u8; CHUNK];

    while received < AMOUNT {
        iface.poll(Instant::now(), &mut device, &mut sockets);

        {
            let socket = sockets.get_mut::<tcp::Socket>(server_handle);
            if !socket.is_active() && !socket.is_listening() && !did_listen {
                socket.listen(1234).unwrap();
                did_listen = true;
            }

            while socket.can_recv() {
                let got = socket.recv(|data| (data.len(), data.len())).unwrap();
                received = received.saturating_add(got);
            }
        }

        {
            let socket = sockets.get_mut::<tcp::Socket>(client_handle);
            let cx = iface.context();
            if !socket.is_open() && !did_connect {
                socket
                    .connect(cx, (IpAddress::v4(127, 0, 0, 1), 1234), 65000)
                    .unwrap();
                did_connect = true;
            }

            while socket.can_send() && sent < AMOUNT {
                let remaining = AMOUNT - sent;
                let to_send = cmp::min(remaining, buffer.len());
                let sent_now = socket.send_slice(&buffer[..to_send]).unwrap();
                sent = sent.saturating_add(sent_now);
            }
        }
    }

    let duration = Instant::now() - start_time;
    let seconds = duration.total_millis() as f64 / 1000.0;
    let gbps = (received as f64 * 8.0) / (seconds * 1e9);
    println!("duration_s={:.3} bandwidth_gbps={:.3}", seconds, gbps);
}
