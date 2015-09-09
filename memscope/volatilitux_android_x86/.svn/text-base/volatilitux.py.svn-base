#!/usr/bin/python

import os
import sys
import getopt

from init import *

def usage(progname):
  print ""
  print "Volatilitux v1.0"
  print "By Emilien Girault <e.girault@sysdream.com>"
  print "http://www.segmentationfault.fr"
  print ""
  print "usage: %s -f <dumpfile> [-c <configfile>] [-o] [-d] <command> [options]" % (os.path.basename(progname))
  print ""
  print "   -f <dumpfile>       Physical memory dump file to analyze"
  print "   -o                  Create an XML file with the current configuration"
  print "   -c <configfile>     Configuration file to read instead of autmatically detecting all offsets"
  print "   -d                  Enable debug mode"
  print ""
  
  print "List of supported architectures: "
  archs = map(  lambda f: f[:-3], 
               filter(lambda f: f != '__init__.py' and f[-3:] == '.py', 
                      os.listdir(os.path.dirname(progname)+"/core/mm/arch")
                      )
               )
  for a in archs:
    print " "*3  + a
  
  print
  
  # Get the list of all supported commands
  print "List of supported commands: "
  commands = map(lambda f: f[:-3], 
                 filter(lambda f: f != '__init__.py' and f[-3:] == '.py', 
                        os.listdir(os.path.dirname(progname)+"/commands")
                        )
                 )
  for c in commands:
    m = __import__('commands.'+c, globals(), locals(), 'desc')
    print " "*3  + c.ljust(20), m.desc()
    
  print
  print "To get help about a specific command: %s [options] <command> -h" % (os.path.basename(progname))

  
def main(argv=sys.argv):

  options = "ho:c:f:d"
  
  
  try:
  
    o = getopt.getopt(sys.argv[1:], options)
    short_opts = dict(o[0])
    args = o[1]
    
    # Parse standard arguments
    if((len(short_opts) == 0 and len(args) == 1) or "-h" in short_opts):
      usage(argv[0])
      sys.exit(0)
      
      
    if(not "-f" in short_opts):
      raise Exception("Dump file not specified, please use -f")
    Config.setDumpFile(short_opts["-f"])
    
    
    if("-d" in short_opts):
      Config.setDebug(True)
    
    # Parse the config file, if any
    if("-c" in short_opts):
      Config.setConfigFile(short_opts["-c"])
    
    else: # Otherwise, perform a fingerprint on the dump
      Config.fingerprint(short_opts.get("-o", None))
      
      
    # Get the module
    if(len(args) == 0):
      raise Exception("No command specified.")
    module_name = args[0]
    
    try:
      module = __import__('commands.'+module_name, globals(), locals(), ['run', 'usage', 'desc'])
    except ImportError:
      raise Exception("Invalid command specified.")
      
    # Parse the command options
    m_o = module.options
    if(m_o is None):
      m_o = ""
      
    module_options = getopt.getopt(args[1:], "h"+m_o)
    
    # Print the command help if needed
    if("-h" in dict(module_options[0])):
      print module_name + ": " + module.desc()
      try:
        module.usage()
      except AttributeError:
        print "No arguments needed."
        pass
      sys.exit(0)
      
    
    # Run the command with the specified option
    module.run(module_options)
    
  
  # Error in arguments
  except getopt.GetoptError, e:
    print "Error: " + str(e)
    usage(argv[0])
    
  except Exception, e:
    print "Error: " + str(e)
  

if __name__ == "__main__":
  main()
  
