# What to do:

You will seek to identify flaws in software that could potentially be exploited to compromise the security of systems depending on the software.

This will involve two phases.

1. Generating "erroneous input" test cases that expose potential security issues through fuzz testing.
2. Using sanitizers to detect specific types of faults in software systems that may cause failures in response to erroneous input.

## Requirements

1. Use a fuzzing tool such as FuzzTest, zzuf, AFL++ or libFuzzer, etc., to perform fuzz testing of your chosen project, seeking to find input cases that cause program crashes.
2. Use sanitizers or other dynamic or static analysis tools to identify the specific program error that caused the crash, that is both the type of the error and the source code lines responsible.
3. Find and document at least 6 distinct errors in your chosen software. Fixing the bugs is not a requirement, but clearly documenting the cause of the failure is required.


# How to do:


# Security: A Fundamental Quality Characteristic

The distinction between the reliability and security aspects of computer systems often boils down to how the systems respectively handle _correct_ and _incorrect_ inputs.

- Correct processing of _correct_ inputs is fundamental to the reliability of the software in carrying out its intended purpose.
- Correct processing of _incorrect_ inputs is fundamental to the security of software in preventing unauthorized access or modification of data or compromise of computing systems.

## CIA Model: Confidentiality, Integrity, Availability

- Confidentiality: information is only disclosed to those _authorized_ to know it.
- Integrity: information may only be modified in _allowed ways_ by _authorized_ users.
- Availability: those authorized for access are not prevented from it.

Software bugs can lead to policy violations.

- Information leaks (C)
- Data corruption (I)
- Denial of service attacks (A)
- Remote takeover (CIA)

## Security Issues in Modern Systems

