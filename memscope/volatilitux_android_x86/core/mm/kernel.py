
class VMSpace:
  """Main class modeling a virtual memory space"""
  
  def va_to_pa(self, va):
    raise Exception("To be overloaded")


class KernelSpace(VMSpace):
  """All kernel memory is lineraly mapped over PAGE_OFFSET"""
  
  # PAGE_OFFSET
  page_offset = 0xC0000000
  
  
  def va_to_pa(self, va):
    if va == 0:
      return 0
    if(va < KernelSpace.page_offset):
      raise Exception("KernelSpace: Unable to translate virtual address (%x) below PAGE_OFFSET" % va)
    return va - KernelSpace.page_offset
  