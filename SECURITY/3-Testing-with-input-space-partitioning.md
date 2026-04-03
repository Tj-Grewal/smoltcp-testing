# What to do:

### Specification of the Program Under Test

Provide a concise specification of the input/output requirements of the program or portion of a program that you are testing, with references to appropriate documents.

### Input Space Partitioning

1. Clearly identify the component you are testing along with all of its inputs, whether from parameters, user input, the environment, etc.
2. Identify the categories for partitioning the input space.
3. Clearly present your partitioned input domain model along with any constraints that are necessary for making it consistent.

You should clearly identify the blocks of choices resulting from your categories and also explain why you added any constraints as a part of your report.

### Test Case Generation

Automate the test-frame and test-case generation as much as possible. You may choose to use a tool such as ACTS provided by the National Institute of Standards and Technology (NIST) for assisting in combinatorial testing, or you may choose to write your own test generation program such as that of the UTF-8 to UTF-16 study.

Once you have generated a plan for which tests to run, create an actual test for each planned _test frame_. You should run these tests on your selected program.

### Test Report and Submission

Using the generated test suite, evaluate the programs under test and report the results. How many tests did you generate? Did you achieve all-pairs or other t-way coverage? How many of these tests were successful/passing?

Your  submission should be well-organized with the following sections.

1. Introduction and identification of the Program Under Test and its specification documents. (You need a well-documented specification from which to derive your input space model).
2. Your Input Space Model
    1. Parameter Environment Categories
    2. Choices or Values in each Category.
    3. Constraints on choice combinations.
3. Method of generating test frames and summary of the results.
4. Method of generating test cases and summary of the results.
5. Results of testing. Bugs found.
6. Observations and Conclusions


# How to do:

# Black-Box Testing: The Category-Partition Method

Test data adequacy criteria let you assess the quality of a test suite. But how do you come up with a good quality test suite in the first place?

_Specification-based test generation_, as a type of _functional testing_ is one general approach.

## Category-Partition Method

The _category-partition method_ is an important practical method that illustrates many concepts of functional testing. This method was first reported by T. J. Ostrand and M. J. Balcer, in their Communications of the ACMarticle "[The category-partition method for specifying and generating functional tests](http://dl.acm.org/citation.cfm?doid=62959.62964)" June 1988, pp. 676-686. The example FIND command specification and test specifications presented below are taken from that article.

For concreteness, consider the definition of a FIND command that searches through an input file looking for occurrences of a search parameter, in accord with the following specification.

|   |   |
|---|---|
|Command|FIND|
|Syntax|FIND <pattern> <file>|
|Function|The FIND command is used to locate one or more instances of a given pattern in a text file. All lines in the file that contain the pattern are written to standard output. A line containing the pattern is written only once, regardless of the number of times the pattern occurs on it.|

