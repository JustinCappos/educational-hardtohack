''' 
   Author: Justin Cappos
 
   Start Date: June 8, 2012

   Purpose: Build a language sandbox that is Turing complete and unhackable

   The goal is to make the instruction set semi-usable (not just a Turing 
   Machine), but as small as possible.


   I'll handle execution like this.   The 'code segment' is 1M of 
   the program.   The 'data segment' has offsets in 1M.   The 'code 
   segment' is unwritable / readable by the program.   

   Each instruction has two parts: the opcode and the argument.   The opcode
   is the first byte and the argument is the next 3 bytes.   I'll write 
   the values as OPCODE ARGUMENT.  For shorthand, (1*4) means 1111, (X*20) 
   means any 20 binary digits, etc.

   The instruction set is the following 6 instructions:

                 
                        SETI
   00000000 (0*16)(X*8)  -> Load the immediate (X) into the register.
                        SUBI
   00000010 (0*16)(X*8)  -> Subtract the immediate (X) from the register.   
                            Underflow results in 00000000.
                        ADDI 
   00000011 (0*16)(X*8)  -> Add the immediate (X) to the register.   Overflow 
                            results in 11111111.
                        STORE
   00001000 (0*4)(X*20)  -> Store the register into position X*20.
                        LOAD
   00001100 (0*4)(X*20)  -> Load position X*20 in memory into the register.
                        BNONZERO
   00010001 (0*4)(X*20)  -> If the register is not 00000000, then jump to 
                            instruction number X*20.   The instruction 
                            X*20 will be executed next (not the one following).

# JAC: I decided to omit this because it isn't needed...
#                        RELJUMP
#   00011000 (0*23)X      -> Relative jump a number of instructions depending 
#                            on the value of register.   If X is 0, go backward.
#                            If X is 1, go forward.   If jumping results in an 
#                            overflow or underflow, then HALT.  A RELJUMP with
#                            a 0 register will result in an infinite loop.
                            


   Any other instruction will be result in the progrm being rejected at load 
   time.

   If execution reaches the end of the instruction segment, the program 
   terminates.   So: SETI 1; BNONZERO 1*20; will halt the program unless
   the final instruction is a BNONZERO.

   In memory, a program is always exactly 257M of memory.   To read in a
   binary, a file is read in.   If it is shorter than 257M, all remaining
   bytes are 0.
'''


# NOTE: I use asserts as my own sanity checks.   They should not be relied
# upon for correctness, so you should be able to remove them all.

# so I can turn on / off debugging easily...
def log(x):
  print x


PROGRAMTORUN = 'program.in'

MAXINSTRUCTION = 2**20   #
INSTRUCTIONSIZE = 4      # instruction size in Bytes
MEMORYITEMS = 2**20       # size of memory (byte addressed)


# we need to parse each instruction before executing it.




def process_instructions(instructions, memory):

  current_instruction_pos = 0
  register = 0

  assert(len(instructions) == MAXINSTRUCTION)
  assert(len(memory) == MEMORYITEMS)
  
  while current_instruction_pos < MAXINSTRUCTION:
    
    thisopcode, thisargument = instructions[current_instruction_pos]
    log(str(current_instruction_pos)+' '+thisopcode+':'+str(thisargument)+' '+str(register))

#                       SETI
#  00000000 (0*16)(X*8)  -> Load the immediate (X) into the register.
    if thisopcode == 'SETI':
      register = thisargument

#                       SUBI
#  00000010 (0*16)(X*8)  -> Subtract the immediate (X) from the register.   
#                           Underflow results in 00000000.

    elif thisopcode == 'SUBI':
      register = register - thisargument
      if register < 0:
        register = 0
    


#                       ADDI 
#  00000011 (0*16)(X*8)  -> Add the immediate (X) to the register.   Overflow 
#                           results in 11111111.

    elif thisopcode == 'ADDI':
      register = register + thisargument
      if register >= 255:
        register = 255

#                       STORE
#  00001000 (0*4)(X*20)  -> Store the register into position X*20.

    elif thisopcode == 'STORE':
      assert(0 <= thisargument < MEMORYITEMS)
      # strings are not mutable...
#      memory[thisargument] = chr(register)

      memory = memory[:thisargument] + chr(register) + memory[thisargument+1:]


#                       LOAD
#  00001100 (0*4)(X*20) -> Load position X*20 in memory into the register.

    elif thisopcode == 'LOAD':
      assert(0 <= thisargument < MEMORYITEMS)
      register = ord(memory[thisargument])

#                       BNONZERO
#  00010001 (0*4)(X*20)  -> If the register is not 00000000, then jump to 
#                           instruction number X*20.   The instruction 
#                           X*20 will be executed next (not the one following).
    elif thisopcode == 'BNONZERO':
      assert(0 <= thisargument < MAXINSTRUCTION)
      if register != 0:
        current_instruction_pos = thisargument
        # I need to make the instruction pointed to the next one (so -1)
        current_instruction_pos = current_instruction_pos - 1

#                       RELJUMP
#  00011000 (0*23)X      -> Relative jump a number of instructions depending 
#                           on the value of register.   If X is 0, go backward.
#                           If X is 1, go forward.   If jumping results in an 
#                           overflow or underflow, then HALT.  A RELJUMP with
#                           a 0 register will result in an infinite loop.
                            
