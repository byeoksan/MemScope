
from .raw_dump import *


def Field(t):
  """Function to create a Field_class class"""
  
  class Field_class:
    
    def __init__(self, struct):
      self.parent_struct = struct   # container
      self.type = t                 # type of the field
      
      
    def negative_offset(self):
      if(neg_offset):
        return self.offset
      else:
        return 0
        
        
    def get_offset(self):
      return self.offset
      
      
    def reader(self):
      r = RawDump.getInstance()
      
      if self.type == str:
        f = r.read_string
      elif self.type == int:
        f = r.read_dword
      else:
        f = self.type
      return f
    
    
    def checkOffset(self):
      """Check the offset is defined, raise an exeption otherwise."""
      
      try:
        self.offset
      except:
        raise Exception("No offset has been set for Field(%s) in struct %s" % (self.type.__name__, self.parent_struct.__class__.__name__))
    
    
    def read(self):
      """Read the field and return its value (in the appropriate type)"""
      
      self.checkOffset()
      
      # Read the value
      res = self.reader()(self.parent_struct.addr + self.offset)
      
      # Add a reference to the parent field
      res.parent_field = self
      
      return res
      
  return Field_class
  
  
def Pointer(t, neg_offset=False):
  """Function to create a Pointer_class class"""
  
  class Pointer_class(Field(t)):
  
    def negative_offset(self):
      if(neg_offset):
        return self.parent_struct.parent_field.get_offset()
      else:
        return 0
        
    def read_addr(self):
      self.checkOffset()
      return RawDump.getInstance().read_dword(self.parent_struct.addr + self.offset) - self.negative_offset()

    def read(self):
      addr = self.read_addr()
      if(addr == 0):
        return InvalidPointer(addr)
      else:
        addr = VirtualAddress(addr)
        res = self.reader()(addr)
        res.parent_field = self
        return res
  
  return Pointer_class
  
  
  
class InvalidPointer:

  def __init__(self, addr):
    self.addr = addr
    
  def __int__(self):
    return self.addr

  def __str__(self):
    return "%08x" % self.addr
    # return "InvalidPointer(%s)"%self.addr # TODO debug
  
  def __getattr__(self, param):
    self.error(param)
    
  def __getitem__(self, param):
    self.error(param)
    
  def error(self, param):
    raise Exception("Unable to get property '%s' from an InvalidPointer (%s) !" % (property, self.addr))
    
    