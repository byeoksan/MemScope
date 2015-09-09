
from ..kernel_struct import *
from ..vmarea import *

from ..config import *

@unix_name("mm_struct")
class UserSpace(KernelStruct, VMSpace):

  @classmethod
  def initclass(cls):
    cls.fields_classes = {"mmap": Pointer(VMArea), 
                          "pgd": Field(int)}
  
  def __str__(self):
    return "%08x (pgd=%08x)" % (self.addr, self.pgd)
    
    
  def getVMAreas(self):
    """Return the list of all vmareas, sorted by address"""
    vmarea = self.mmap
    l = []
    while not isinstance(vmarea, InvalidPointer):
      l.append(vmarea)
      vmarea = vmarea.next()
    return l
    
  
  def getVMAreasByFileName(self):
    """Return a dict {file1: [vm11, vm12, vm13], file2: [vm21], ... }"""
    vmarea = self.mmap
    d = {}
    
    # Loop over all vmareas
    while not isinstance(vmarea, InvalidPointer):
      f = vmarea.getFile()
      
      # If there is a file
      if f is not None:
        f = str(f)
        
        # Register it
        if not f in d:
          d[f] = []
        d[f].append(vmarea)
      vmarea = vmarea.next()
    
    return d
    
    
  def getVMAreaByAddr(self, addr):
    """Return the vmarea containing the given address, or None if there is not any"""
    vmarea = self.mmap
    while not isinstance(vmarea, InvalidPointer):
      
      if addr >= vmarea.vm_start and addr < vmarea.vm_end:
        return vmarea
      
      vmarea = vmarea.next()
    return None
  
  
  def va(self, addr):
    return VirtualAddress(addr, self)
    
  
  def va_to_pa(self, addr):
    """
    Translate a virtual address
    @param addr a virtual address (provided as an int/long)
    @return physical address (int)
    """
    return Config.arch.va_to_pa(addr, VirtualAddress(self.pgd).pa())
    
    
  def dumpMemory(self, outputFile, start=None, end=None, force=False, skip=False, quiet=False):
    """
    Dump a given memory area in the target process. If start and end are not specified, dump the whole process memory.
    Return the length of the dumped file.
    """
    
    # TODO optimiziation : no need to browse pages that are not within vmareas.
    if start is None or end is None:
      vmareas = self.getVMAreas()
    
      if start is None:
        start = vmareas[0].vm_start
      if end is None:
        end = vmareas[-1].vm_end
    
      if not quiet:
        print "Dumping from %08x to %08x..." % (start, end)
    
    f = open(outputFile, "wb")
    r = RawDump.getInstance()
    
    # Dump each page
    pages = []
    invalid = 0
    pages_total = range(int(start), int(end), Page.SIZE)
    for addr in pages_total:
      
      va = VirtualAddress(addr, self)
      try:
        c = r.read_bytes(va, Page.SIZE)
        pages.append(Page(va, Page.SIZE, c))
      except:
        pages.append(InvalidPage(va, Page.SIZE))
        
        if not quiet:
          print "Warning: Page %08x-%08x is invalid!" % (va, va+Page.SIZE)
          
        invalid += 1
    
    if invalid != 0:
      
      if not quiet:
        print "Warning: The target memory range is incomplete, because %d pages out of %d are not mapped anymore." % (invalid, len(pages_total))
      
      if not force:
        raise Exception("Aborting.")
    
    content = "".join([p.getContent() for p in pages if(not skip or not isinstance(p, InvalidPage))])
    f.write(content)
    f.close()
    
    return len(content)
    
    
  def dumpFile(self, filename, output, force=False, skip=False, quiet=False):
    """Dump the content of a file"""
    
    allvmareas = self.getVMAreasByFileName()
    if not filename in allvmareas:
      raise Exception("Unable to find the specified filename in the target process")
    
    vmareas = allvmareas[filename]
    
    start = vmareas[0].vm_start
    end = vmareas[0].vm_end
    for v in vmareas:
      if start + v.vm_pgoff * Page.SIZE > end:
        end = v.vm_end
    
    if not quiet:
      print "Dumping from %08x to %08x..." % (start, end)
    
    return self.dumpMemory(output, start, end, force, skip, quiet)
    
  