#    elif thisopcode == 'RELJUMP':
#      assert(thisargument == 0 or thisargument == 1)
#
#      # jump back...
#      if thisargument == 0:
#        current_instruction_pos = current_instruction_pos - register
#
#      # or forward...
#      else:
#        current_instruction_pos = current_instruction_pos + register
#
#      # halt if outside of the code...
#      if current_instruction_pos < 0 or current_instruction_pos >= MAXINSTRUCTION:
#        break
#
#      # I need to make the instruction pointed to the next one (so -1)
#      current_instruction_pos = current_instruction_pos - 1



    # unknown opcode!!!
    else:
      print "should be impossible.   You've won!"


    # move the instruction position

    current_instruction_pos = current_instruction_pos + 1



  # we halted!
  log('HALT!')

  return






def parse_binary():
  # I'm going to make a concious decision to allow non-padded files.   This
  # may come back to bite me...
  totalrawdatasize = (MAXINSTRUCTION * INSTRUCTIONSIZE) + MEMORYITEMS

  print 'about to read'
  # Going to read data.   I'm using 'rb' because I don't want translation.
  # Ideally, I'd hand code an I/O routine, but I'm tired...
  filedata = open(PROGRAMTORUN,'rb').read(totalrawdatasize)

  # let's pad this up...
  amountshort = totalrawdatasize - len(filedata)

  print 'about to pad'
  filedata = filedata + '\00'*amountshort


  print 'about to divide'
  # divvy up into instructions and memory...
  instructionblob = filedata[:MAXINSTRUCTION * INSTRUCTIONSIZE]

  assert(len(instructionblob) == INSTRUCTIONSIZE*MAXINSTRUCTION)

  memoryblob = filedata[MAXINSTRUCTION * INSTRUCTIONSIZE:]
  assert(len(memoryblob) == MEMORYITEMS)

  print 'about to parse'

  instructionlist = []
  # let's parse the instructions...
  for instructionpos in range(MAXINSTRUCTION):
    rawinstruction = filedata[instructionpos*INSTRUCTIONSIZE:instructionpos*INSTRUCTIONSIZE+INSTRUCTIONSIZE]
    
    assert(len(rawinstruction) == INSTRUCTIONSIZE)

    rawinstructionarg = ord(rawinstruction[1]) * 2**16 + ord(rawinstruction[2]) * 2**8 + ord(rawinstruction[3])

    opcode = rawinstruction[0]

    opcodenum = ord(opcode)

#                       SETI
#  00000000 (0*16)(X*8)  -> Load the immediate (X) into the register.
    if opcodenum == 0:
      if rawinstructionarg >= 2**8:
        print 'ERROR!   Invalid instruction:',rawinstruction
        log('Invalid SETI instruction:'+rawinstruction)
        return []
        
      instructionlist.append(('SETI',rawinstructionarg))

#                       SUBI
#  00000010 (0*16)(X*8)  -> Subtract the immediate (X) from the register.   
#                           Underflow results in 00000000.

    elif opcodenum == 2:
      if rawinstructionarg >= 2**8:
        print 'ERROR!   Invalid instruction:',rawinstruction
        log('Invalid SUBI instruction:'+rawinstruction)
        return []

      instructionlist.append(('SUBI',rawinstructionarg))

#                       ADDI 
#  00000011 (0*16)(X*8)  -> Add the immediate (X) to the register.   Overflow 
#                           results in 11111111.

    elif opcodenum == 3:
      if rawinstructionarg >= 2**8:
        print 'ERROR!   Invalid instruction:',rawinstruction
        log('Invalid ADDI instruction:'+rawinstruction)
        return []

      instructionlist.append(('ADDI',rawinstructionarg))




#                       STORE
#  00001000 (0*4)(X*20) -> Store the register into position X*20.

    elif opcodenum == 8:
      if rawinstructionarg >= 2**20:
        print 'ERROR!   Invalid instruction:',rawinstruction
        log('Invalid STORE instruction:'+rawinstruction)
        return []


      instructionlist.append(('STORE',rawinstructionarg))


#                       LOAD
#  00001100 (0*4)(X*20)  -> Load position X*20 in memory into the register.
    
    elif opcodenum == 12:
      if rawinstructionarg >= 2**20:
        print 'ERROR!   Invalid instruction:',rawinstruction
        log('Invalid LOAD instruction:'+rawinstruction)
        return []


      instructionlist.append(('LOAD',rawinstructionarg))

#                       BNONZERO
#  00010001 (0*4)(X*20) -> If the register is not 00000000, then jump to 
#                           instruction number X*20.   The instruction 
#                           X*20 will be executed next (not the one following).

    elif opcodenum == 17:
      if rawinstructionarg >= 2**20:
        print 'ERROR!   Invalid instruction:',rawinstruction
        log('Invalid BNONZERO instruction:'+rawinstruction)
        return []


      instructionlist.append(('BNONZERO',rawinstructionarg))


#                       RELJUMP
#  00011000 (0*23)X      -> Relative jump a number of instructions depending 
#                           on the value of register.   If X is 0, go backward.
#                           If X is 1, go forward.   If jumping results in an 
#                           overflow or underflow, then HALT.  A RELJUMP with
#                           a 0 register will result in an infinite loop.

#    elif opcodenum == 24:
#      if rawinstructionarg >= 2:
#        print 'ERROR!   Invalid instruction:',rawinstruction
#        log('Invalid RELJUMP instruction:'+rawinstruction)
#        return []
#
#
#      instructionlist.append(('RELJUMP',rawinstructionarg))



# UNKNOWN OPCODE!!!

    else:
      print 'ERROR!   Invalid instruction:',rawinstruction
      return []

  return instructionlist,memoryblob
    
  

def main():
  # I really don't like doing this.   However, I like importing sys even less.
  result = parse_binary()
  if result:
    instructions = result[0]
    memory = result[1]
    process_instructions(instructions, memory)
  
    for membyte in memory[:10]:
      print ord(membyte),
    print



if __name__ == '__main__':
  main()
