
import struct 

from .mm.addr import *

class Proxy:
  
  def __init__(self, obj):
    self.__obj = obj
  
  def __getattr__(self, name):
    return getattr(self.__obj, name)      

class String(Proxy):
  pass

class Integer(Proxy):
  pass
  
  
class RawDump:

  instance = None
  
  def __init__(self, file):
    f = open(file, "rb")
    self.mem = f.read()
    f.close()
    RawDump.instance = self
  
  
  @classmethod
  def setFile(cls, file):
    cls(file)
  
  @classmethod  
  def getInstance(cls):
    if cls.instance is None:
      raise Exception(cls.__name__ + " has not been instanciated!")
    return cls.instance
    
  
  @staticmethod
  def little_endian(dword_string):
    return struct.unpack("=L", dword_string)[0]
    
  @staticmethod
  def little_endian_qword(qword_string):
    return struct.unpack("=Q", qword_string)[0]
	
	
  def read_dword(self, addr):
    if isinstance(addr, Address):
      addr = addr.pa()
    try:
      return Integer(RawDump.little_endian(self.mem[addr : addr+4]))
    except Exception as e:
      raise Exception("RawDump: Unable to read physical memory at offset %x" %addr)
    
    
  def read_qword(self, addr):
    if isinstance(addr, Address):
      addr = addr.pa()
    try:
      return Integer(RawDump.little_endian_qword(self.mem[addr : addr+8]))
    except Exception as e:
      raise Exception("RawDump: Unable to read physical memory at offset %x" %addr)
      
    
  def read_string(self, addr, maxlen=100):
    if isinstance(addr, Address):
      addr = addr.pa()
    string = ""
    for i in range(addr, addr + maxlen):
      if self.mem[i] != "\x00":
        string += self.mem[i]
      else:
        break
    return String(string)
    
    
  def read_bytes(self, addr_begin, l):
    # Get physical address
    if isinstance(addr_begin, Address):
      addr_begin = addr_begin.pa()
      
    return self.mem[addr_begin : addr_begin+l]
    
  
