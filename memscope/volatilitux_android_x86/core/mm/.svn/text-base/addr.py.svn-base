
from .kernel import *

class Address:
  
  def __init__(self, addr):
    self.addr = addr
    
  def pa(self):
    return self.addr
    
  def __add__(self, val):
    return self.__class__(self.addr + val)
    
  def __sub__(self, val):
    return self.__class__(self.addr - val)
  
  def __int__(self):
    return self.addr
    
  def __str__(self):
    return self.__class__.__name__ + "(%08x)" % self.addr
    
  def isValid(self):
    return True
  
    
class PhysicalAddress(Address):
  pass
  
  
class VirtualAddress(Address):

  def __init__(self, addr, vmspace=KernelSpace()):
    self.addr = addr
    self.vmspace = vmspace
    self.phys_addr = None     # caching the translation
  
  def pa(self):
    if self.phys_addr is not None:
      return self.phys_addr
    else:
      self.phys_addr = self.vmspace.va_to_pa(self.addr)
      return self.phys_addr
    
  def isValid(self):
    try:
      self.pa()
      return True
    except:
      return False
  

    