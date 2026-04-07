Feedback to add :

 - add the software configs from the test env from plan - and hardware part. 
- portability issue - fuzzing only works on linux - windows no fuzz

-

---

1. Introduction:

Remove the last part of the paragraph. 

2. MAT:

remove all the file names? 
remove murate_and_test.py

Say something about the different types of mutations applied - distribution of the mutations. Just a simple point. 

2.3:

Is this graph jank? 
Should be a checkmark or a bulleted list instead. Or have some details about the mutant analysis. 

WHat is top 5? What criteria makes it top 5. 

MAYBE add a table to show what M0020, M0009 etc is. 

---


3. 

- remove the file reference. no csv file. 
instead say this:
"They were logged and evaluated as follows:"

Input space partition graph doesn't make sense? 

- reinforce the notable finding and mention how it affects the conformance. 

4. 

60 + 180 = 240 not 300 

Original time was 60 - but the script ran too long and quit before full test was done. So it upped to 180 for tests and got correct results. 

Address the run statement - with 60 max

---

4.2

Remove the mention to log entries since the TA doesnt have the file. 

Leave the part in about shitting on C++

4.3 portability 

Leave it in - remove the fuzzing windows.log part. 


5. 

What is IHL - ? Internet Header Length?

Leave the points in for 1 and 2. 
Change it over from plot to a table instead? SO the name is bigger 


6. 

Remove the loopback_suite part. 

How can you reword the examples/loopback part is. How can you word it to sound better without the example or tuntapinterface part. 

less claimy - don't add extra details. 

Remove 6.2 completely. - WSL 


7.

Explain more about what the 4 and 2 missed regions are. 

What are the regions not covered? Why is the plot here?

8.

9.

Remove the part about "This defect was already present..."

Should we remove 9 all together?

Also make a note of what has been removed up top - how many dimensions. 

---

10.

Make the graph into a table instead. 

Should be a table so that's it's easily readable. 

Remove the graph completely. Figure 12.

11.

Also remove the part about section 9 from this image. 

12.

MUTATION ADEQUCY SCORE NOT CONSISTENT - 

69.18 and 69.67. 

Confirm the 300+ second run

WSL -> say linux instead 

Last bullet point - talk about whitebox coverage or something else.

Remove recommendations completely. 

