
from .kernel_struct import *
import mm.user
from .file import *
from .raw_dump import *
from .config import *


class Page:

  SIZE = 0x1000
  
  def __init__(self, virt_addr, size, content=None):
    self.addr = virt_addr
    self.size = size
    self.content = content
  
  def __repr__(self):
    return self.__class__.__name__ + "(addr=0x%08x, size=%d)" % (self.addr, self.size)
    
  def getContent(self):
    return self.content
    
    
class InvalidPage(Page):

  def __init__(self, virt_addr, size):
    Page.__init__(self, virt_addr, size)
    
    
  def getContent(self):
    return chr(0) * self.size
    


@unix_name("vm_area_struct")
class VMArea(KernelStruct):

  # Access flags. See mm.h and fs/proc/task_mmu.c
  flags = [(0x00000001, "r", "-"),
           (0x00000002, "w", "-"),
           (0x00000004, "x", "-"),
           (0x00000080, "s", "p"),
           (0x00000100, " [stack]", "")] # TODO check using start_stack, Cf fs/proc/task_mmu.c, show_map_vma()
  

  @classmethod
  def initclass(cls):
    cls.fields_classes = {"vm_mm": Pointer(mm.user.UserSpace),
                          "vm_start": Field(int), 
                          "vm_end": Field(int), 
                          "vm_file": Pointer(File),
                          "vm_pgoff": Field(int),
                          "vm_next": Pointer(VMArea),
                          "vm_flags": Field(int)}
  
  def contains(self, addr):
    """Return true if the vmarea contains the given addr"""
    return self.vm_start <= addr and addr < self.vm_end
    

  def getFile(self):
    """Return the associated file, or None if there is not"""
    file = self.vm_file
    if isinstance(file, InvalidPointer):
      return None
    else:
      return file
      
      
  def getFlags(self):
    """Get a string representation of the flags"""
    f = self.vm_flags
    s = ""
    for (val, y, n) in self.flags:
      if(f & val):
        s += y
      else:
        s += n
    return s
      
      
  def getNbValidPages(self):
    """Return the number of valid pages"""
    n = 0
    for addr in range(int(self.vm_start), int(self.vm_end), Page.SIZE):
      n += int(VirtualAddress(addr, self.vm_mm).isValid())
    return n
    
  def getNbTotalPages(self):
    """Get the total number of pages"""
    return len(range(int(self.vm_start), int(self.vm_end), Page.SIZE))
    
  
  def getValidPagesRatio(self, num=False):
    """Get the ratio valid pages / total pages"""
    if num:
      return float(self.getNbValidPages()) / self.getNbTotalPages()
    else:
      return "%d/%d" % (self.getNbValidPages(), self.getNbTotalPages())
    
    
  @classmethod
  def getColumns(cls):
    s = "Begin    End       Flags "
    s += "File".ljust(30)
    if(Config.debug):
      s += "Offset".ljust(8)
      s += "Ratio".ljust(8)
    
    return s

    
  def __repr__(self):
    file = self.vm_file
    if isinstance(file, InvalidPointer):
      file = ""
    
    s = "%08x-%08x  %s  " % (self.vm_start, self.vm_end, self.getFlags())
    
    s += ("%s" % file).ljust(30)
    if(Config.debug):
      o = self.vm_pgoff
      if(isinstance(self.vm_file, InvalidPointer)):
        o = ""
      s += str(o).ljust(8)
      s += self.getValidPagesRatio().ljust(8)
    
    return s
    
  def next(self):
    return self.vm_next
    
