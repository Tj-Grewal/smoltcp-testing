use smoltcp::storage::Assembler;
use smoltcp::wire::{Ipv4Packet, TcpPacket, UdpPacket};
use std::fs;
use std::panic;
use std::path::{Path, PathBuf};

fn repo_root() -> PathBuf {
    let dir = Path::new(env!("CARGO_MANIFEST_DIR"));
    dir.parent().unwrap().parent().unwrap().parent().unwrap().to_path_buf()
}

#[test]
fn panic_safety_invalid_inputs() {
    let buffers = vec![
        vec![],
        vec![0u8; 1],
        vec![0u8; 7],
        vec![0u8; 8],
        vec![0u8; 12],
        vec![0u8; 20],
    ];

    for buf in &buffers {
        let udp_ok = panic::catch_unwind(|| {
            let _ = UdpPacket::new_checked(buf.as_slice());
        })
        .is_ok();
        assert!(udp_ok, "UdpPacket panicked on buffer len {}", buf.len());

        let ipv4_ok = panic::catch_unwind(|| {
            let _ = Ipv4Packet::new_checked(buf.as_slice());
        })
        .is_ok();
        assert!(ipv4_ok, "Ipv4Packet panicked on buffer len {}", buf.len());

        let tcp_ok = panic::catch_unwind(|| {
            let _ = TcpPacket::new_checked(buf.as_slice());
        })
        .is_ok();
        assert!(tcp_ok, "TcpPacket panicked on buffer len {}", buf.len());
    }

    let add_ok = panic::catch_unwind(panic::AssertUnwindSafe(|| {
        let mut assembler = Assembler::new();
        let _ = assembler.add(usize::MAX / 4, 0);
        let _ = assembler.add(0, 0);
    }))
    .is_ok();
    assert!(add_ok, "Assembler panicked on boundary sizes");
}

#[test]
fn unsafe_inventory() {
    let root = repo_root();
    let src_dir = root.join("src");
    let mut rows = Vec::new();

    fn visit_dir(dir: &Path, rows: &mut Vec<(String, usize)>) {
        for entry in fs::read_dir(dir).expect("read dir") {
            let entry = entry.expect("dir entry");
            let path = entry.path();
            if path.is_dir() {
                visit_dir(&path, rows);
            } else if path.extension().and_then(|s| s.to_str()) == Some("rs") {
                let text = fs::read_to_string(&path).expect("read file");
                let mut count = 0usize;
                for token in text.split(|c: char| !c.is_alphanumeric() && c != '_') {
                    if token == "unsafe" {
                        count += 1;
                    }
                }
                if count > 0 {
                    let rel = path.strip_prefix(&repo_root()).unwrap();
                    rows.push((rel.to_string_lossy().replace('\\', "/"), count));
                }
            }
        }
    }

    visit_dir(&src_dir, &mut rows);
    rows.sort_by(|a, b| a.0.cmp(&b.0));

    let suite_dir = Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap();
    let out_path = suite_dir.join("unsafe_inventory.csv");
    let mut out = String::from("path,unsafe_count\n");
    for (path, count) in rows {
        out.push_str(&format!("{},{}\n", path, count));
    }
    fs::write(out_path, out).expect("write unsafe inventory");
}
