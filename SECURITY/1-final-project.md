
## Project Planning and Requirements

#### Project Requirements

Assess and improve the quality of an external open-source project. 

Quality assessment and improvement of the open source project must include the following dimensions.

Quality dimensions include:
- Mutation adequacy evaluation. - 2-mutation-adequecy-testing.md
- Test suite improvement driven by test data adequacy results. - 2-mutation-adequecy-testing.md
- Functional testing using combinatorial methods. - 3-Testing-with-input-space-partitioning.md
- Security analysis and testing. - 4-sqa-fuzzing
- Conformance testing for interoperability with other software. - 5-conformance-testing
- Performance testing - 6-performance-testing
- Test data adequacy evaluation using white-box methods. 
- Software safety.
- Defect correction to remove flaws identified.
- Software refactoring.

Functionality enhancement is not to be a goal of course projects.

### Final Project Write-Ups 

Final project reports write-up must be 4000 words. Figures should be included. Up to 12 figures may be counted towards the word count total at 100 words per figure.

---

## Test Planning

Test plans outline the purpose, environment, resources, schedule and evaluation criteria for testing. They are used to guide testing at various stages in the software life cycle.
### Test Plan Types

Test plans may be of various types.

- Unit test plans may guide the evaluation of individual software modules, typically with a focus on correctness.
- Integration test plans assess whether software modules correctly interact with one another including properly preparing and communicating any necessary data objects.
- System test plans often go beyond assessment of functional correctness to consider load testing, throughput testing, response-time testing, reliability testing and other system factors.
- Acceptance test plans focus on customer requirements and the assessment of the delivered software in a production environment.
- A Master Test Plan is an overall test plan document that includes an outline of the various testing phases, together with reference to their individual test plans.

A test plan is NOT: a long list of test cases.

### Test Objectives

The overall objectives of testing should be introduced as the first part of any test plan.

- Specification of the software to be tested.
- Definition of the functional requirements that software must meet.
- Resource constraints.
- Performance, reliability, conformance and portability requirements.

### Test Environment

Every test plan should describe the anticipated test environment, that is the set of assumptions and resources that are required to exercise the software under test.

### Environmental Factors

Environmental specifications include many different factors.

- Operating systems: Windows, Linux, Mac OS, Solaris, AIX, Android
- Operating system versions: 32-bit vs. 64-bit, Red Hat vs. Ubuntu
- Support software needed: e.g., Java Run-Time Environment, Xerces C++, ...
- Software build environment: compiler, scripting tools
- Processor architecture: e.g., generic x86 32-bit, amd64 with SSSE3, ...
- Hardware requirements: e.g., specific scanners, cameras, ...
- Network requirements: e.g., DNS, HTTP, ...

### Multiple Configurations

In many situations, software systems may need to be supported for multiple configurations. If so, the test plan must address which configurations will be tested.

Applying all test cases to all configurations is often impractical within the limits of available resources. To mitigate this, a test strategy might include elements such as the following.

- A small number of "extreme point" environments may be tested extensively.
- The most common environments may be tested extensively.
- Intermediate environmental combinations may be chosen and tested with only a few tests each.

### Test Deliverables

Test plans must include a list of deliverables as a result of the testing processes.

- Documented test cases: inputs and expected outputs
- Test automation scripts
- Test logs
- Incident reports for failed tests
- Statistical summaries of tests executed, passed, failed.
- Test data adequacy assessments.

