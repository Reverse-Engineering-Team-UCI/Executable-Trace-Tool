# Program-Features-Identifier
Determine the area of code that are associated with specific feature in a program with only the compiled code.

Tools
-----
+   Immunity Debugger 
+   Python 2

Setup
-----
Download our analysis.py script and put it inside the PyCommands folder.

Instruction
-----------
+   Open the executable in Immunity Debugger. 
+   Run "!analysis" inside Immunity Debugger's prompt. After the script ran, stats.txt will be created inside the Immunity Debugger folder. The file will contain all the conditional statements that are hit and the percentage of time that the conditional statements are true and the percentage of time that the conditional statements are false.

Assumptions
-----------
+   The executable is in PE format. 
+   The executable is compiled with GCC. 
