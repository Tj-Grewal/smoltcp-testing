
# Conformance Testing

# Conformance Testing: Standards and Interoperability

Within the spectrum of software testing activities, [conformance testing](http://en.wikipedia.org/wiki/Conformance_testing) is an important type of testing intended to assess how well a given software system adheres to requirements set out by a particular software standard.

A key benefit of adherence to software standards is [interoperability](http://en.wikipedia.org/wiki/Interoperability), the ability of different computing systems to work together through established protocols and data formats.

Another important benefit of conformance to standards is _substitutability_: the ability to replace one software system by another.

Conformance testing is a special type of black-box or specification-based testing. However, conformance testing does not deal with a specification developed for the purpose of a single software product, but rather with a broader standard that represents a common basis for many different systems to interoperate.

## Example: The XML Conformance Test Suite

### XML Standards and the W3C

The [World-Wide Web Consortium](http://w3c.org/) is responsible for developing, publishing and maintaining an important collection of standards for the interoperation on the World-Wide Web.

Extensible Markup Language (XML) is a flexible data and document format language that is widely used for information storage and exchange in applications of all kinds. In order to ensure the interoperability of different systems and applications to take advantage of XML technologies, W3C has developed a substantial collection of [XML Standards](http://www.w3.org/standards/xml/).

The [XML Conformance Test Suite](http://www.w3.org/XML/Test/) is a collection of tests designed to assess the conformance of XML parsers to the core specifications of XML 1.0 and 1.1 as well as to the associated specifications of XML Namespaces.

### Test Case Description

In order to automate testing, it is necessary to have a data representation for test cases. In the XML conformance suite, an XML representation of test cases is used. The key components of each test case are:

- The version(s) of the XML spec to which the case applies (1.0 or 1.1)
- The type of the test:
    - `not-wf`: not well-formed; parser must report an error
    - `invalid`: well-formed but not valid; validating parser must report an error
    - `valid`: well-formed and valid; parser must accept
- `SECTIONS`: the reference to the particular requirement being tested.
- `OUTPUT`: canonical output that must be produced, if any.

For example, the following test cases are illustrative.

<TEST TYPE='not-wf' SECTIONS='2.3 [4]'
        ID='o-p04fail3' URI='p04fail3.xml'>
        Name contains invalid character.
</TEST>
<TEST VERSION="1.1" RECOMMENDATION="XML1.1" URI="not-wf/P02/ibm02n03.xml"
        TYPE="not-wf" ID="ibm-1-1-not-wf-P02-ibm02n03.xml" ENTITIES="none" SECTIONS="2.2,4.1">
        This test contains embeded control character 0x3.
</TEST>
<TEST URI="invalid/optional25.xml" ID="optional25" ENTITIES="parameter" SECTIONS="3" TYPE="invalid">
        Tests the Element Valid VC (clause 2) for one
        instance of "children" content model, providing
        text content where one or more elements are
        required.
</TEST>

The [DTD description of test cases](http://parabix.costar.sfu.ca/browser/trunk/QA/xmlconf/testcases.dtd) provides more detail.

Given that the test cases are described in XML and the goal is to test an XML parser, a different XML parser should be used to for automating the tests!

### Error Processing and Security

An important aspect of XML conformance and many other types of conformance is to ensure that processors reject input that is not well-formed. The failure to do so often leads to security vulnerabilities in software systems. From this perspective, full conformance testing of a system against any specification it implements should be considered a necessary part of software system quality assurance.
