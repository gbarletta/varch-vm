import traceback
import time

registers = {
  "rv": 15,
  "sf": 14,
  "sp": 13,
  "fl": 12,
  "r15": 15,
  "r14": 14,
  "r13": 13,
  "r12": 12,
  "r11": 11,
  "r10": 10,
  "r9": 9,
  "r8": 8,
  "r7": 7,
  "r6": 6,
  "r5": 5,
  "r4": 4,
  "r3": 3,
  "r2": 2,
  "r1": 1,
  "r0": 0,
}

class Machine:
  pc = 0
  flags = [0] * 16

  def __init__(self, memory_size):
    self.memory = bytearray(memory_size)
    self.registers = [0] * 16
    self.registers[13] = memory_size # set up stack pointer
  
  def load(self, byte_array, offset):
    self.memory[offset:offset + len(byte_array)] = byte_array
  
  def load_file(self, file_path, offset):
    with open(file_path, "rb") as f:
      file_contents = bytearray(f.read())
      self.load(file_contents, offset)

  def dump_memory(self, file_path):
    with open(file_path, "wb") as f:
      f.write(self.memory)

  def get_byte(self, address, incr=True):
    value = self.memory[address]
    if incr:
      self.pc += 1
    return value
  
  def get_short(self, address, incr=True):
    value = (self.memory[address] << 8) | self.memory[address + 1]
    if incr:
      self.pc += 2
    return value
  
  def set_short(self, address, value):
    self.memory[address] = (value >> 8) & 0xFF
    self.memory[address + 1] = value & 0xFF

  opcodes = [
    "push",
    "mov_rp_r",
    "mov_rp_m",
    "mov_rp_c"
    "mov_r_r",
    "mov_r_m",
    "mov_r_c",
    "mov_r_rp",
    "sub_r_r",
    "sub_r_c",
    "add_r_r",
    "add_r_c",
    "cmp",
    "flg",
    "jnz",
    "jmp",
    "call",
    "pop",
    "ret",
  ]
  
  def run_opcode(self, opcode, debug=False):
    print("PC: ", self.pc)
    match opcode:
      case 0: # PUSH
        reg = self.get_byte(self.pc)
        print(reg)
        self.registers[13] -= 2
        self.set_short(self.registers[13], self.registers[reg])
        if debug:
          print(f"PUSH r{reg}: r13/sp={self.registers[reg]}")
      case 1: # MOV [r], r
        regref = self.get_byte(self.pc)
        reg = self.get_byte(self.pc)
        address = self.registers[regref]
        self.set_short(address, self.registers[reg])
        if debug:
          print(f"MOV [r{regref}], r{reg}: [{address}]={self.registers[reg]}")
      case 2: # MOV [r], m
        regref = self.get_byte(self.pc)
        address = self.get_short(self.pc)
        value = self.get_short(address, incr=False)
        address_to = self.registers[regref]
        self.set_short(address_to, value)
        if debug:
          print(f"MOV [r{regref}], [{address}]: [{address_to}]=[{address}] ({value})")
      case 3: # MOV [r], c
        regref = self.get_byte(self.pc)
        value = self.get_short(self.pc)
        self.set_short(self.registers[regref], value)
        if debug:
          print(f"MOV [r{regref}], {value}: [{self.registers[regref]}]={value}")
      case 4: # MOV r, r
        r_to = self.get_byte(self.pc)
        r_from = self.get_byte(self.pc)
        self.registers[r_to] = self.registers[r_from]
        if debug:
          print(f"MOV r{r_to}, r{r_from}: r{r_to}={self.registers[r_from]}")
      case 5: # MOV r, m
        reg = self.get_byte(self.pc)
        address = self.get_short(self.pc)
        value = self.get_short(address, incr=False)
        self.registers[reg] = value
        if debug:
          print(f"MOV r{reg}, [{address}]: r{reg}=[{address}] {value}")
      case 6: # MOV r, c
        reg = self.get_byte(self.pc)
        value = self.get_short(self.pc)
        self.registers[reg] = value
        if debug:
          print(f"MOV r{reg}, {value}: r{reg}={value}")
      case 7: # MOV r, [r]
        reg = self.get_byte(self.pc)
        regref = self.get_byte(self.pc)
        value = self.get_short(self.registers[regref], incr=False)
        self.registers[reg] = value
        if debug:
          print(f"MOV r{reg}, [r{regref}]: r{reg}=[{self.registers[regref]}] {value}")
      case 8: # SUB r, r
        r_to = self.get_byte(self.pc)
        r_from = self.get_byte(self.pc)
        self.registers[r_to] -= self.registers[r_from]
        if debug:
          print(f"SUB r{r_to}, {r_from}: r{r_to}-={self.registers[r_from]}")
      case 9: # SUB r, c
        reg = self.get_byte(self.pc)
        value = self.get_short(self.pc)
        self.registers[reg] -= value
        if debug:
          print(f"SUB r{reg}, {value}: r{reg}-={value}")
      case 10: # ADD r, r
        r_to = self.get_byte(self.pc)
        r_from = self.get_byte(self.pc)
        self.registers[r_to] += self.registers[r_from]
        if debug:
          print(f"ADD r{r_to}, {r_from}: r{r_to}+={self.registers[r_from]}")
      case 11: # ADD r, c
        reg = self.get_byte(self.pc)
        value = self.get_short(self.pc)
        self.registers[reg] += value
        if debug:
          print(f"ADD r{reg}, {value}: r{reg}+={value}")
      case 12: # CMP r, r
        r_1 = self.get_byte(self.pc)
        r_2 = self.get_byte(self.pc)
        ra = self.registers[r_1]
        rb = self.registers[r_2]
        if ra < rb:
          if ra <= rb:
            self.flags[0] = 1
          else:
            self.registers[1] = 1
        if ra > rb:
          if ra >= rb:
            self.flags[2] = 1
          else:
            self.flags[3] = 1
        if ra == rb:
          self.flags[4] = 1
        if debug:
          print(f"CMP r{r_1}, r{r_2}")
      case 13: # FLG
        reg = self.get_byte(self.pc)
        flag = self.get_byte(self.pc)
        self.registers[reg] = self.flags[flag]
        if debug:
          print(f"FLG r{reg}, {flag}: r{reg}={flag} ({self.flags[flag]})")
      case 14: # JNZ
        reg = self.get_byte(self.pc)
        address = self.get_short(self.pc)
        print("JNZ??", self.registers[reg])
        if self.registers[reg] != 0:
          self.pc = address
          print("JUMPED!")
        if debug:
          print(f"JNZ r{reg}, {address}")
      case 15: # JMP
        address = self.get_short(self.pc)
        self.pc = address
        print(f"JMP {address}")
      case 16: # CALL
        address = self.registers[self.get_byte(self.pc)]
        self.registers[11] = self.pc
        self.pc = address
        print(f"CALL {address}: r11/ra={self.registers[11]}, pc={address}")
      case 17: # POP
        reg = self.get_byte(self.pc)
        value = self.get_short(self.registers[13], incr=False)
        self.registers[reg] = value
        self.registers[13] += 2
        if debug:
          print(f"PUSH r{reg}: r13/sp={self.registers[reg]}")
      case 18: # RET
        self.pc = self.registers[11]
        print(f"Returned: {self.registers[15]}")
      case 19: # HLT
        print("HALT!!!!!!")
        self.flags[5] = 0

  def run(self, pc=0, debug=False):
    self.pc = pc
    self.flags[5] = 1
    try:
      while self.flags[5] == 1:
        self.run_opcode(self.get_byte(self.pc), debug)
        time.sleep(0.1)
      print(self.registers)
    except Exception as e:
      print(e)
      print(self.registers)
      print(f"Exception at address {self.pc}")
      traceback.print_exc()
