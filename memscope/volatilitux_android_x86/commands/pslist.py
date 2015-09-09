
from init import *

options = None

def desc():
  return "Print the list of all process"


def run(module_options=None):
  
  process_list = Task.getTasks()
  print Task.getColumns()
  print "\n".join([str(c[1]) for c in process_list])
  