The pattern is any sequence of characters whose length does not exceed the maximum length of a line in the file. To include a blank in the pattern, the entire pattern must be enclosed in quotes ("). To include a quotation mark in the pattern, two quotes in a row ("") must be used.

#### Examples

find john myfile

displays lines in the file `myfile` which contain `john``.`

find "john smith" myfile

displays lines in the file `myfile` which contain `john smith``.`

### Determine Parameter and Environment Categories

The first step in the category-partition method is categorize the inputs and environmental conditions to determine the general categories of program input parameters and environment variables.

For the FIND command, the following questions lead to categories that can be chosen relating to the input parameters.

1. How big is the pattern?
2. Is the pattern quoted?
3. Does the pattern contain whitespace (blanks)?
4. Are there any embedded quotes in pattern?
5. Is the filename valid?

Environmental conditions included the characteristics of the data file being searched.

1. Does the pattern occur in the file?
2. Are there multiple occurrences per line?

### Partition each Category into Choices

The next step is to _partition_ each category into separate _choices_. These choices represent different cases that are expected to be handled differently or perhaps may represent error-prone boundary conditions. This gives us our first test specification as follows.

# Unrestricted Test Specification for FIND command
Parameters:
    Pattern size:
        empty
        single character
        many character
        longer than any line in the file

    Quoting:
        pattern is quoted
        pattern is not quoted
        pattern is improperly quoted

    Embedded blanks:
        no embedded blank
        one embedded blank
        several embedded blanks

    Embedded quotes:
        no embedded quotes
        one embedded quote
        several embedded quotes

    Filename:
        good file name
        no file with this name
        omitted

Environments:
    Number of occurrences of pattern in file:
        none
        exactly one
        more than one

    Pattern occurrences on target line:
    # assumes line contains the pattern
        one
        more than one

Given this specification, we can consider combinations of all categories. In all,test frames for the various combinations can be generated.
		4 x 3 x 3 x 3 x 3 x 2 = 1944
Here is an example _test frame_ generated by the process.

Pattern size : many character
Quoting : pattern is quoted
Embedded blanks : several embedded blanks
Embedded quotes : no embedded quotes
File name : good file name
Number of occurrences of pattern in file : more than  one
Pattern occurrences on target line : one

The process of test-frame generation can be entirely automated. Each test frame then represents a work item for a member of the SQA team to write a test case.

In this example, writing 1944 test cases is feasible, although tedious.

But consider a slightly more complex specification:

- 20 categories with 4 choices each.
- 4^20 test cases
- This is (2^40)!
- Or, approximately  (10^12)!
- Combinatorial explosion of test cases!

However, not all combinations make sense. For example, consider the test frame:

Pattern size : empty
Quoting : pattern is quoted
Embedded blanks : several embedded blanks
Embedded quotes : no embedded quotes
File name : good file name
Number of occurrences of pattern in file : none
Pattern occurrences on target line : one

Contradictory!

### Eliminate Contradictions with Properties

We can eliminate many contradictory or otherwise poor cases by adding property annotations to choices. These properties are assertions that may constrain combination with other choices.

# 
Parameters:
    Pattern size:
        empty                                [property Empty]
        single character                     [property NonEmpty]
        many character                       [property NonEmpty]
        longer than any line in the file     [property NonEmpty]

    Quoting:
        pattern is quoted                    [property Quoted]
        pattern is not quoted                [if NonEmpty]
        pattern is improperly quoted         [if NonEmpty]

    Embedded blanks:
        no embedded blank                    [if NonEmpty]
        one embedded blank                   [if NonEmpty and Quoted]
        several embedded blanks              [if NonEmpty and Quoted]

    Embedded quotes:
        no embedded quotes                   [if NonEmpty]
        one embedded quote                   [if NonEmpty]
        several embedded quotes              [if NonEmpty]

    Filename:
        good file name
        no file with this name
        omitted

Environments:
    Number of occurrences of pattern in file:
        none                                 [if NonEmpty]
        exactly one                          [if NonEmpty] [property Match]
        more than one                        [if NonEmpty] [property Match]

    Pattern occurrences on target line:
    # assumes line contains the pattern
        one                                  [if Match]
        more than one                        [if Match]

As a result of these properties, the total number of generated cases reduces to 678.

### Further Reduce Combinations for Error and Single Cases

Some parameter conditions denote errors or conditions that can otherwise be addressed with a single test case. So the number of frames can be further reduced with annotations of these `error` and `single` assertions.

# 
Parameters:
    Pattern size:
        empty                                [property Empty]
        single character                     [property NonEmpty]
        many character                       [property NonEmpty]
        longer than any line in the file     [error]

    Quoting:
        pattern is quoted                    [property Quoted]
        pattern is not quoted                [if NonEmpty]
        pattern is improperly quoted         [error]

    Embedded blanks:
        no embedded blank                    [if NonEmpty]
        one embedded blank                   [if NonEmpty and Quoted]
        several embedded blanks              [if NonEmpty and Quoted]

    Embedded quotes:
        no embedded quotes                   [if NonEmpty]
        one embedded quote                   [if NonEmpty]
        several embedded quotes              [if NonEmpty]

    Filename:
        good file name
        no file with this name               [error]
        omitted                              [error]

Environments:
    Number of occurrences of pattern in file:
        none                                 [if NonEmpty] [single]
        exactly one                          [if NonEmpty] [property Match]
        more than one                        [if NonEmpty] [property Match]

    Pattern occurrences on target line:
    # assumes line contains the pattern
        one                                  [if Match]
        more than one                        [if Match]  [single]

The total number of cases reduces to 125 using these techniques.

### Producing Test Scripts from Test Frames

Given the automatically produced test frames, test scripts can now be written to implement each case.

In some contexts, it may be possible to take automation further, to fully automate test case generation. This would be ideal.

## Controlling Combinatorial Explosion of Test Cases

### All-Pairs Testing

- Rather than test all possible combinations of category choices that satisfy semantic constraints, test cases can be generated such that each pair of choices is tested exactly once.

- Hypothesis: faults in programs generally relate to the incorrect processing of one particular range of parameter values for a single parameter, possibly in the context of logic that is specialized based on one other parameter.

- Provided that the category choices include are appropriately partitioned, all-pairs testing includes a case that covers every potential fault of this kind.
- Example of 20 categories with 4 choices each:
    - (4^20), for all-combination testing.
    -  ((80x76)/2) = 3040, for all-pairs testing.
- Note a pair of choices is unlikely to be properly tested if one of the other parameters reflects an error choice. Therefore, error choices should be excluded from the test cases used for all-pairs testing. This is all-pairs valid case testing.
- Suppose there is one `[error]` or `[single]` choice for each category. We achieve a significant reduction in combinations to cover for all-pairs valid case testing.
    -   ((60x57)/2) + 20 = 1730.
- But we don't have two create a separate test frame for every combination!
- A test frame has one choice each from the 20 categories. A single test frame therefore can cover many pairs.
    -  ((20x19)/2) = 190.
    - By clever choice of test frames can we cover all 1730 pairs with just 10 test frames?

