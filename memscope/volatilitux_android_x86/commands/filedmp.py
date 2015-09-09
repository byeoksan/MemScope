
from init import *

import getopt
import os

options = "p:t:o:"

def desc():
  return "Dump an open file"

  
def usage():
  print "Usage: filedmp -p <pid> -t <target_file> -o <output_file>"
  print " "*3 + "pid".ljust(15) + "PID of the target process"
  print " "*3 + "target_file".ljust(15) + "target file to dump"
  print " "*3 + "output_file".ljust(15) + "output file"
  

def run(module_options):
  
  args = dict(module_options[0])

  if(not "-p" in args):
    raise Exception("Please specify a PID with -p")
  pid = int(args['-p'])
  
  if(not "-t" in args):
    raise Exception("Please specify a target file with -t")
  target_file = args['-t']
  
  if(not "-o" in args):
    raise Exception("Please specify an output file with -o")
  output_file = args['-o']
  
  if(os.path.exists(output_file)):
    raise Exception("The file already exists")
  
  
  process_list = dict(Task.getTasks())
  
  if(not pid in process_list):
    raise Exception("Invalid PID")
  
  vmspace = process_list[pid].mm
  
  if(isinstance(vmspace, InvalidPointer)):
    raise Exception("The target process does not have a valid memory map")
    
  res = vmspace.dumpFile(target_file, output_file, True, True)
  
  print "%d bytes dumped to %s" % (res, output_file)
  
  