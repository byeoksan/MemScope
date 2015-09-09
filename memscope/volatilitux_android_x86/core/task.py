
from .config import *
from .kernel_struct import *
from .mm.user import *

import re
  
@unix_name("task_struct")
class Task(KernelStruct):
  
  @classmethod
  def initclass(cls):
    cls.fields_classes = {"pid": Field(int), 
                          "comm": Field(str),
                          "parent": Pointer(Task),
                          "tasks": ListHead(Task),
                          "mm": Pointer(UserSpace),
                          }
    cls.fields_aliases = {"name": "comm"}
    
    
  @classmethod
  def getColumns(cls):
    s = ""
    if(Config.debug):
      s += "Address".ljust(14)
    s += "Name".ljust(20)
    s += "PID".ljust(10)
    s += "PPID".ljust(10)
    
    if(Config.debug):
      s += "mm"
      
    return s
    
  def __repr__(self):
    s = ""
    
    if(Config.debug):
      s += ("%08x" % self.addr).ljust(14)
    s += ("%s" % self.comm).ljust(20)
    s += ("%d" % self.pid).ljust(10)
    s += ("%d" % self.parent.pid).ljust(10)
    
    if(Config.debug):
      s += ("%s" % self.mm)
      
    return s
  
  
  def next(self):
    return self.tasks.next
    
    
  def prev(self):
    return self.tasks.prev
    
  
  @classmethod
  def getTasks(cls):
    """
    Get the list of all tasks: [(pid, t), ...]
    """
    
    l = []
    t = Task(Config.init_task)
    var = True

    #while var or t.comm != "swapper":
    while var or not t.comm.startswith("swapper"):
      l.append((int(t.pid), t))
      t = t.next()
      var = False
    
    return l
    
  
  @classmethod
  def getTasksByName(cls, name, is_regex=False):
    """Get the list of tasks matching the given name. If name is a regex, is_regex must be True."""
    l = dict(cls.getTasks()).values()
    if is_regex:
      f = lambda task: re.search(name, str(task.name)) is not None
    else:
      f = lambda task: task.name == name
    return filter(f, l)

