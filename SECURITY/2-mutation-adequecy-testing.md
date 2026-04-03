
# What to do:

You should do the following for Mutation adequacy testing: 

Choose three source code file from the project and generate mutations to test the routines within it. Choose a file with complex routines that are likely to have errors.

Generate mutants by applying a small number of mutation operators to the code. You may apply the mutations manually, with a script or with a tool. Document your mutation operators. Each mutant should be identical to the original code except for the application of one mutation operator at one specific location. You should generate at least 300 mutants for testing.

The source code for each routine tested should be submitted, together with a file showing the mutations applied. This could be a "diff" file showing a 3-line unified diff for each mutant created or something similar. This should be a single file with just a few lines for each mutant, not 100 copies!!

Apply the test suite to all mutants. Document the results: how many mutants are killed for each of the chosen routines. Choose 5 mutants that are not killed and try to determine either (a) that it is an equivalent mutant that should not be killed, or (b) how to add a test to kill it.

Calculate the effectiveness of the test suite. Effectiveness should be calculated separately for each routine tested. Overall effectiveness for each file should also be calculated using the ratio of total mutants killed to the total number of non-equivalent mutants created. Discuss your results and your methods, including how you might automate the generation of mutants and/or the application of tests. Focus on interesting observations and lessons learned.


# How to do:

### Fault Seeding and Mutation Adequacy

#### Fault seeding is a technique for evaluating the effectiveness of a testing process.

- One or more faults are deliberately introduced into a code base, without informing the testers.
- The discovery of seeded faults during testing can be used to calibrate the effectiveness of the test process.
- Let S be the total number of seeded faults, and s(t) be the number of seeded faults that have been discovered at time t.
- s(t)/S is the seed-discovery effectiveness of testing to time t.
- If seeded faults are assumed are to be representative of actual faults, then seed-discovery effectiveness can be assumed to be representative of overall testing effectiveness.

#### Sample Problem

- Seed 100 faults into a project at time 0.
- Testing continues to time 30, at which point 73 of the seeded faults have been detected.
- If 219 actual faults were discovered, what is the expected number of total faults prior to seeding?
- How many latent faults are expected to remain in the software at time 30?
- Answer at the bottom of the page.


But be aware of the caution in section 4.2.2 of SWEBOK:"Inserting faults into software involves the obvious risk of leaving them there".
### Mutation Adequacy
Mutation adequacy uses a similar concept to fault seeding to evaluate the effectiveness of a test suite.

- Assume we have a test suite TS with C total test cases c(j).
- Assume that the program under test P passes all the test cases c(j) for 1 <= j <= C.
- Can we stop testing? That is, have we tested P adequately?
- The mutation adequacy criterion provides one answer that we might use.

The mutation adequacy approach differs from fault seeding in that it is applied at a particular point in the testing process and also in that faults are not directly inserted into P.

- Instead, a series of mutants m(i) are created.
- Each mutant m(i) differs from P by the injection of exactly one fault.
- Let M be the total number of mutants m(i).
- The test suite TS is applied to each mutant m(i).
- If a particular mutant m(i) fails any test in c(j), then it is said to be killed.
- All mutants that are not killed are said to remain live at this point.
- The ratio of killed to total mutants (K/M) can be considered a measure of adequacy of TS.

### Automated Mutation: Mutation Operators

- Manually creating mutants is time-consuming.
- A collection of mutants m(i) created from P at some point in time will no longer be representative of P after it has undergone many changes.
- Mutation can be automated by through the concept of mutation operators.
- Mutation operators are simple changes that can be made at various program locations.

#### Some Mutation Operators

Mutation Operator Meaning Original Code Mutated Code
Add 1 Add 1 to a constant q = 0;  q = 1;
Replace Variable  Replace a variable with a different one of the same type  r = x;  r = y;
Replace Operator  Replace an operator with a compatible one q = q + 1 q = q - 1
There are many other kinds of mutation operators.

#### A Program and Three Mutants

Consider the following program P to perform integer division.

  
q = 0;
r = x;
while r >= y {
  r = r - y;
  q = q + 1;
}

Given inputs x and y, P computes the integer division of x divided by y producing quotient q and remainder r.

Applying the mutation operators in the previous table, we can produce the following 3 mutants of P.
  
q = 1;
r = x;
while r >= y {
  r = r - y;
  q = q + 1;
}

q = 0;
r = y;
while r >= y {
  r = r - y;
  q = q + 1;
}

q = 0;
r = x;

while r >= y {
  r = r - y;
  q = q  - 1;
}


### Mutation Theory

