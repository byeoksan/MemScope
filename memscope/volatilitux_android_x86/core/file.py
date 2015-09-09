
from .kernel_struct import *

@unix_name("qstr")
class Qstr(KernelStruct):
  """
  String
  """
  
  @classmethod
  def initclass(cls):
    cls.fields_classes = {"name": Pointer(str)}
  
  def __repr__(self):
    return str(self.name)
    

@unix_name("dentry")
class Dentry(KernelStruct):
  """
  Name of a file
  """
  
  @classmethod
  def initclass(cls):
    cls.fields_classes = {"d_name": Field(Qstr)}
  
  def __repr__(self):
    return str(self.d_name)

"""
@unix_name("path")
class Path(KernelStruct):
  # Path of a file
  
  @classmethod
  def initclass(cls):
    cls.fields_classes = {"dentry": Pointer(Dentry)}
  
  def __repr__(self):
    return str(self.dentry)
"""

@unix_name("file")
class File(KernelStruct):
  """
  Open file
  """
  
  @classmethod
  def initclass(cls):
    cls.fields_classes = {"f_dentry": Pointer(Dentry)}
    
  def __repr__(self):
    return "%s" % str(self.f_dentry)
    
    