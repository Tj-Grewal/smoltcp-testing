# Presentation Script — smoltcp Quality Assessment & Improvement

**Total estimated time: 12–14 minutes**

---

## Slide 1 — Title (30 seconds)

> Good afternoon everyone. Today we'll be presenting our quality assessment and improvement of smoltcp — an open-source, event-driven TCP/IP stack written in Rust that's designed for embedded and resource-constrained systems. This is our final project for Security Testing and Software Quality Assurance.

---

## Slide 2 — Agenda (30 seconds)

> Here's a quick overview of what we'll cover. We conducted testing across eight quality dimensions — from mutation adequacy and input space partitioning, to security fuzzing, RFC conformance, performance benchmarks, white-box coverage, and software safety analysis. We'll walk through each of these, and then wrap up with our quality dashboard and conclusions.

---

## Slide 3 — Introduction (45 seconds)

> So what exactly is smoltcp? It's a standalone TCP/IP stack written entirely in Rust, designed for bare-metal and embedded systems. One of the key properties of Rust is its memory-safety guarantees — it eliminates entire classes of vulnerabilities like buffer overflows, use-after-free, and double-free bugs at compile time. However, this doesn't mean the code is free from all defects. Logic errors, specification deviations, and performance regressions can still exist, and that's exactly what our assessment investigates. We tested across two platforms — Windows 10 and Ubuntu — to evaluate both correctness and cross-platform portability.

---

## Slide 4 — Scope & Target Modules (45 seconds)

> We focused on the four highest-complexity modules in the codebase. First, `assembler.rs`, which handles TCP segment reassembly. Then `ipv4.rs` for IPv4 header parsing, `udp.rs` for UDP datagram handling, and `tcp.rs` for TCP segment parsing and emission. These modules are critical because they handle untrusted network input directly. Our assessment spans eight quality dimensions listed on the right, and a key strategic decision was developing a custom Python-based mutation engine that generated 333 first-order mutants, giving us empirical validation of test effectiveness.

---

## Slide 5 — Mutation Testing: Operator Distribution (1 minute)

> Let's dive into mutation testing. We applied seven classes of mutation operators to our four target files. As you can see from the chart, constant replacement dominates with 98 mutants, followed by arithmetic with 52 and relational with 48. The less common operators — assignment and shift — produced 27 to 28 mutants each. In total, we generated 333 first-order mutants, where each mutant modifies exactly one source line. For example, one mutant changes a less-than-or-equal operator to strictly less-than in the assembler's boundary check. Each mutant was then tested individually against the module's unit test suite to see if any test could detect the change.

---

## Slide 6 — Mutation Testing: Kill Ratios (1 minute 15 seconds)

> Here are our mutation kill results. The bar chart on the left shows kill ratios per module, and the pie chart on the right shows the overall split. Out of 333 mutants, 229 were killed and 104 survived, giving us an overall kill ratio of 68.77%.

> Looking at the per-module breakdown in the table: `assembler.rs` had the strongest result at 89.41%, reflecting its thorough existing test suite. The wire protocol modules showed lower ratios — `ipv4.rs` at 61%, `udp.rs` at 57.5%, and `tcp.rs` at 63%. These lower ratios tell us that many boundary-condition and bitwise mutations are escaping the current test suite, particularly in the protocol parsing code.

---

## Slide 7 — Equivalent Mutant Analysis (1 minute)

> Now, not all surviving mutants represent genuine test gaps. Some are equivalent mutants — mutations that don't actually change observable behavior. We manually reviewed the top five survivors. Two were classified as equivalent: M0004 mutates a debug-only assertion that doesn't affect release builds, and M0024 alters a formatting-only display branch that doesn't impact protocol logic.

> The remaining three — M0008, M0009, and M0014 — are genuinely killable. They reveal missing boundary-condition tests, specifically around hole sizing and exact-boundary segment assembly in the assembler. After adjusting for the two equivalent mutants, our refined mutation adequacy score comes to 69.18%.

---

## Slide 8 — Input Space Partitioning (1 minute)

> For input space partitioning, we targeted UDP packet parsing in `udp.rs`, focusing on the `new_checked` and `Repr::parse` functions. We derived our input model from RFC 768 and the smoltcp source code, identifying six input dimensions: buffer length, length field value, destination port, checksum mode, IP family, and whether receive checksum checking is enabled. The full combinatorial product gives us 480 test frames.

> The heatmap on the right visualizes which combinations of buffer length and length field result in successful parsing. All 480 test cases matched their expected outcomes on both Windows and Ubuntu — a 100% pass rate. We also ran an additional 216 IPv4 combinatorial test cases, all passing.

---

## Slide 9 — ISP Key Findings (45 seconds)

> The partitioning model revealed clear requirements for successful parsing: the buffer must be at least 8 bytes, the length field must be between 8 and the buffer length, the destination port must be non-zero, and the checksum must be valid or zero when checking is enabled.

> A notable finding is that smoltcp accepts a zero checksum for UDP over IPv6, which is a deviation from RFC 2460 expectations. This was independently confirmed by our conformance test suite, which we'll discuss next.

---

## Slide 10 — Security Fuzzing (1 minute)

> For security fuzzing, we used cargo-fuzz with the LLVM libFuzzer backend, targeting five fuzz harnesses: packet_parser, tcp_headers, dhcp_header, ieee802154_header, and sixlowpan_packet. Each target received 180 seconds of fuzzing.

