
from init import *

import getopt
import os

options = "p:o:"

def desc():
  return "Dump the addressable memory of a process"

  
def usage():
  print "Usage: memdmp -p <pid> -o <file>"
  print " "*3 + "pid".ljust(10) + "PID of the target process"
  print " "*3 + "file".ljust(10) + "output file"
  

def run(module_options):
  
  args = dict(module_options[0])

  if(not "-p" in args):
    raise Exception("Please specify a PID with -p")
  pid = int(args['-p'])
  
  if(not "-o" in args):
    raise Exception("Please specify an output file with -o")
  file = args['-o']
  
  if(os.path.exists(file)):
    raise Exception("The file already exists")
  
  
  process_list = dict(Task.getTasks())
  
  if(not pid in process_list):
    raise Exception("Invalid PID")
  
  vmspace = process_list[pid].mm
  
  if(isinstance(vmspace, InvalidPointer)):
    raise Exception("The target process does not have a valid memory map")
    
  
  res = vmspace.dumpMemory(file, None, None, True, True, True)
  
  print "%d bytes dumped to %s" % (res, file)
  
  