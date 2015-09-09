#
# This file shows how to use Volatilitux in a script.
# WARNING: These are only example commands you have to adapt to your will. Do not expect this script to work out of the box.
#


# Import the module
from init import * 

# Use this syntax if the file is placed in the parent directory
#from volatilitux import *


# Set the memory dump file
Config.setDumpFile("./android.bin")

# Enable automatic offset detection (to save ithe configuration, pass the output file name as a parameter)
Config.fingerprint()

# Set the configuration file (requires a valid configuration file, either exported using -o or generated using the LKM)
#Config.setConfigFile("conf.xml")

# Get all process in a list
process_list = Task.getTasks()
print "\n".join([str(c[1]) for c in process_list])

# Search by name
print "\n".join([str(t) for t in Task.getTasksByName("httpd")])
# Same thing with a regex
print "\n".join([str(t) for t in Task.getTasksByName("^httpd$", True)])

# Get the process number N
t1 = dict(process_list)[N]

# Get the list of all its vm_areas (as in memmap)
vmspace = t1.mm
vmareas = vmspace.getVMAreas()
print "\n".join([str(a) for a in vmareas])

# List all open files for this process
print "\n".join([str(v) for v in vmspace.getVMAreasByFileName()])

# Dump a memory area of the target process
print vmspace.dumpMemory("test.bin", 0x426f3000, 0x426f8000, force=False, skip=False, quiet=False)

# Dump an open file
print vmspace.dumpFile("openfile.txt", "output.txt", force=False, skip=False, quiet=False)