The [Common Weakness Enumeration](http://cwe.mitre.org/) is a joint MITRE/SANS project to identify, classify and document the common security weaknesses of modern computing systems together with recommended best practices to address these weaknesses. Overall the weaknesses are grouped into three broad classes.

- _Insecure interaction between components_. These weaknesses relate to flaws in how networked components interact with each other, potentially allowing malicious agents to compromise systems.
- _Unsafe resource management_. These weaknesses relate to failures to correctly manage and limit access to system resources.
- _Compromised defenses_. These weaknesses relate to failures to follow best practices in the very security measures that are intended to defend systems from outside threats.

### Insecure Interaction Between Components

The following weaknesses are specific types of insecure interaction.

1. _SQL Injection_ [CWE-89](http://cwe.mitre.org/data/definitions/89.html). This weakness relates to the inclusion of user or external input into the formation of an SQL command.  
    [Examples](http://cwe.mitre.org/data/definitions/89.html#Demonstrative_Examples).
2. _OS Command Injection_ [CWE-78](http://cwe.mitre.org/data/definitions/78.html). Like SQL injection, this weakness again relates to insecure use of user or external input, this time in the context of creating an operating system command.  
    [Examples](http://cwe.mitre.org/data/definitions/78.html#Demonstrative_Examples).
3. _Cross-Site Scripting_ [CWE-79](http://cwe.mitre.org/data/definitions/79.html). User or external input to scripts on one site may generate web pages that can compromise another site.  
    [Examples](http://cwe.mitre.org/data/definitions/79.html#Demonstrative_Examples). [Wikipedia](https://en.wikipedia.org/wiki/Cross-site_scripting).
4. _Unrestricted File Upload_ [CWE-434](http://cwe.mitre.org/data/definitions/434.html).  
    [Examples](http://cwe.mitre.org/data/definitions/434.html#Demonstrative_Examples).
5. _Cross-Site Request Forgery_ [CWE-352](http://cwe.mitre.org/data/definitions/352.html).  
    [Examples](http://cwe.mitre.org/data/definitions/352.html#Demonstrative_Examples).
6. _Open Redirect_ [CWE-601](http://cwe.mitre.org/data/definitions/601.html).  
    [Examples](http://cwe.mitre.org/data/definitions/601.html#Demonstrative_Examples).

### Unsafe Resource Management

The following weaknesses represent failures to safely manage resources.

1. _Buffer Overflow_ [CWE-120](http://cwe.mitre.org/data/definitions/120.html). If the size of input strings is not checked before copying, data may be copied beyond reserved buffer areas.  
    [Examples](http://cwe.mitre.org/data/definitions/120.html#Demonstrative_Examples).
2. _Path Traversal_ [CWE-22](http://cwe.mitre.org/data/definitions/22.html). User or external paths with "../" sequences may allow access to restricted directories.  
    [Examples](http://cwe.mitre.org/data/definitions/22.html#Demonstrative_Examples).
3. _Code Download_ [CWE-494](http://cwe.mitre.org/data/definitions/494.html).  
    [Examples](http://cwe.mitre.org/data/definitions/494.html#Demonstrative_Examples).
4. _Untrusted Code_ [CWE-829](http://cwe.mitre.org/data/definitions/829.html9).  
    [Examples](http://cwe.mitre.org/data/definitions/829.html#Demonstrative_Examples).
5. _Unsafe Library Functions_ [CWE-676](http://cwe.mitre.org/data/definitions/676.html).  
    [Examples](http://cwe.mitre.org/data/definitions/676.html#Demonstrative_Examples).
6. _Incorrect Buffer Size Calculation_ [CWE-131](http://cwe.mitre.org/data/definitions/131.html).  
    [Examples](http://cwe.mitre.org/data/definitions/131.html#Demonstrative_Examples).
7. _Uncontrolled Format String_ [CWE-134](http://cwe.mitre.org/data/definitions/134.html).  
    [Examples](http://cwe.mitre.org/data/definitions/134.html#Demonstrative_Examples).
8. _Integer Overflow or Wraparound_ [CWE-190](http://cwe.mitre.org/data/definitions/190.html).  
    [Examples](http://cwe.mitre.org/data/definitions/190.html#Demonstrative_Examples).

### Compromised Defenses

The following weaknesses represent failures in the defences used to secure systems.

1. _Missing Authentication for Critical Function_ [CWE-306](http://cwe.mitre.org/data/definitions/306.html).  
    [Examples](http://cwe.mitre.org/data/definitions/306.html#Demonstrative_Examples).
2. _Missing Authorization_ [CWE-862](http://cwe.mitre.org/data/definitions/862.html).  
    [Examples](http://cwe.mitre.org/data/definitions/862.html#Demonstrative_Examples).
3. _Use of Hard-coded Credentials_ [CWE-798](http://cwe.mitre.org/data/definitions/798.html).  
    [Examples](http://cwe.mitre.org/data/definitions/798.html#Demonstrative_Examples).
4. _Missing Encryption of Sensitive Data_ [CWE-311](http://cwe.mitre.org/data/definitions/311.html).  
    [Examples](http://cwe.mitre.org/data/definitions/311.html#Demonstrative_Examples).
5. _Reliance on Untrusted Inputs in a Security Decision_ [CWE-807](http://cwe.mitre.org/data/definitions/807).  
    [Examples](http://cwe.mitre.org/data/definitions/807.html#Demonstrative_Examples).
6. _Execution with Unnecessary Privileges_ [CWE-250](http://cwe.mitre.org/data/definitions/250.html).  
    [Examples](http://cwe.mitre.org/data/definitions/250.html#Demonstrative_Examples).
7. _Incorrect Authorization_ [CWE-863](http://cwe.mitre.org/data/definitions/863.html).  
    [Examples](http://cwe.mitre.org/data/definitions/863.html#Demonstrative_Examples).
8. _Incorrect Permission Assignment for Critical Resource_ [CWE-732](http://cwe.mitre.org/data/definitions/732.html).  
    [Examples](http://cwe.mitre.org/data/definitions/732.html#Demonstrative_Examples).
9. _Use of a Broken or Risky Cryptographic Algorithm_ [CWE-327](http://cwe.mitre.org/data/definitions/327.html).  
    [Examples](http://cwe.mitre.org/data/definitions/327.html#Demonstrative_Examples).
10. _Improper Restriction of Excessive Authentication Attempts_ [CWE-307](http://cwe.mitre.org/data/definitions/307.html).  
    [Examples](http://cwe.mitre.org/data/definitions/307.html#Demonstrative_Examples).
11. _Use of a One-Way Hash without a Salt_ [CWE-759](http://cwe.mitre.org/data/definitions/759.html).  
    [Examples](http://cwe.mitre.org/data/definitions/759.html#Demonstrative_Examples).

## Security Practices

### Mitigating the Top 25 Weaknesses

To address the security weaknesses represented by its top 25 list, the CWE site also offers a list of its top 9 mitigations, the [monster mitigations](http://cwe.mitre.org/top25/mitigations.html).

- M1 Establish and maintain control over all of your inputs.
- M2 Establish and maintain control over all of your outputs.
- M3 Lock down your environment.
- M4 Assume that external components can be subverted, and your code can be read by anyone.
- M5 Use industry-accepted security features instead of inventing your own.
- GP1 (general) Use libraries and frameworks that make it easier to avoid introducing weaknesses.
- GP2 (general) Integrate security into the entire software development lifecycle.
- GP3 (general) Use a broad mix of methods to comprehensively find and prevent weaknesses.
- GP4 (general) Allow locked-down clients to interact with your software.

### Default Deny: Whitelists instead of blacklists

- Whitelists identify explicitly resources that are permitted access, while blacklists identify resources that are denied access.
- Blacklist approaches can be used to counter known threats as they arise; simply deny service to the address associated with the threat.
- But blacklist approaches are inherently _reactive_: providing security against a threat only after it is known to exist and has been identified.
- Whitelists provide much greater security through a policy of _default deny_: only allow access to known resources.

### Secure Coding Practices

The Software Engineering Institute at Carnegie Mellon University has a series of secure coding standards that address specific known problems in particular programming languages as well as general security recommendations.

#### Secure Coding Practices

The [CERT Top 10 Secure Coding Practices](https://www.securecoding.cert.org/confluence/display/seccode/Top+10+Secure+Coding+Practices) represent best practices for building security into software systems by design.


---


# Fuzz Testing and Sanitizers for Security and Hardening

## Fuzz Testing

Fuzz testing is the practice of testing software by bombarding it with randomly generated inputs.

### Security Goal

- Systematically test software for security vulnerabilities.
- Identify cases where software crashes or operates incorrectly for incorrect or out-of-bounds inputs.
    - Make sure that the software does not suffer security failures:
        - Confidentiality - inappropriate access to data.
        - Integrity - corruption of data
        - Availability - crashes leading to denial of service
    - These failures may be triggered by many kinds of defects.
        - buffer overflows
        - division by zero
        - null pointer dereference
        - failure to terminate (infinite recursion)
        - uninitialized memory

## Creating Fuzz

- Entirely random input to programs may catch vulnerabilities that lead to crashes.
- But restricted inputs may be more helpful.

### Model-Based Generation

- In this case, inputs are based on some form of _model_ of the input domain.
- For example, grammars can be used to generate random strings of the language described by the grammar.
- Frameworks may provide simple tools to construct models.
    - [Simple Models with Google FuzzTest](https://github.com/google/fuzztest/blob/main/doc/overview.md)

### Mutation-Based Fuzzing

- Another way of generating inputs for fuzzing is to _mutate_ inputs already used in a test suite.
    - Small random changes are made to inputs, e.g. bit flipping, appending data, deleting data.

### Coverage-Guided Fuzzing

- A variant of mutation-based fuzzing is to include a white-box source code coverage tools.
- Mutated inputs are then investigated to identify new code paths and potentially locate faults for poorly tested paths.
- [AFL++](https://github.com/AFLplusplus/AFLplusplus)
- [LibFuzzer](http://llvm.org/docs/LibFuzzer.html)

## Oracles

- Random inputs are very useful for finding security vulnerabilities due to crashes.
- But if normal looking output is produced, how do you check for correctness?
- That is, how do you created oracles for the randomly generated test cases.

### Equivalent Functions

- One way to create oracles for randomly generate input is to rely on _equivalent implementations_.
    - For example, a high-performance implementation of a given function could be accompanied with a reference implementation that computes the same result.
    - Different language-based implementations may be used, for example a Python implementation may be used as an oracle for a C++ function.

### Round-Trip Functions

- Some systems have complementary functions that are inverses of each other.
- For example: encoders and decoders for compression.
- Checking the encoder output of a randomly generated output may be done by confirming that the decoder can take this input and regenerate the random input.

### Property-Based Systems

- In this case, we may define oracles that just check that certain observed properties of the output are correct.
- For example, one property could be the assertion that the output is a simple numeric value.
- For security vulnerabilities, another property is that the program does not crash.
- For denial-of-service vulnerabilities, ensuring that the output is produced within a given time period may suffice.

- [Hypthosis Property-Based Testing for Python](https://hypothesis.readthedocs.io/en/latest/)

## Sanitizers

- Sanitizers are code instrumentation tools that help identify faults due to resource management issues in software.
- Sanitizers are often provided as options to compilers such as Clang.
- [Address Sanitizer (Clang )](http://clang.llvm.org/docs/AddressSanitizer.html)
- [Thread Sanitizer (Clang )](http://clang.llvm.org/docs/ThreadSanitizer.html)
- [Memory Sanitizer (Clang)](http://clang.llvm.org/docs/MemorySanitizer.html)

### Sanitizers with Fuzzing

- It may be particularly useful to incorporate sanitizers when performing fuzz testing.
- Once an input that crashes a program has been identified, a sanitizer may help pin down the exact bug.

## Hardening

- [Control Flow Integrity](http://clang.llvm.org/docs/ControlFlowIntegrity.html)
- [SafeStack](http://clang.llvm.org/docs/SafeStack.html)


