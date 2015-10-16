# Executable Trace Tool
The goal of this project is to make the analysis of compiled programs easier when the source code is not available. Analyzing compiled programs is hard since the source code to assembly is not a one-to-one translation. To help with the analysis of compiled programs, our team created a script that runs on Immunity Debugger to record and provide statistics on the conditional statements that are executed. This allows us to find out which conditional statements are executed for a specific program feature. Conditional statements are an important part of a program and focusing on it makes it easier for us to figure out how certain program features are implemented even without the original source. 

*supervised under Professor Ian Harris. 

Notes
-----
Within our group, some of us decided to implement finding the jcc(jump conditional code) statements in disassembly differently. The code in this repository first finds and sets breakpoints at all the jcc statements in the binaries, then dynamically checks the boolean values of the conditional statements. On the other hand, their code steps into each instruction in the binaries and if that instruction is a jcc statement, their code will record whether the instruction is true or false. Check out their github repository here: https://github.com/Reverse-Engineering-Team-UCI-diffver/Executable-Trace-Tool.

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
+   Run "!analysis" inside Immunity Debugger's prompt. After the script runs, stats.txt will be created inside the Immunity Debugger folder. The file will contain all the conditional statements that are hit and the percentage of time that they are true and the percentage of time that they are false.

Assumptions
-----------
+   The executable is in PE format. 
+   The executable is compiled with GCC. 
