import immlib

DESC = "CS 199 jump finding function by Derek and Tung"
# **************modify on 2015-07-24 by Yunho Kim, Wonbeom Choi and Sunghyun Hong :: local function calling part ************* 
# **************modify & revise on 2015-07-31 by Yunho Kim :: set all breakpoint at once ******************

# if a process has spaces, capital letters, or is over 8 characters long it needs to be modified
# for example, the process "Hello World.exe" appears as "hello_wo" in the assembly code
def formattedCall(module_name):
    ''' takes Hello_World.exe and returns call hello_wo '''
    module_name = module_name.split(".")[0]
    module_name = module_name.replace(" ", "_")
    if len(module_name) > 8:
        module_name = module_name[0:8]
    module_name = module_name.lower()
    return "call " + module_name
    
def findStartPoint(address):
    imm = immlib.Debugger()
    while(True):
        opcode = imm.disasm(address) # we get the numeric code for the instruction we are currently on (e.g. 2342342)
        opcode_str = opcode.getDisasm()  # we get the string representation of the instruction we are currently on (e.g. jmp esp)
        if(opcode_str[0:3] == "NOP"):
            address += 1
            imm.log("Program start point------------- " + hex(address))
            break
        address -= 1
    return address

def findEndPoint(address):
    imm = immlib.Debugger()
    while(True):
        opcode = imm.disasm(address) 
        opcode_str = opcode.getDisasm()  
        if(opcode_str[0:3] == "NOP"):
            address -= 1
            imm.log("Program end point------------- " + hex(address))
            break
        address += opcode.getOpSize()
    return address


def main(args):
    imm = immlib.Debugger()
##    1.) use module.getEntry() to start at the beginning of the executable
##    2.) iterate through each instruction until we find a function call in the format "call program.00401180". This is the "pre-main"
##    3.) now we will iterate through every line of the "pre-main" until we find cexit. The call to main is always exactlty 7 bytes
##        before the call to cexit, so it is located at the address of cexit - 7
##    4.) jump to main and decrease address until find the startpoint of user code.
##    5.) increase the address and find all branch instruction. if find it, set the breakpoint
##    6.) when address pointed 'NOP', stop searching
    
##      Key Assumptions:
##       
##       the call to main is underneath Immunity's automatic breakpoint
##       the opcode string of the call to main is in the format "call proj4.00401180"
##          (proj4 is less than 8 characters, all of which are lower case. all spaces are replaced with underscores
##       all jump instructions and ONLY jump instructions start with the letter "j". In other words, it has to be x86
##          (I can confirm that in x86, all 32 jump instructions start with the letter "j", and only jump instructions start with the letter "j"
##       cexit is always called at the end of pre-main. (I use cexit to end my loop that goes through main)
##       the call to the program's main is always 7 bytes before the call to cexit in the pre-main

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
            address = address-7 # In GCC (or at least we assume so) the call to main is always 7 bytes above the call to cexit. this is how we find main
            imm.log("The call to main is located at:    " + hex(address))
            last_address = address
            address = int(imm.disasm(address).getDisasm().split(".")[1], 16)
            imm.log("The address of main is located at: " + hex(address))
            break

            
        address += opcode.getOpSize()
        i += 1

    #find the start/end address in entire code
    index = findStartPoint(address)
    endAddress = findEndPoint(index)
    

    #search all branch instruction from start point to end point.
    while(index != endAddress):
        opcode = imm.disasm(index) # we get the numeric code for the instruction we are currently on (e.g. 2342342)
        opcode_str = opcode.getDisasm()  # we get the string representation of the instruction we are currently on (e.g. jmp esp)
        module = imm.findModule(index)[0].lower()
        if opcode_str[0] == "J":
            if opcode_str[0:3] != "JMP":
                imm.setBreakpoint(index)
                imm.log("   " + "%-35s" % opcode_str + "%10s" % module, address=address) #address is the address of the jump
        else:
            None
            #imm.log("%10s" % hex(address).upper() + "   " + "%-35s" % opcode_str + "%10s" % module)
            
        index += opcode.getOpSize()
        i += 1

    
    
    
    return "Search completed!"