> The coverage progression chart shows the packet_parser target. Starting from 10 seed corpus files, libFuzzer discovered 759 unique coverage edges across approximately 380,000 executions, exploring TCP option parsing, ICMP message formatting, and UDP display routines.

> The critical result: zero crash artifacts were produced across all five targets on either platform.

---

## Slide 11 — Fuzzing Platform Issue (45 seconds)

> Why zero crashes? This is directly because of Rust's memory-safety guarantees — bounds checking, no null pointer dereferences, and safe integer arithmetic by default. These are exactly the vulnerability classes that fuzzing typically uncovers in C and C++ network stacks, and Rust eliminates them at the language level.

> On the portability side, all fuzzing attempts failed on Windows due to missing runtime DLLs and unresolved sanitizer-coverage symbols. This is a known MSVC/libFuzzer compatibility Issue and represents a significant gap for Windows-based security testing workflows.

---

## Slide 12 — RFC Conformance Testing (1 minute)

> We designed nine conformance test cases against RFC 791 for IPv4 and RFC 768 for UDP. Each test constructs a packet with specific header values and validates whether smoltcp accepts or rejects it.

> Seven of nine cases behaved exactly as expected. However, we identified two specification deviations, highlighted in orange. First, when the IPv4 IHL field encodes a header length smaller than the RFC-mandated minimum of 20 bytes, smoltcp accepts the packet if the buffer is long enough. Second, smoltcp accepts zero-checksum UDP packets over IPv6, which RFC 2460 mandates should be rejected.

---

## Slide 13 — RFC Deviations Details (45 seconds)

> Let's look at these deviations more closely. The permissive IPv4 header length validation appears to be a deliberate design choice for performance in smoltcp. However, it means that crafted packets with invalid header lengths could pass through validation. The UDP/IPv6 zero-checksum acceptance is more concerning from a standards perspective — RFC 2460 mandates non-zero checksums specifically for UDP over IPv6, and accepting zero checksums could allow corrupted datagrams to go undetected on IPv6 networks.

---

## Slide 14 — Performance Testing (45 seconds)

> For performance testing, we developed a custom loopback benchmark that transmits 128 megabytes of data through smoltcp's internal stack using in-memory buffers. We ran five trials on each platform.

> The results show a striking difference: Ubuntu achieved an average throughput of 52.15 gigabits per second, while Windows managed only 17.11 — approximately a 3x performance gap. We used identical in-memory loopback harnesses on both platforms to keep the comparison fair, so this difference reflects genuine platform-level overhead differences.

---

## Slide 15 — White-Box Coverage (45 seconds)

> White-box coverage was measured using cargo-llvm-cov with LLVM's source-based coverage tools. The results show that `assembler.rs` achieved near-complete coverage at 98.28% of regions, reflecting its extensive test suite. The protocol wire modules showed good coverage for parsing paths — over 90% — but lower coverage for emission and error-handling paths. `tcp.rs` had the lowest coverage at 72.58% due to its complexity and many protocol state combinations.

---

## Slide 16 — Enhanced Coverage (30 seconds)

> We also did coverage measurement for the IPv4 combinatorial and microbenchmark test suites, achieving 98.53% and 98.76% region coverage respectively, with only 4 and 2 missed regions. While the remaining gaps are small in absolute terms, they provide a concrete roadmap for targeted future test additions.

---

## Slide 17 — Software Safety (1 minute)

> For software safety, we conducted two analysis experiments. First, panic-safety testing verified that smoltcp's parsing functions handle wrong inputs gracefully — zero-length buffers, truncated headers, and maximum-value fields all returned proper error results rather than panicking. All tests passed on both platforms.

> Second, we performed an unsafe code inventory and found 18 unsafe code occurrences across four files. Critically, all of these are confined to the PHY layer — the platform-specific FFI calls for Berkeley Packet Filter, raw sockets, and TUN/TAP interfaces. Zero unsafe code exists in the core protocol parsing or state machine modules, which is a significant safety property.

---

## Slide 18 — Quality Dashboard (30 seconds)

> This dashboard summarizes all our quality scores. Mutation adequacy at about 70% is the primary area for improvement. All other quality dimensions — input partitioning, fuzzing, conformance, performance, coverage, and safety — achieved 80% or above. The dashboard confirms that smoltcp's core parsing and protocol handling is robust, but the test suite would benefit from additional boundary-condition tests on the wire protocol modules.

---

## Slide 19 — Cross-Platform Portability (30 seconds)

> Regarding cross-platform portability: 8 of our 9 test suites finished successfully on both Windows and Ubuntu. The sole exception was fuzzing, blocked on Windows by the MSVC/libFuzzer incompatibility we discussed. Our performance harness used a custom in-memory loopback to ensure fair cross-platform comparison. These findings underscore the importance of testing across multiple toolchains in real-world deployment scenarios.

---

## Slide 20 — Conclusions (45 seconds)

> To summarize our key takeaways: We achieved a 69.18% adjusted mutation adequacy across 333 mutants, with the assembler module leading at nearly 90%. Our 696 input partition test cases all passed with a 100% rate. Zero crash artifacts from fuzzing confirm Rust's memory safety in practice. We documented two RFC deviations that could be security-relevant in certain deployment contexts. We observed a 3x performance gap between Ubuntu and Windows. And critically, no unsafe code exists in any of the core protocol modules.

> Overall, smoltcp is a well-engineered TCP/IP stack with strong safety properties. The main recommendation is to add boundary-condition tests targeting the wire protocol modules to close the mutation adequacy gap.

---

## Slide 21 — Thank You (15 seconds)

> Thank you for your time!

---