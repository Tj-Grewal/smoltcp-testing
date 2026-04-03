
# Performance Testing and Software Quality

## The Performance Dimension of Software Quality

An important aspect of many software systems is how well they perform. Performance may refer to speed of execution, responsiveness to user input, memory footprint, energy efficiency and/or other resource utilization characteristics.

**But:**

"There is no doubt that the grail of efficiency leads to abuse. Programmers waste enormous amounts of time thinking about, or worrying about, the speed of noncritical parts of their programs, and these attempts at efficiency actually have a strong negative impact when debugging and maintenance are considered. We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil."

Donald E. Knuth, Structured Programming with **`go to`** Statements, Computing Surveys 6(4), December 1974.

## Structured Performance Improvement Engineering

Performance considerations in software system development should first be addressed using high-level approaches.

1. Design system and software architecture for good performance.
2. Choose good data structures and algorithms in critical areas.
3. Use compiler settings and/or optimizing compilers for initial performance improvement.
4. When necessary, profile then optimize source code.

### When Performance Matters

- Performance Improvement
    - Performance improvement is the idea of restructuring software specifically to focus on improvements to performance.
    - start with working software
    - perform performance improvement transformations
    - verify functionality

- Measure First, Optimize Later *
    - Identify the performance-critical 10% of your program.
    - Typically, over 90% of execution time is taken by this performance-critical **Premature optimization is evil.**
        - Low-level coding techniques complicate program structure.
        - Low-level coding techniques are error-prone.

### Test-Driven Performance Improvement

- Test Cases First!
    - cases validate current functionality.
    - Performance improvement steps should continue to pass all tests.
    - New test cases should be written changes testing is inadequate.
    - Test failures: revert the changes and try again.

- Small Steps
    - Performance improvement can be done in multiple small steps.
    - Each step should preserve correctness: pass all tests.

## Computer Architecture and Software Performance

Performance improvement engineering requires a strong knowledge of computer and system architecture. This is particularly true for software deployed on modern multicore processors.

### Branch Mispredictions

- Control structures such as if-statements and while-loops are implemented using conditional branch instructions.
- Depending on some condition (e.g., if-test or while-test), conditional branches _may_ transfer control from one point in an instruction stream to a different instruction address.
- If a conditional branch is not taken, control flows to the next instruction.
- Modern processors typically have a pipeline of 10-25 instructions in different stages of execution.
- When a conditional branch instruction is encountered, a branch _prediction_ is used to identify the next instruction to be loaded into the pipeline.
- Processors use _branch target buffers_ and branch prediction algorithms to improve prediction rates.
- If the predicted branch is not taken, this is a _branch misprediction_.
- Branch mispredictions cause a _pipeline flush_ to clear out the incorrectly loaded instructions.
- The pipeline flush in turn causes a _processor stall_, 10-20 CPU cycles of no useful work while the pipeline reloads.

Consider the following code that attempts to speed things up by avoiding a divison in many cases.

// Optimize z = x/y, given that 50% of the time y = 2.
// In this case,  we can just shift in this case.
if (y == 2) {
  z = x<<1;
}
else {
  z = x/y;
}

With a random pattern of divisor values being equal to 2 about half the time, a 50% branch prediction rate is likely. At 10 cycles per misprediction, this optimization costs 5 cycles to save half of the divisions.

Although division may take several cycles, a design goal of pipelined processors is to achieve an effective throughput of a single cycle per operation. Thus the "optimization" actually _slows down_ performance.

