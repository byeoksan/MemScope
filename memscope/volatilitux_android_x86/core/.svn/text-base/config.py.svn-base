
from .kernel_struct import *
from .raw_dump import *
from .fingerprint import *

from xml.dom.minidom import parse, Document
import os.path


CONFIG_VERSION = 1.0

class Config:

  init_task = None
  arch = None
  offsets = {}
  dumpfile = None
  
  debug = False
  
  
  @classmethod
  def setDebug(cls, debug=False):
    cls.debug = debug
  
  @classmethod
  def setDumpFile(cls, file):
    RawDump.setFile(file)
    dumpfile = file
    
  
  @classmethod
  def fingerprint(cls, dumpConfig=None):
    """
    Fingerprint the given raw memory dump. Save the configuation in the a file (dumpConfig) if needed.
    """
    
    res = Fingerprint(cls.dumpfile, cls.debug)
    
    if(not res.valid):
      raise Exception("Unable to fingerprint the given dumpfile. Please use a configuration file.")
    
    cls.setArch(res.arch_name)
    cls.init_task = res.init_task
    
    for struct_name, offsets in res.offsets.items():
      for field_name, offset in offsets.items():
        cls.setOffset(struct_name, field_name, offset)
        
    # Save config
    if(dumpConfig is not None):
    
      if os.path.exists(dumpConfig):
        raise Exception("The provided filename already exists.")
      
      f = open(dumpConfig, "w")
      
      doc = Document()
      
      config = doc.createElement("config")
      config.setAttribute("version", str(CONFIG_VERSION))
      doc.appendChild(config)
      
      # init_task address
      init_task = doc.createElement("init_task")
      init_task.setAttribute("address", "0x%08x" % cls.init_task)
      config.appendChild(init_task)
      
      # architecture
      arch = doc.createElement("arch")
      arch.setAttribute("name", res.arch_name)
      config.appendChild(arch)
      
      # structures
      for struct_name, offsets in res.offsets.items():
        
        struct = doc.createElement("struct")
        struct.setAttribute("name", struct_name)
        
        for field_name, offset in offsets.items():
          field = doc.createElement("field")
          field.setAttribute("name", field_name)
          field.setAttribute("offset", str(offset))
          struct.appendChild(field)
          
        config.appendChild(struct)
      

      # Generate XML and write it
      xml = doc.toprettyxml(indent="  ")
      f.write(xml)
      f.close()
      
      print "Configuration exported to %s." % dumpConfig
      
    
  
  @classmethod
  def setArch(cls, arch):
    try:
      cls.arch = __import__('mm.arch.'+arch, globals(), locals(), 'va_to_pa')
    except:
      raise Exception("Invalid arch specified.")
      
  
  @classmethod
  def setOffset(cls, struct_name, field_name, field_offset):
    cls_obj = STRUCTS[struct_name]
    cls_obj.setFieldOffset(field_name, field_offset)
    

  @classmethod
  def setConfigFile(cls, file):
  
    # parse the file
    o = parse(file)
    
    # Get init_task addr and the architecure
    res = o.getElementsByTagName("init_task")
    if(len(res) == 0):
      raise Exception("No init_task tag found in config file")
    if(not res[0].getAttribute("address")):
      raise Exception("Missing address field in init_task tag")
      
    cls.init_task = int(res[0].getAttribute("address"), 16)
    
    res = o.getElementsByTagName("arch")
    if(len(res) == 0):
      raise Exception("No arch tag found in config file")
    cls.setArch(res[0].getAttribute("name"))
    
    # Get the structure field offsets
    for s in o.getElementsByTagName("struct"):
      struct_name = s.getAttribute("name")
      
      if not struct_name in STRUCTS:
        raise Exception("Invalid struct name '%s'" % struct_name)
        
      cls = STRUCTS[struct_name]
      
      for f in s.getElementsByTagName("field"):
        field_name = f.getAttribute("name")
        field_offset = int(f.getAttribute("offset"))
        
        if not field_name in cls.fields_classes:
          raise Exception("Invalid field %s' for struct '%s'" % (field_name, struct_name))

        cls.setFieldOffset(field_name, field_offset)
  