#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import hashlib

import volatilitux_android_x86 as vol

# Constants
PAGE_SIZE = 4096 # bytes
ZYGOTE_COMM = 'zygote'
NONAME_REGION = '_anonymous_'

VM_R  = 0x00000001 # read
VM_W  = 0x00000002 # write
VM_X  = 0x00000004 # execute
VM_S  = 0x00000080 # shared
VM_IO = 0x00004000 # memory-mapped IO

# TODO: Exception handling for invalid input
class DuplicationTable(object):
  def __init__(self, hash_func=hashlib.md5):
    self.__hashed_content_dict = {}
    self.__hash_func = hash_func

  def add(self, content, physical_addr, pid, comm, virtual_addr, region, flags):
    content_hash = self.__hash_func(content).hexdigest()

    if self.__hashed_content_dict.get(content_hash) is None:
      self.__hashed_content_dict[content_hash] = HashedContent(content_hash)

    self.__hashed_content_dict[content_hash].add(physical_addr, pid, comm, virtual_addr, region, flags)

  def finalize(self):
    for hashed_content in self.hashed_contents():
      if len(hashed_content.physical_pages()) < 2:
        self.__hashed_content_dict.pop(hashed_content.get_hash_value())

  def hashed_contents(self):
    return self.__hashed_content_dict.values()


class HashedContent(object):
  def __init__(self, content_hash):
    self.__content_hash = content_hash
    self.__physical_page_dict = {}

  def add(self, physical_addr, pid, comm, virtual_addr, region, flags):
    if self.__physical_page_dict.get(physical_addr) is None:
      self.__physical_page_dict[physical_addr] = PhysicalPage(physical_addr)

    self.__physical_page_dict[physical_addr].add(pid, comm, virtual_addr, region, flags)

  def physical_pages(self):
    return self.__physical_page_dict.values()

  def get_hash_value(self):
    return self.__content_hash


class PhysicalPage(object):
  def __init__(self, physical_addr):
    self.__physical_addr = physical_addr
    self.__virtual_page_list = []

  def add(self, pid, comm, virtual_addr, region, flags):
    virtual_page = VirtualPage(pid, comm, virtual_addr, region, flags)
    if virtual_page not in self.__virtual_page_list:
      self.__virtual_page_list.append(virtual_page)
    else:
      del virtual_page

  def virtual_pages(self):
    return self.__virtual_page_list[:]

  def get_address(self):
    return self.__physical_addr


class VirtualPage(object):
  def __init__(self, comm, pid, virtual_addr, region, flags):
    self.__comm = comm
    self.__pid = pid
    self.__virtual_addr = virtual_addr
    self.__region = region
    self.__flags = flags

  def __hash__(self):
    return hash('%s %d 0x%08x' % (self.__comm, self.__pid, self.__virtual_addr))

  def __eq__(self, other):
    return (self.__comm == other.__comm) and \
           (self.__pid == other.__pid) and \
           (self.__virtual_addr == other.__virtual_addr)

  def get_pid(self):
    return self.__pid

  def get_comm(self):
    return self.__comm

  def get_address(self):
    return self.__virtual_addr

  def get_region(self):
    return self.__region

  def get_flags(self):
    return self.__flags


def usage():
  print >> sys.stderr, '%s DUMPFILE' % sys.argv[0]

def main():
  if len(sys.argv) < 2:
    usage()
    sys.exit()

  # initialization
  dumpfile = sys.argv[1]

  vol.Config.setDumpFile(dumpfile)
  vol.Config.fingerprint()

  mem = vol.RawDump.getInstance().mem
  tasks = dict(vol.Task.getTasks()).values() # list of tasks
  zygote_pid = find_zygote_pid(tasks)

  if zygote_pid < 1:
    # error
    print >> sys.stderr, 'zygote cannot be found'
    sys.exit()

  pt_tasks = find_tasks_with_pagetable(tasks)
  app_tasks = find_application_tasks(pt_tasks, zygote_pid)
  sys_tasks = find_system_tasks(pt_tasks, zygote_pid)

  # build duplication table
  table = build_duplication_table(mem, pt_tasks, hashlib.md5)
  print_table(table)








def find_zygote_pid(tasks):
  for task in tasks:
    if str(task.comm) == ZYGOTE_COMM:
      return int(task.pid)

  return 0

def find_tasks_with_pagetable(tasks):
  pt_tasks = []

  for task in tasks:
    try:
      task.mm.getVMAreas()
      pt_tasks.append(task)
    except:
      continue

  return pt_tasks

def find_application_tasks(tasks, zygote_pid):
  app_tasks = []

  for task in tasks:
    pid = int(task.pid)
    ppid = int(task.parent.pid)

    if pid == zygote_pid or ppid == zygote_pid:
      app_tasks.append(task)

  return app_tasks

def find_system_tasks(tasks, zygote_pid):
  sys_tasks = []

  for task in tasks:
    pid = int(task.pid)
    ppid = int(task.parent.pid)

    if pid != zygote_pid and ppid != zygote_pid:
      sys_tasks.append(task)

  return sys_tasks

def build_duplication_table(mem, tasks, hash_func):
  table = DuplicationTable()

  for task in tasks:
    comm = str(task.comm)
    pid = int(task.pid)
    vmspace = task.mm
    vmareas = vmspace.getVMAreas()

    prev_region = ''
    for vmarea in vmareas:
      region = get_region_name(vmarea)
      vm_start = int(vmarea.vm_start)
      vm_end = int(vmarea.vm_end)
      vm_flags = int(vmarea.vm_flags)

      if not (vm_flags & (VM_R | VM_W | VM_X)):
        # skip protection region
        continue

      if vm_flags & VM_IO:
        # skip memory-mapped region
        continue

      if prev_region.endswith('.so') and region == NONAME_REGION:
        # assume that the very next region of library(.so) region
        # with noname is BSS segment for that library.
        region = prev_region + '(bss)'

      prev_region = region

      for vaddr in range(vm_start, vm_end, PAGE_SIZE):
        try:
          va = vol.VirtualAddress(vaddr, vmspace)
          paddr = va.pa()
        except:
          # invalid virt-to-phys mapping
          continue

        page = get_memory_chunk(mem, paddr, PAGE_SIZE)
        table.add(page, paddr, pid, comm, vaddr, region, vm_flags)

  table.finalize()
  return table

def get_region_name(vmarea):
  region = vmarea.getFile()
  return NONAME_REGION if region is None else str(region)

def get_memory_chunk(mem, addr, size):
  return mem[addr:addr+size]

def print_table(table):
  for hashed_content in table.hashed_contents():
    print hashed_content.get_hash_value()
    for physical_page in hashed_content.physical_pages():
      print '\t0x%08x' % physical_page.get_address()
      for virtual_page in physical_page.virtual_pages():
        print '\t\t%15s\t0x%08x\t%s' % (virtual_page.get_comm(),
                                        virtual_page.get_address(),
                                        virtual_page.get_region())
    print ''


if __name__ == '__main__':
  main()
