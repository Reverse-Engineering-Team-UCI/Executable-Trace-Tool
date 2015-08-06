import immlib
from collections import defaultdict

imm = immlib.Debugger()
 
# if a process has spaces, capital letters, or is over 8 characters long it needs to be modified
# for example, the process "Hello World.exe" appears as "hello_wo" in the assembly code

def getRawData(imm,rawFile):
    '''RawFile will contain addresses of all jcc statements and addresses of where each jcc statement jumps to'''
    while(True): 
        imm.run() #Run the code until a breakpoint is hit
        regs = imm.getRegs()
        if len(regs)==0: #When reach the end, can't read register value anymore
            break
        rawFile.write(str(regs['EIP'])+" ")
        imm.stepOver()
        regs = imm.getRegs() #Get the reg values at the new address
        rawFile.write(str(regs['EIP'])+" ")

def initStatsKey(stats, oldValue):
    '''Value of the address that is added to the stats dictionary is a list. The list needs to be initialized
    so that it contains two int that is zero'''
    stats[oldValue].append(0)
    stats[oldValue].append(0)

def addrBoolValue(processedFile, oldValue, boolean, stats, notLoop, loopAddr):
    '''Write to the processedFile whether a jcc address is True or False'''
    #If the loop is true it jumps away and if the loop is false it goes to the next line
    #Since it is opposite of regular conditional statements, we just flip the boolean value
    if(not(notLoop and oldValue not in loopAddr)):
        if(boolean == "true"):
            boolean = "false"
        else:
            boolean = "true"
    processedFile.write(hex(long(oldValue))+":"+boolean+" ")
    processedFile.write("\n")
    #If this is the first time the address is added to the dictionary
    initStatsKey(stats, oldValue)
    #How many time a conditional statement is true and how many time it is false is stored in a dictionary.
    #Key is the address and the value is a list with two element. The first element is how many times it is
    #true and the second element is how many times it is false. 
    if(boolean == "true"):
        stats[oldValue][0]+=1
    elif(boolean == "false"):
        stats[oldValue][1]+=1
    
def statsForAddr(statsFile, stats, key):
    '''Write to the file the statistic for a particular address'''
    #stats is a dictionary. Key: address. Value: a list with two element. First element contains amount of
    #time it is true. Second element contains amount of time it is false.
    statsFile.write(hex(long(key))) #Address
    statsFile.write("\t\t")
    trueP = str((float(stats[key][0])/(stats[key][0]+stats[key][1]))*100)
    statsFile.write(trueP.split(".")[0]+"."+trueP.split(".")[1][0]) #Percentage of times it is true
    statsFile.write("\t\t")
    falseP = str((float(stats[key][1])/(stats[key][0]+stats[key][1]))*100)
    statsFile.write(falseP.split(".")[0]+"."+falseP.split(".")[1][0])#Percentage of times it is false
    statsFile.write("\n")

def writeStatsHeader(statsFile):
    '''The header for the file statsFile'''
    statsFile.write("Breakpoint Address")
    statsFile.write("\t")
    statsFile.write("Percent True")
    statsFile.write("\t")
    statsFile.write("Percent False")
    statsFile.write("\n")
        
def logJmpsOfFunction(address):
    while(1):
        opcode = imm.disasm(address) # we get the numeric code for the instruction we are currently on (e.g. 2342342)
        opcode_str = opcode.getDisasm()  # we get the string representation of the instruction we are currently on (e.g. jmp esp)
        module = imm.findModule(address)[0].lower()
        if opcode_str[0] == "J":
            if opcode_str[0:3] != "JMP":
                imm.setBreakpoint(address)
                imm.log(" - " + "%-35s" % opcode_str, address=address) #address is the address of the jump
        elif "leave" in opcode_str.lower() or "retn" in opcode_str.lower():
            imm.log(" - exiting function")
            #imm.log("       current address = " + hex(address) + " our call to main address =" + hex(address-7))
            #imm.log("%10s" % hex(address).upper() + "   " + "%-35s" % opcode_str + "%10s" % module)
            break
        # recursively check for functions within this function
        if (formattedCall(module)) in opcode_str.lower():
            function_hex_address = opcode_str.split(".")[1]
            function_address = int(function_hex_address, 16)
            imm.log("function: " + opcode_str + " located at: " + hex(function_address).upper())
            imm.updateLog()
            logJmpsOfFunction(function_address)
        else:
            None
            #imm.log("%10s" % hex(address).upper() + "   " + "%-35s" % opcode_str + "%10s" % module)
        address += opcode.getOpSize()

