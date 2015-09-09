
from init import *

import getopt

options = "p:"

def desc():
  return "Print the memory map of a process"

  
def usage():
  print "Usage: memmap -p <pid>"
  print " "*3 + "pid".ljust(10) + "PID of the target process"
  

def run(module_options):
  
  args = dict(module_options[0])

  if(not "-p" in args):
    raise Exception("Please specify a PID with -p")
  pid = int(args['-p'])
    
  process_list = dict(Task.getTasks())
  
  if(not pid in process_list):
    raise Exception("Invalid PID")
  
  vmspace = process_list[pid].mm
  
  if(isinstance(vmspace, InvalidPointer)):
    raise Exception("The target process does not have a valid memory map")
    
  vmareas = vmspace.getVMAreas()
  
  print VMArea.getColumns()
  print "\n".join([str(a) for a in vmareas])
  