# Executable Trace Tool
The goal of this project is to make the analysis of compiled program easier when the source code is not available. Analyzing compiled program is hard since the source code to assembly is not one-to-one translations. To help with the analysis of compiled program, our team creates a script that runs on Immunity Debugger to record and provide statistics on the conditional statements that are executed. This allows us to find out which conditional statements are executed for a specific program feature. Conditional statements are important part of a program and focusing on it makes it easier for us to figure out how certain program feature is implemented even without the original source. 

This project is supervised under Professor Ian Harris. 

Tools
-----
+   Immunity Debugger 
+   Python 2.x

Setup
-----
Download our analysis.py script and put it inside the PyCommands folder. The PyCommands folder is inside the Immunity Debugger Folder.

Instruction
-----------
+   Open the executable in Immunity Debugger. 
+   Run "!analysis" inside Immunity Debugger's prompt. After the script ran, stats.txt will be created inside the Immunity Debugger folder. The file will contain all the conditional statements that are hit and the percentage of time that the conditional statements are true and the percentage of time that the conditional statements are false.

Assumptions
-----------
+   The executable is in PE format. 
+   The executable is compiled with GCC. 
