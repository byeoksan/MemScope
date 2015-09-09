
from .fields import *
from .mm.addr import *
from .raw_dump import *
from .mm.kernel import *

STRUCTS = {}

def unix_name(name):
  """
  Decorator for KernelStruct subclasses. Define the Unix name and reference it into the STRUCT global dict.
  """
  def wrap(cls):
    cls.unix_name = name
    STRUCTS[name] = cls
    return cls
  return wrap
  
  
class KernelStruct:
  """
  Main class for kernel structs
  """

  # Child class have to initialize this in the initclass() method
  fields_classes = {}
  
  # Idem, but optional
  fields_aliases = {}
  
  
  @classmethod
  def initclass(cls):
    """
    Each child class has to overload this method and define the cls.fields_classes dict.
    """
    raise Exception("KernelStruct doest not implement the initclass method!")
  
  def __init__(self, addr):
  
    # Set the base address
    if not isinstance(addr, Address):
      addr = VirtualAddress(addr)
    self.addr = addr
    
    # Build all fields from the given field class list
    self.fields = {}
    for (name, cls) in self.fields_classes.items():
      self.fields[name] = cls(self)
      self.fields[name].name = name
    
    
  @classmethod
  def setFieldOffset(cls, field_name, field_offset):
    cls.fields_classes[field_name].offset = field_offset
    
    
  def __str__(self):
    return self.__repr__()
    
    
  def __getattr__(self, name):
    """
    Provide a field accessor
    """
    
    # Is it an alias ?
    if name in self.fields_aliases:
      name = self.fields_aliases[name]
    
    # Read the field value
    if name in self.fields:
      return self.fields[name].read()
      
    else:
      raise Exception("Unknown field/method %s in class %s " % (name, self.__class__.__name__))
    

def ListHead(t):

  class ListHead_class(KernelStruct):
    @classmethod
    def initclass(cls):
      cls.fields_classes = {"next": Pointer(t, True), 
                            "prev": Pointer(t, True)}
                            
  ListHead_class.initclass()

  ListHead_class.setFieldOffset('next', 0)
  ListHead_class.setFieldOffset('prev', 4)
  
  return Field(ListHead_class)
