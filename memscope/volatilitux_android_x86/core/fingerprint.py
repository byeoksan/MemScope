
from .config import *

import sys
import re
import os

# Starting virtual address of the kernel
PAGE_OFFSET = 0xC0000000

# Hardcoded offsets for structures that never change in the Linux kernel
'''
HARDCODED_OFFSETS = {
  "vm_area_struct": {
    "vm_mm": 0,
    "vm_start": 4,
    "vm_end": 8,
    # vm_file and vm_pgoff are unstable, they are detected at runtime
    "vm_next": 12,
    "vm_flags": 20
  },


  "qstr" : {
    "name": 8
  }
}
'''

HARDCODED_OFFSETS = {
  "vm_area_struct": {
    # "vm_mm": 32,
    "vm_start": 0,
    "vm_end": 4,
    # vm_file and vm_pgoff are unstable, they are detected at runtime
    "vm_next": 8,
    "vm_flags":40,
  },


  "qstr" : {
    "name": 8
  }
}

class Fingerprint:
  
  MAX_TASK_SIZE = 2048
  MAX_VM_AREA_SIZE = 128
  MAX_VM_FILE_SIZE = 128 # Not true but the flags we are looking for are at the beginning of the struct
  
  def __init__(self, dumpfile, debug_enabled=False):
    self.dumpfile = dumpfile
    self.debug_enabled = debug_enabled
    self.r = RawDump.getInstance()
    
    self.context = {}
    self.offsets = {}
    self.init_task = None
    self.arch_name = None
    
    # First step: find the first task_structs using their names and compute basic deltas
    res = self.find_swapper_init()
    
    # Second step: find the start of all task_structs, and compute some field offsets
    if(res):
      res &= self.find_task_struct_starts()
    
    # Third step: find additional fields (pid, mm and mmap)
    if(res):
      res &= self.find_pid_mm()
    
    # Fourth step: determine file-related offsets (vm_file, f_dentry, f_name)
    if(res):
      res &= self.find_file_offsets()
    
    
    # Fifth step: find the pgd offset and the architecture
    if(res):
      res &= self.find_pgd_arch()
    
    
    # Final step: prepare self.offsets, self.init_task and self.arch_name
    if(res):
      res &= self.finalize()
    
    self.valid = res
    
    
    
  def debug(self, msg):
    if(self.debug_enabled):
      print msg
      
      
  def read_int(self, addr):
    return int(self.r.read_dword(addr))
    
  def read_va(self, addr):
    return self.read_int(addr) - PAGE_OFFSET
      
      
  def find_swapper_init(self):
    """
    First fingerprinting step: Find the first 2 task_structs (swapper and init)
    Cf http://lxr.linux.no/#linux+v2.6.36/include/linux/init_task.h#L109
    """
    
    for res in re.finditer("swapper", self.r.mem):
      swapper_comm_addr = res.start()
      name = self.r.read_string(swapper_comm_addr)
    
      self.debug("swapper comm found at %08x" % swapper_comm_addr)
      
      # Try to locate the 'tasks' linked list
      for delta_comm_tasks in range(-self.MAX_TASK_SIZE/2, self.MAX_TASK_SIZE):
        swapper_tasks_addr = swapper_comm_addr + delta_comm_tasks
        
        # Go to the next task_struct (supposed to be init's 'tasks' field)
        init_tasks_addr = self.read_va(swapper_tasks_addr) # TODO optimize ; check that it is > 0
        
        # Find init (pid = 1)
        for res in re.finditer("init", self.r.mem[init_tasks_addr : init_tasks_addr+self.MAX_TASK_SIZE]):
          
          # Check the delta between the found name and the task field; it should be the same as swapper
          if(res.start() == -delta_comm_tasks):
            init_comm_addr = init_tasks_addr+res.start()
            self.debug("init comm found at %08x" % (init_tasks_addr))
            
            # Confirm with init's prev, supposed to be swapper's 'tasks' field
            swapper2_addr = self.read_va(init_tasks_addr+4)
            swapper2_comm_addr = swapper2_addr-delta_comm_tasks
            if(self.r.mem[swapper2_comm_addr:swapper2_comm_addr+7] == "swapper"):
              self.debug("confirmed: swapper comm found with init's prev")
            
              # Save everything
              self.context["delta_comm_tasks"] = delta_comm_tasks
              self.context["swapper_comm_addr"] = swapper_comm_addr
              self.context["swapper_tasks_addr"] = swapper_tasks_addr
              self.context["init_comm_addr"] = init_comm_addr
              self.context["init_tasks_addr"] = init_tasks_addr
                
              return True
      
    return False
    
    
  def find_task_struct_starts(self):
    """
    Second fingerprinting step: Find the parent field, use it to find the start of task_struct and deduce the offsets of all previous fields.
    Cf http://lxr.linux.no/#linux+v2.6.36/include/linux/init_task.h#L109
    """
  
    # Rename context
    c = self.context
    
    # dict( delta_comm_parent => (swapper_addr, tasks) )
    candidates = {}
    
    # Find the beginning of all task_structs using init's parent field
    for delta_comm_parent in range(-self.MAX_TASK_SIZE/2, self.MAX_TASK_SIZE/2):
    
      # Get swapper's and init's parents, supposed to be swapper itself
      swapper_parent = self.read_va(c['swapper_comm_addr']+delta_comm_parent)
      init_parent = self.read_va(c['init_comm_addr']+delta_comm_parent)
      
      # Check if both are equal and inside the range (basic pruning condition)
      if(swapper_parent == init_parent
         and swapper_parent > c["swapper_comm_addr"]-self.MAX_TASK_SIZE/2 
         and swapper_parent < c["swapper_comm_addr"]+self.MAX_TASK_SIZE/2):
        
        # Compute temporary offsets
        swapper_addr = swapper_parent
        offset_comm = c['swapper_comm_addr'] - swapper_addr
        offset_tasks = c['swapper_tasks_addr'] - swapper_addr
        offset_parent = c['swapper_comm_addr']+delta_comm_parent - swapper_addr
        init_addr = c['init_comm_addr'] - offset_comm
    
    
        # Find all task_structs
        tasks = [("swapper", swapper_addr),
                 ("init", init_addr),
                ]
        task_addr = init_addr
        end = False
        error = False
        while not end and not error: # For each task_struct starting with init
        
          # Go to the next one
          task_addr = self.read_va(task_addr+offset_tasks) - offset_tasks
          name = self.r.read_string(task_addr+offset_comm)
          
          # Check if the parent is already in the list
          parent = self.read_va(task_addr+offset_parent)
          if(parent in dict(tasks).values()):
          
            # Have we reached the end?
            if(name.startswith("swapper")):
              end = True
            else:
              tasks.append((name, task_addr))
          else:
            error = True
        
        if(error):
          continue
        
        candidates[offset_parent] = (swapper_addr, tasks)
    
    if(len(candidates) == 0):
      return False
    
    # There should only be max 2 remaining offsets: parent and real_parent. assert parent is the last one (higher address).
    self.debug("potential offset_parents: %s" % ', '.join([str(int(i)) for i in candidates.keys()]))
    offset_parent = max(candidates.keys())
    
    # Save offsets and addresses
    c['tasks'] = candidates[offset_parent][1]
    
    c['swapper_addr'] = candidates[offset_parent][0]
    c['offset_comm'] = c['swapper_comm_addr'] - c['swapper_addr']
    c['offset_tasks'] = c['swapper_tasks_addr'] - c['swapper_addr']
    c['offset_parent'] = offset_parent
    c['init_addr'] = c['init_comm_addr'] - c['offset_comm']
    
    self.debug("swapper_addr = %08x, init_addr = %08x" % (c['swapper_addr'], c['init_addr']))
    self.debug("offset_comm = %d, offset_tasks = %d, offset_parent = %d" % (c['offset_comm'], c['offset_tasks'], c['offset_parent']))
    
    return True

  
  def find_pid_mm(self):
    """
    Third fingerprinting step: Find pid and mm fields.
    Cf http://lxr.free-electrons.com/source/include/linux/mm_types.h#L222
    """
    
    c = self.context
    
    # Get the pid and tgid offsets
    for potential_offset_pid in range(0, self.MAX_TASK_SIZE):
      swapper_pid = self.read_int(c['swapper_addr']+potential_offset_pid)
      init_pid = self.read_int(c['init_addr']+potential_offset_pid)
      third_pid = self.read_int(c['tasks'][2][1]+potential_offset_pid)

      # check pids using the first 3 process
      if(swapper_pid == 0 and init_pid == 1 and third_pid == 2):
        self.debug("potential_offset_pid = %d" % potential_offset_pid)
        
        # the test is true for the pid but also for the tgid; break on first
        c['offset_pid'] = potential_offset_pid
        break
        
        
        
    # Find mm offset. assert it is before pid (seems to be true for Linux < 2.6.11
    for offset_mm in range(0, c['offset_pid']):
      try: 
        swapper_mm_addr = self.read_int(c['swapper_addr']+offset_mm)
        init_mm_addr = self.read_int(c['init_addr']+offset_mm)
        third_mm_addr = self.read_int(c['tasks'][2][1]+offset_mm)
        
        # Only init has a mm (type: mm_struct)
        if(swapper_mm_addr == 0 and third_mm_addr == 0 and init_mm_addr > PAGE_OFFSET):
          init_mm_addr -= PAGE_OFFSET
          
          # assert mmap (type: vm_area_struct) is the first member of mm_struct
          init_mmap_addr = self.read_va(init_mm_addr)
          
          if init_mmap_addr > 0:
            for offset_vm_mm in range(100): # TODO: What could be a reasonable range?
              if init_mm_addr == self.read_va(init_mmap_addr + offset_vm_mm):
                self.debug("offset_mm = %d" % offset_mm)
                c['offset_mm'] = offset_mm
                c['init_mm_addr'] = init_mm_addr
                c['offset_mmap'] = 0 # mmap member is always the first member of mm
                return True
          '''
          if(init_mmap_addr > 0 and init_mm_addr == self.read_va(init_mmap_addr)):
            self.debug("offset_mm = %d" % offset_mm)
            c['offset_mm'] = offset_mm
            c['init_mm_addr'] = init_mm_addr
            c['offset_mmap'] = 0
            return True
          '''
            
      except:
        pass
    
    return False
  
  
  def find_pgd_arch(self):
    """
    Fifth fingerprinting step: find the pgd offset in mm_struct and the architecture.
    """
    
    c = self.context
  
    # Get available architectures
    archs_names = map( lambda f: f[:-3], 
                       filter(lambda f: f != '__init__.py' and f[-3:] == '.py', 
                              os.listdir(os.path.dirname(__file__)+"/mm/arch")
                              )
                       )
    archs = {}
    for a in archs_names:
      archs[a] = __import__('mm.arch.'+a, globals(), locals(), 'va_to_pa')
      
      
    for offset_pgd in range(0, self.MAX_VM_AREA_SIZE):
      
      init_pgd = self.read_va(c['init_mm_addr']+offset_pgd)
      
      if(init_pgd > 0):
    
        # Find pgd offsets and detect architecture
        for name, module in archs.items():
          
          try:
            a = module.va_to_pa(c['init_mm_addr']+PAGE_OFFSET, init_pgd)
            if(a == c['init_mm_addr']):
              self.debug("offset_pgd = %d" % offset_pgd)
              self.debug("arch = %s" % name)
              c['offset_pgd'] = offset_pgd
              c['arch_name'] = name
              return True
              
          except:
            pass
    
    return False
    
    
  def find_file_offsets(self):
    """
    Fourth fingerprinting step: find vm_file, f_dentry and vm_pgoff offsets
    """
    c = self.context
    
    # Get init's first vm_area
    init_1st_vmarea = self.read_va(c['init_mm_addr'] + c['offset_mmap'])
    
    # Brute force the offset of vm_file starting at vm_area end
    for offset_vmfile in range(self.MAX_VM_AREA_SIZE, 0, -4):
    
      # Browse the list of vm_areas - assert that vm_next is always at a stable offset
      offset_vm_next = HARDCODED_OFFSETS["vm_area_struct"]["vm_next"]
      
      l = []
      vmarea = init_1st_vmarea
      end = error = False
      while not end and not error:
      
        # Read the vm_file field
        vmfile = self.read_int(vmarea + offset_vmfile)
        
        # Assert vm_pgoff is just before
        vmpgoff = self.read_int(vmarea + offset_vmfile - 4)
        
        # Break if invalid fields (vm_file is either null or > PAGE_OFFSET, and vm_pgoff can't be too large)
        if(vmfile != 0 and (vmfile < PAGE_OFFSET or vmpgoff > PAGE_OFFSET)):
          error = True
        else:
        
          if(vmfile !=0):
            l.append((vmfile, vmpgoff))
            
          # Go to the next vm_area
          vmarea = self.read_va(vmarea + offset_vm_next)
        
          # Break if we reach the end of the list
          if(vmarea < 0):
            end = True
      
      # If there was an error, or if the list si empty, of if there are non-unique elements, break
      # Warning: there may have some non-unique elements, so this is not a pruning criterion.
      if(error or len(l) == 0):
        continue
        
      # The list should not contain only (vm_file, 0) couples
      if(len(filter(lambda x: x[1] != 0, l)) == 0):
        continue
        
      # If the offset is good, every (vm_file, vm_pgoff) with vm_pgoff != 0 should be preceeded by (vm_file, vm_pgoff2) with vm_pgoff2 =< vm_pgoff
      for i in range(len(l)-1, -1, -1):
        f, o = l[i]
        if(o != 0 and (i == 0 or l[i-1][0] != f or l[i-1][1] > o)):
          error = True
          break
        
      if(error):
        continue
      
      # Debug
      #print "offset_vmfile = %d, vm_files = %s" % (offset_vmfile, ",".join("(%08x, %d)" % (i,j) for (i,j) in l))
      
      # Not necessary...
      # Compute a score : # of couples / # of couples with vm_pgoff = 0
      # Take the higher
      #print "offset_vmfile = %d, score = %f" % (offset_vmfile, (float(len(l)) / len(filter(lambda x: x[1] ==0, l))))
      
      # Save the first non-null vmfile for later
      c['first_nonnull_vmfile'] = filter(lambda x: x[1] != 0, l)[0][0]
      break
      
    
    # Fill the context
    c['offset_vmfile'] = offset_vmfile
    c['offset_vmpgoff'] = offset_vmfile - 4
    self.debug("offset_vmfile = %d" % offset_vmfile)
    
    vmfile = c['first_nonnull_vmfile'] - PAGE_OFFSET
    
    # Bruteforce f_dentry offset
    for offset_fdentry in range(0, self.MAX_VM_FILE_SIZE):
      fdentry = self.read_va(vmfile + offset_fdentry)
      
      if(fdentry > 0):
        
        try:
          # Bruteforce d_name (type: qstr) offset and assert the offset of name within qstr is constant 
          for offset_qstr in range(0, self.MAX_VM_FILE_SIZE):
            name_addr = self.read_va(fdentry + offset_qstr + HARDCODED_OFFSETS["qstr"]["name"])
            
            if(name_addr > 0):
            
              try:
              
                # Read the 4 first bytes of the name, they have to be ascii
                s = str(self.r.read_string(name_addr, 4))
                if(not all(ord(c) < 128 for c in s)):
                  continue
                  
                # If the full name is 'init' or looks like a .so, it is the good one
                if(s == "init" or re.search("\.so(\.[0-9]+)*$", str(self.r.read_string(name_addr)))):
                  end = True
                  
                  self.debug("offset_fdentry = %d, offset_qstr = %d" % (offset_fdentry, offset_qstr))
                  
                  # Fill the context
                  c['offset_fdentry'] = offset_fdentry
                  c['offset_qstr'] = offset_qstr
                  return True
              
              except:
                continue
          
        except:
          continue
    
    return False
  
  
  def finalize(self):
    """
    Final step: prepare variables
    """
    
    c = self.context
    
    self.init_task = c['swapper_addr'] + PAGE_OFFSET # supposed to be a va
    self.arch_name = c['arch_name']
    
    # task_struct offsets
    self.offsets['task_struct'] = {}
    for name in ["pid", "comm", "parent", "tasks", "mm"]:
      self.offsets['task_struct'][name] = int(c['offset_'+name])
    
    # mm_struct offsets
    self.offsets['mm_struct'] = {}
    for name in ["pgd", "mmap"]:
      self.offsets['mm_struct'][name] = int(c['offset_'+name])
      
    # hardcoded offsets
    self.offsets.update(HARDCODED_OFFSETS)
    
    # file offsets
    self.offsets['vm_area_struct']['vm_file'] = c['offset_vmfile']
    self.offsets['vm_area_struct']['vm_pgoff'] = c['offset_vmpgoff']
    self.offsets['file'] = {'f_dentry': c['offset_fdentry']}
    self.offsets['dentry'] = {'d_name': c['offset_qstr']}
    
    
    return True
  
