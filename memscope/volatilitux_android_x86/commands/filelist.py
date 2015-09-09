
from init import *

import getopt
import re

options = "p:r:"

def desc():
  return "Print the list of all open files for a given process"

  
def usage():
  print "Usage: filelist -p <pid> [-r <regex>]"
  print " "*3 + "pid".ljust(10) + "PID of the target process"
  print " "*3 + "regex".ljust(10) + "optional regular expression to filter filenames"

  
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
    
  if("-r" in args):
    f = lambda x: re.search(args["-r"], x)
  else:
    f = lambda x: True
    
  print "\n".join(filter(f, [str(v) for v in vmspace.getVMAreasByFileName()]))
  
  