#### First-Order and Higher-Order Mutants

A first-order mutant is a mutant produced from the program under test by application of a single mutation operator at a single point in the program.

Higher-order mutants are produced by applying a sequence of mutations to a program.

#### Competent Programmer Hypothesis
- Good programmers tend to write programs that are close to correct.
- Therefore, a program with a single mutation is a good model for a realistic bug.
- Ability to detect mutants with a single mutation is a good model for ability to detect errors made by competent programmers.

#### Coupling Effect
- Complex errors are coupled to simple ones.
- A test suite that is sensitive enough to kill first-order mutants is also likely to kill higher-order mutants.
#### Equivalent Mutants
- Sometimes a mutation to the program under test results in a modified program that produces the same results.
- In this case, the mutant cannot be killed during tested.
- Equivalent mutants should be removed from the mutation adequacy score.
- Mutation adequacy of test suite TS can be determined.
TS= K/(M - E)
- BUT, determining whether a mutant M is equivalent to its program P is difficult.

#### Mutation-Based Test Generation
- After mutant generation and testing, live mutants may remain.
- Once a test suite TS has been evaluated for mutation adequacy, the test suite can be improved by adding new test cases to specifically kill the live mutants.

### Answers

#### Fault Seeding Problem
- The discovered original faults are three times the numbered of discovered seeded faults, so 300 original faults are expected.
- The latent faults are those remaining and not removed: (300 - 219) original faults plus (100 - 73) seeded faults, that is 81 + 27 = 108 latent faults.
  
### Mutation Operators

A systematic mutation testing approach requires that a set of mutation operators be chosen. Mutants are then constructed from the source program by systematically applying the operators to each qualifying instance in the PUT (program under test).

#### FORTRAN: The MOTHRA Operators

The earliest systematic tools for mutation testing were developed for the FORTRAN language. The following 22 mutation operators were defined.

- AAR - array reference for array reference replacement
- ABS - absolute value insertion
- ACR - array reference for constant replacement
- AOR - arithmetic operator replacement
- ASR - array reference for scalar variable replacement
- CAR - constant for array reference replacement
- CNR - comparable array name replacement
- CRP - constant replacement
- CSR - constant for scalar variable replacement
- DER - DO statement end replacement
- DSA - DATA statement alterations
- GLR - GOTO label replacement
- LCR - logical connector replacement
- ROR - relational operator replacement
- RSR - RETURN statement replacement
- SAN - statement analysis
- SAR - scalar variable for array reference replacement
- SCR - scalar for constant replacement
- SDL - statement deletion
- SRC - source constant replacement
- SVR - scalar variable replacement
- UOI - unary operator insertion

#### Language-Based Mutation Operators

As illustrated by the FORTRAN case, mutation operators are often defined with respect to the syntax features of a particular programming language.

#### Too Many Mutants

One of the key challenges of mutation testing is that too many mutants may be produced.

- Cost of compiling each mutant and executing the full test suite against it.
- Cost of analyzing unkilled mutants for equivalence.

#### Reducing The Number of Mutants
- Mutant sampling: choose only a sample (e.g., a random sample) of the mutants for evaluation: even a sample size of 10% can be effective.
- Selective-mutation: apply only the critical subset of operators.
- 5-selective mutation using only the 5 expression modication operators ABS, UOI, LCR, AOR, and ROR has found to be very effective.
- Note that these mutation operators are relatively language independent.


#### Strong vs. Weak Mutation
- Strong mutation: the mutant program must produce different output that fails to pass the test suite in order for it to be considered killed.
- Weak mutation: a mutant may be considered killed if the program state immediately after execution of the mutated operation is detectably different than in the PUT.
- Weak mutation may be computationally less expensive and also lead to a higher kill ratio.

#### Equivalent Mutants
The problem of equivalent mutants is a critical issue for mutation testing.

Recall that the effectiveness of a test suite is determined by TS= K/(M - E), where K is the number of killed mutants and M-E is the number of non-equivalent mutants.

- Determination of whether mutants are equivalent or not often involves a human in the loop as the test oracle, i.e., as the one who makes the decision.
- Human decisions on mutant equivalence are slow and also potentially error-prone.
- But there are automated techniques that can help.
- Trivial compiler equivalence: use the highest optimization modes of a compiler. In this case, many equivalent mutants produce exactly the same object code as the PUT, and are therefore known to be equivalent.
- Recent research has been investigating the use of Large Language Models for automatically identifying equivalent mutants.

Zhao Tian, et al. Large Language Models for Equivalent Mutant Detection: How Far Are We?, ISSTA 2024