from ...raw_dump import *
from ..addr import *

def va_to_pa(va, pgd):
  r = RawDump.getInstance()
  
  # Split the virtual address into a PD index, PT index and page index
  (pdpt_i, pd_i, pt_i, page_i) = ((va >> 30), ((va >> 21) & (1 << 9)-1), ((va >> 12) & (1 << 9)-1), (va & (1 << 12) - 1))
  
  
  # Read the PDPTE
  pdpte = long(r.read_qword((pgd & 0xFFFFFFE0) + pdpt_i*8))
  if(pdpte & 0b1 != 0b1):
    raise Exception("Error translating VA "+hex(va)+", invalid pdpte: "+hex(pdpte))
  
  
  # Read the PDE
  pde = long(r.read_qword((pdpte & 0xFFFFF000) + pd_i*8))
  if(pde & 0b1 != 0b1):
    raise Exception("Error translating VA "+hex(va)+", invalid pde: "+hex(pde))
    
    
  # 2 Mb page => read bits M-1:21 from PDE
  if(pde & (1 << 7) == (1 << 7)):
    return (pde & 0xFFFFE00000) + (va & (1 << 21) - 1)
    
  # 4 Kb page
  else:
  
    # Read the PTE
    pte = long(r.read_qword((pde & 0xFFFFFFF000) + pt_i*8))
    if(pte & 0b1 != 0b1):
      raise Exception("Error translating VA "+hex(va)+", invalid pte: "+hex(pte))
    
    return (pte & 0xFFFFFFF000) + page_i
    