from ...raw_dump import *
from ..addr import *

def va_to_pa(va, pgd):
  r = RawDump.getInstance()
  
  # Split the virtual address into a PD index, PT index and page index
  (pd_i, pt_i, page_i) = ((va >> 22), ((va >> 12) & (1 << 10)-1), (va & (1 << 12) - 1))
  
  # Read the PDE
  pde = int(r.read_dword(((pgd >> 12) << 12) + pd_i*4))
  if(pde & 0b1 != 0b1):
    raise Exception("Error translating VA "+hex(va)+", invalid pde: "+hex(pde))
    
  # 4 Mb page
  if(pde & (1 << 7) == (1 << 7)):
    
    return ((pde >> 22) << 22) + (va & (1 << 22) - 1)
    
  # 4 Kb page
  else:
  
    # Read the PTE
    pte = int(r.read_dword(((pde >> 12) << 12) + pt_i*4))
    if(pte & 0b1 != 0b1):
      raise Exception("Error translating VA "+hex(va)+", invalid pte: "+hex(pte))
    
    return ((pte >> 12) << 12) + page_i
    