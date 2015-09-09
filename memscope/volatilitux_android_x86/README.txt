
  Volatilitux v1.0
  by Emilien Girault <emilien.girault@sogeti.com | trance@segmentationfault.fr>
  http://www.segmentationfault.fr | http://esec-pentest.sogeti.com/
  
===================================================================================================
  
Description
============
Volatilitux is a memory forensics framework to help analyzing Linux physical memory dumps.


Features
========
Volatilitux supports the following architectures for physical memory dumps:
- ARM
- x86
- x86 with PAE enabled

It supports the following commands:
- filedmp              Dump an open file
- filelist             Print the list of all open files for a given process
- memdmp               Dump the addressable memory of a process
- memmap               Print the memory map of a process
- pslist               Print the list of all process

It can easily be extended with new architectures, commands and classes.

Volatilitux automatically detects kernel structure offsets within the memory dump, and can export its current configuration into a XML file.
If it is unable to successfuly detect offsets, you can use the provided Loadable Kernel Module to generate a configuration file.

Volatilitux has been tested with the following machines:
- Android 2.1
- Fedora 5 and 8
- Debian 5
- CentOS 5
- Ubuntu 10.10 with and without PAE

The manual offset detection using the provided LKM works successfully with all platforms.
The automatic offset detection seems to work perfectly with all machines but the two Ubuntu ones. In these cases, the only bug that has been noticed is a problem the vm_flags field (within vm_aream_struct) offset detection, causing leading to false information reported by the 'memmap' command. All the other commands seem to work perfectly on those machines.
Note: I plan to fix this bug in the next release.


License
=======
Volatilitux is released under the terms of the General Public License v2. See COPYING.txt.


Disclaimer
==========
Volatilitux is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.


Requirements
============
Volatilitux requires Python 2.6 or higher. It only uses builtin modules like:
  - getopt
  - xml.dom.minidom
  - os
  - sys
  - re
  - struct

If you plan to use the provided LKM, you must have:
  - gcc
  - make
  - your kernel header files (usually located under /usr/src/)
  
The framework has been mainly run on a Windows XP machine, but it should work will other versions of Windows, Linux and other platforms.


Installation
============
You don't need to install Volatilitux. Just extract the archive in your favorite directory, and you're ready.


Usage
=====
This is a command-line tool; its main syntax is:
  
  volatilitux.py -f <dumpfile> [-c <configfile>] [-o] [-d] <command> [options]
  
Use -f to specify which memory dump file to analyze. 
By default, Volatilitux automatically detects offsets, but you can specify a configuration file to skip this phase (of if it fails).

To get some help, run Volatilitux in a console like this:

  volatilitux.py -h
  
To use the LKM, you first have to compile it:
  
  cd ./lkm
  make

Load it as root, display kernel logs and unload it.

  insmod ./module.ko && dmesg && rmmod ./module.ko

Then you can copy the generated XML output to a configuration file (be sure to remove any non-XML character) and pass it to volatilitux:

  volatilitux -f my_dump.bin -c my_configuration_file.xml
  
Of course you can also use Volatilitux within a Python script. Please refer to the provided example.py file, and do not hesitate to browse the source.


Troubleshooting
===============

You can enable Debug mode using the -d flag. I'm concious it is very limited, but it is better than nothing...