def formattedCall(module_name):
    ''' takes Hello_World.exe and returns call hello_wo '''
    module_name = module_name.split(".")[0]
    module_name = module_name.replace(" ", "_")
    if len(module_name) > 8:
        module_name = module_name[0:8]
    module_name = module_name.lower()
    return "call " + module_name
    

def usage(imm):
    imm.log("!search <ASM>")
    imm.log("For example: !search pop r32\\npop r32\\nret")

def main(args):
##    1.) use module.getEntry() to start at the beginning of the executable
##    2.) iterate through each instruction until we find a function call in the format "call program.00401180". This is the "pre-main"
##    3.) now we will iterate through every line of the "pre-main" until we find cexit. The call to main is always exactlty 7 bytes
##        before the call to cexit, so it is located at the address of cexit - 7
##    4.) jump to main and iterate though it making breakpoints at each jump until we reach a "leave", which means main has ended.
##        is at.
    
##      Key Assumptions:
##       
##       the call to main is underneath Immunity's automatic breakpoint
##       the opcode string of the call to main is in the format "call proj4.00401180"
##          (proj4 is less than 8 characters, all of which are lower case. all spaces are replaced with underscores
##       all jump instructions and ONLY jump instructions start with the letter "j". In other words, it has to be x86
##          (I can confirm that in x86, all 32 jump instructions start with the letter "j", and only jump instructions start with the letter "j"
##       cexit is always called at the end of pre-main. (I use cexit to end my loop that goes through main)
##       the call to the program's main is always 7 bytes before the call to cexit in the pre-main

    #Initialization
    rawFile = open('data.txt', 'w')
    processedFile = open('result.txt', 'w')
    statsFile = open('stats.txt', 'w')
    tempVal = 0 #Variables for writing to processedFile
    oldValue = ""
    boolean = ""
    notLoop = True
    loopAddr = []
    stats = defaultdict(list)
    # this code block finds the last address in the entire executable. We use it in our while loop to make sure we don't run off the end of the program
    name=imm.getDebuggedName()
    module=imm.getModule(name)
    address=module.getEntry()
    mod_size=module.getCodesize()
    last_address = address+mod_size

    x = 0
    
    imm.log("Starting search for call to main...")
    imm.updateLog()
    while(address < last_address): # we will loop forever (until the end of the executable) until we find the instruction "call X.Y", where X is the name of our process and Y is the address which the call jumps to. (e.g. call proj4.00401180)
                  # If our opcode_string is not a call to pre-main, we increment our current address, which moves us to the next line and continue the loop.
        opcode = imm.disasm(address) # we get the numeric code for the instruction we are currently on (e.g. 2342342)
        opcode_str = opcode.getDisasm().lower() # we get the string representation of the instruction we are currently on (e.g. jmp esp)
        module = imm.findModule(address)[0].lower() # the module name is the name of the process we are debugging (e.g. proj4.exe)
        #imm.log(opcode_str + " in module: " + module, address=address)
        imm.updateLog()

        # check to see if the line we are on is the call to main
        #imm.log(formattedCall(module))
        #imm.log(opcode_str)
        if (formattedCall(module)) in opcode_str: # (i.e. if "call proj4" can be found in our opcode string). Extra explanation of string operations: if module = "proj4.exe" then module.split(".")[0] = "proj4"
            imm.updateLog()
            hex_address = opcode_str.split(".")[1] # hex address is everything to the right of the period
            address = int(hex_address, 16) # the opcode string saves the address in hex, so we need to convert it to decimal to use it
            imm.log(opcode_str + " located at: " + hex(address).upper())
            imm.log("============================================================")
            break
        else:
            address += opcode.getOpSize() #otherwise increment the address by one instruction (we can use getOpSize() to calculate how much incrementing by one instruction actually is)
        x += 1    
            
    i = 0
    
    while(address < last_address):
        opcode = imm.disasm(address) # we get the numeric code for the instruction we are currently on (e.g. 2342342)
        opcode_str = opcode.getDisasm()  # we get the string representation of the instruction we are currently on (e.g. jmp esp)
        module = imm.findModule(address)[0].lower()
        if "cexit" in opcode_str.lower():
            imm.log("Found cexit: ===============================================")
            imm.log("The call to main is located at:    " + hex(address-7))
            address = address-7 # In GCC (or at least we assume so) the call to main is always 7 bytes above the call to cexit. this is how we find main
            address = int(imm.disasm(address).getDisasm().split(".")[1], 16)
            imm.log("The address of main is located at: " + hex(address))
            break

            
        address += opcode.getOpSize()
        i += 1

    # Step 3: starting from main, iterate through instructions, logging it if it is a jump. The loop ends when "cexit is called"


    while(address < last_address):
        opcode = imm.disasm(address) # we get the numeric code for the instruction we are currently on (e.g. 2342342)
        opcode_str = opcode.getDisasm()  # we get the string representation of the instruction we are currently on (e.g. jmp esp)
        module = imm.findModule(address)[0].lower()
        #imm.log("<=> " + opcode_str.lower() + " " + formattedCall(module))
        if (formattedCall(module)) in opcode_str.lower():
            function_hex_address = opcode_str.split(".")[1]
            function_address = int(function_hex_address, 16)
            imm.log("function: " + opcode_str + " located at: " + hex(function_address).upper())
            imm.updateLog()
            logJmpsOfFunction(function_address)
        if opcode_str[0] == "J":
            if opcode_str[0:3] != "JMP":
                imm.setBreakpoint(address)
                imm.log("   " + "%-35s" % opcode_str + "%10s" % module, address=address) #address is the address of the jump
        elif "leave" in opcode_str.lower():
            imm.log("Found leave: ===============================================")
            imm.log("current address = " + hex(address) + " our call to main address =" + hex(address-7))
            imm.log("%10s" % hex(address).upper() + "   " + "%-35s" % opcode_str + "%10s" % module)
            break
        else:
            None
            #imm.log("%10s" % hex(address).upper() + "   " + "%-35s" % opcode_str + "%10s" % module)
            
        address += opcode.getOpSize()
        i += 1
 
    #Finished setting breakpoints. The rest of the code are for automating analysis
    imm.run() #Get to the start of program

    #Populating the rawFile
    getRawData(imm, rawFile)
    rawFile.close()

    rawFile = open('data.txt', 'r')
    #Populating the processedFile
    line = rawFile.read()
    for word in line.split():
        if tempVal%2 == 0: #where I break at
            oldValue = word
        else: #One stepover from where I break at
            if (long(word)-long(oldValue))>5: #branches away. Word is new EIP value and oldValue is the previous EIP value
                boolean = "false"
            elif (long(word)-long(oldValue)<0): #Loops alway jmp backward
                notLoop = False
                boolean = "false"
                loopAddr.append(oldValue)
            else: #Go to next instruction
                boolean = "true"
            #Write to the processedFile whether the jcc address(oldValue) is true or false 
            addrBoolValue(processedFile, oldValue, boolean, stats, notLoop, loopAddr)
        #prepare for the next loop
        notLoop = True
        tempVal+=1
    #Write to the statsFile
    writeStatsHeader(statsFile)
    for key in stats:
        statsForAddr(statsFile, stats, key)
    #Close all files
    rawFile.close()
    processedFile.close()
    statsFile.close()
  
    return "Finished"
