from ...raw_dump import *
from ..addr import *

# TODO: Handle big pages

# Cf ARM reference manual, page 1282
def va_to_pa(va, pgd):
  r = RawDump.getInstance()
  
  # Split the virtual address into a PD index, PT index and page index
  (pd_i, pt_i, page_i) = ((va >> 20), ((va >> 12) & (1 << 8)-1), (va & (1 << 12) - 1))
  
  # Read the PDE
  pde = r.read_dword(pgd + pd_i*4)
  
  # Page table
  if(pde & 0b11 == 0b01):
    
    # Read the PTE
    pte = r.read_dword(((pde >> 10) << 10) + pt_i*4)
    if(pte & 0b10 != 0b10):
      raise Exception("Error translating VA "+hex(va)+", invalid pte: "+hex(pde))
  
    return ((pte >> 12) << 12) + page_i
      
  # Section / supersection
  elif(pde & 0b11 == 0b10):
    
    supersection = int(pde & 1 << 18)
    
    # Section, cf page 1291
    if(not supersection): 
      return ((pde >> 20) << 20) + (va & (1 << 20) - 1)
      
    # Supersection
    else:
      raise Exception("Error translating VA "+hex(va)+", pde: "+hex(pde) + " is a supersection, not handled yet... Sorry.")
    
  else:
    raise Exception("Error translating VA "+hex(va)+", invalid pde: "+hex(pde))
  