An [detailed example](http://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-an-unsorted-array) shows the effects of 50% branch mispredictions.

### Cache Misses

- Most modern processors use at least 2 levels of cache memory to avoid the cost of always retrieving data from off-chip memory.
- The L1 cache is tightly integrated with the processor and may cost only 2-3 cycles to access.
- L2 cache is generally much larger than L1 but may cost 10-20 cycles to access in the event of a cache miss.
- A miss in the last-level cache may result in a penalty of 100-200 cycles to access main memory

Algorithms which attempt to use large tables of data in memory to save computation costs may be much slower than ones that perform computation (even recomputation) on demand.

Cache memory limitations affect instruction streams as well as data streams. Programs with large memory footprints can have very poor performance due to instruction cache misses.

Cache limitations become more severe in multicore systems, when processors typically share at least the last-level cache.

Interesting [processor cache effects](http://igoro.com/archive/gallery-of-processor-cache-effects/) can show some surprisingly nonintuitive behaviour.

### Short Vector SIMD Parallelism

Modern commodity processors generally include a set of SIMD instructions that operate simultaneously on short vectors of data held in wide registers. SSE on AMD/Intel, Neon on ARM and Altivec on Power PC all use 128-bit wide registers, which can allow four 32-bit operations at a time, eight simultaneous 16-bit operations or sixteen simultaneous single-byte operations.

Intel/AMD AVX and AVX2 instructions now support SIMD parallelism with 256-bit registers.

The [Parabix](http://parabix.costar.sfu.ca/) project takes advantage of SIMD registers for text processing using parallel bit vectors, each having 1-bit per character. Thus SSE registers can be used to process 128 characters at a time.

### Multicore Processors

All major processor families now feature multicore processors, i.e., processor chips with multiple processors on the chip.

Multicore systems can potentially increase throughput by increasing the number of processors being used to solve a particular problem. However, synchronization overheads may limit the effectiveness of multithreaded solutions. Furthermore the speedup that may be achieved is limited to that portion of a program that may be parallelized, in accord with [Amdahl's Law](http://en.wikipedia.org/wiki/Amdahl%27s_law).

## Program Profiling and Performance Measurement

When software system performance is an important issue to overall software quality, systematic profiling and measurement of performance is important to identify system bottlenecks and opportunities for performance improvement.

_Program profiling_ determines a profile of execution time broken down to the level of individual routines, using varous approaches.

- Sampling statistically determines a program profile by periodically sampling program counter locations and reporting the relative frequencies that samples area taken in each of the systems individual routines.
- Event-based approaches, record start and stop timing data triggered by specific events, such as the call to and return from individual functions.
- Instrumentation approaches add specific monitoring and/or measurement statements to the software being evaluated. This may be done through source code addition or by compiler-aided instrumentation.

## Processor Performance Counters

Modern processors have built-in performance counters for directly accessing various aspects of performances. The Linux `perf` tool provides access to these counters. The following `perf list` data shows typical counters available.

  cpu-cycles OR cycles                               [Hardware event]
  stalled-cycles-frontend OR idle-cycles-frontend    [Hardware event]
  stalled-cycles-backend OR idle-cycles-backend      [Hardware event]
  instructions                                       [Hardware event]
  cache-references                                   [Hardware event]
  cache-misses                                       [Hardware event]
  branch-instructions OR branches                    [Hardware event]
  branch-misses                                      [Hardware event]
  bus-cycles                                         [Hardware event]

  cpu-clock                                          [Software event]
  task-clock                                         [Software event]
  page-faults OR faults                              [Software event]
  minor-faults                                       [Software event]
  major-faults                                       [Software event]
  context-switches OR cs                             [Software event]
  cpu-migrations OR migrations                       [Software event]
  alignment-faults                                   [Software event]
  emulation-faults                                   [Software event]

  L1-dcache-loads                                    [Hardware cache event]
  L1-dcache-load-misses                              [Hardware cache event]
  L1-dcache-stores                                   [Hardware cache event]
  L1-dcache-store-misses                             [Hardware cache event]
  L1-dcache-prefetches                               [Hardware cache event]
  L1-dcache-prefetch-misses                          [Hardware cache event]
  L1-icache-loads                                    [Hardware cache event]
  L1-icache-load-misses                              [Hardware cache event]
  L1-icache-prefetches                               [Hardware cache event]
  L1-icache-prefetch-misses                          [Hardware cache event]
  LLC-loads                                          [Hardware cache event]
  LLC-load-misses                                    [Hardware cache event]
  LLC-stores                                         [Hardware cache event]
  LLC-store-misses                                   [Hardware cache event]
  LLC-prefetches                                     [Hardware cache event]
  LLC-prefetch-misses                                [Hardware cache event]
  dTLB-loads                                         [Hardware cache event]
  dTLB-load-misses                                   [Hardware cache event]
  dTLB-stores                                        [Hardware cache event]

## Performance Testing Script

The [perf stat runner](https://cs-git-research.cs.sfu.ca/cameron/parabix-devel/-/blob/master/QA/perf_stat_runner.py) of the Parabix project is an example performance testing tool for evaluating various options with the Parabix tools.

The tool uses the linux `perf` program to pull performance counter information from sample runs of the program under test (PUT).

- Any number of performance parameters and their possible values can be speciried.
- Functional parameters can also be specified.
- The PUT is run with all combinations of performance and functional parameters.
- One run with default performance parameters is used to capture the expected output.
- Each combination is run once to ensure that the application is fully compiled and caches/memory is warmed up.
- Then each combination is run several times under perf stat to collect the performance data.
- The program collects all the data and generates it to a .csv file.

For example, [NFD_perf.py](https://coursys.sfu.ca/2026sp-cmpt-473-e1/pages/NFD_perf.py) is a script for gathering data for the `nfd` application.