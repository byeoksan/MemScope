import subprocess
import sys
import time
import os

import libvirt
import socket

import select

ARGNUM = 5

"""
dumper.py

author : Park Eru <eru1729@kaist.ac.kr>


Main objective

    Create dump and log from android guest with certain rules


System Requirements

    1. qemu 2.0
    2. libvirt-bin package
    3. android-x86 guest
    4. python2.7 or higher
    5. Java 7 or higher
    6. Android SDK

Apparmor issue

    In this script, I've assumed that qemu guest is spawned by the virsh.
    Since the guests are spawned by virsh, the global apparmor rule for libvirt-qemu
    does not allow any right other than necessary config files.
    Add the line to /etc/apparmor.d/abstraction/libvirt-qemu as

    /tmp rw 

    I've used tmp as my dump location.
    Thus one needs to change apparmor config or the memory dump won't be written.

    This code has been tested on Ubuntu 14.04 LTS

HOWTO

    1. Install Android SDK (http://developer.android.com/sdk/index.html)
    2. Install QEMU (sudo apt-get install qemu)
    3. Install libvirt (sudo apt-get install libvirt-bin)
    4. Create Android VM (you can do this with a lot of ways. I recommend virt-install)
    5. Check IP of android guest (various ways. check arp table. it's easiest)
    6. Start the script

"""



"""
    usage()

    None -> None

    prints usage string if user input is not valid

"""
def usage():
    print "usage: %s guets_ip guestname memsize dump_dest getevent_capture" % sys.argv[0] + "\n" +        \
           "guest_ip : IP address of guest\n" +                                          \
           "memsize  : size of guest memory in MB. One can specify unit with K,M,G\n" +  \
           "dump_dest : destination dump file\n"                                      +  \
           "getevent_capture : captured getevent. this will emulate user input"
    sys.exit(1)



"""
    verify_input()

    None -> tuple

    verify user input.
    check parameter number, valid ip address, 
"""
def verify_input(): 
    global ARGNUM

    if len(sys.argv[1:]) != ARGNUM:
        usage()
    else:
        # Test if first argument is valid ipv4 string
        try:
            socket.inet_aton(sys.argv[1])
        except socket.error:
            print "Given IP is not a valid IPv4 address"
            sys.exit(1)

        # Test if second argument is valid virsh guestname and spawn the guest
        if spawn_guest(sys.argv[2]) == 1:
            sys.exit(1)

        # Test if third argument is an valid integer
        mult = 1024*1024
        value = sys.argv[3]

        if value[-1] == 'G':
            mult = 1024*1024*1024
            value = value[0:-1]
        else if value[-1] == 'M':
            value = value[0:-1]
        else if value[-1] == 'K':
            mult = 1024
            value = value[0:-1]

        try:
            int(value)
        except ValueError:
            print "Given argument " + sys.argv[3] + " is not a valid memory size"
            sys.exit(1)
       
        fpath = sys.argv[5]
        if fpath[0] != "/":
            fpath = os.getcwd() + fpath

        if !os.path.isfile(fpath):
            print "Givent argument" + sys.argv[5] + " is not a valid file name"
    
    return sys.argv[1], sys.argv[2], int(value)*mult, sys.argv[4], sys.argv[5]

"""
"""

def handle_getevent_capture(file):
    ret = []

    try:
        f = open(file, 'r')
    except IOError as s:
        print "I/O error while opening " + file
    else:
        lines = f.readlines()

        for line in lines:
            if lines[0:4] != '/dev':
                continue
            else:
                temp = line.split(' ')
                if len(temp) != 4:
                    print "Invalid input. Is this really a captured getevent output?"
                    print "This line will be ignored: " + line
                else:
                    ret.append([temp[0][0:-1], int(temp[1], 16), int(temp[2], 16), int(temp[3], 16))

        f.close()

    return ret
"""
    exec_workload()

    String String String String -> None

    run given script with given plugin, program options.
    takes None if there's no plugin to be loaded
    takes None if monekeyrunner is in bash alias.
    takes empty string if there's no options to be applied.
"""

def exec_workload(sdk_loc, script, plugin, options):
    if plugin == '' or sdk_loc == '':
        print "exec_workload takes None for no plugin case or" + \
              "monekyrunner is in bash alias"
        return

    exe_loc = ''
    if sdk_loc == None:
        exe_loc = 'monekeyrunner'
    else:
        exe_loc = sdk_loc.rstrip('/')+'/tools/monkeyrunner'

    # TODO Handle failure cases. notify users
    if plugin == None:
        subprocess.call([exe_loc, script, options])
    else:
        subprocess.call([exe_loc, '-plugin', plugin, script, options])

"""
   spawn_guest(guestname)
   
   string -> int

   starts guest if it's not running
   returns 0 if succeed 1 otherwise
"""
def spawn_guest(guestname):
    try:
        conn = libvirt.open("qemu:///system")
    except libvirt.error:
        print "Could not connect to qemu:///system"
        return 1

    try:
        guest = conn.lookupByName(guestname)
    except libvirt.error:
        print "Not a valid guest name " + guestname + '\n' + \
              "Failed to spawn a guest"
        return 1
    finally:
        conn.close()

    while guest.info()[0] != 1:
        if guest.info()[0] == 3:
            guest.resume()
        elif guest.info()[0] == 5:
            guest.create()

        time.sleep(2)
    
    return 0

"""
    monitor_string(cmd, timeout)

    array integer sring -> None 
    
    takes command array and timeout and monitor adb log.
    checks adb log asynchronously and return if [* died] or timeout ocurred
"""

def monitor_string(cmd, timeout, tgt_str):
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, close_fds=True)

    dline = time.time() + timeout
    while True:
        max_wait = dline - time.time()
        ex = select.select([pr.stdout], [], [pr.stdout], max_wait)[2]

        if dline <= time.time():
            break
        
        elif len(ex) == 0:
            line = pr.stdout.readline()
            if tgt_str in line:
                print 'LMK has worked'
                break

    pr.kill()


"""
    timed_dump(time, lcount, guest_ip, guest_name, memsize, dumploc)

    int string string int string string -> None

    flushes logcat and creates log and dump after given time has passed
"""
def timed_dump(stime, lcount, guest_ip, guest_name, memsize, dumploc):
    for i in range(lcount):
        adb_flush_log(guest_ip)  # flush log not to allow previous LMK result affect current run

        monitor_string(['adb', 'logcat', 'ActivityManager:I', '*:S'], stime, 'died')

        log_output, dm_output = adb_log(guest_ip)
        meminfo_output = adb_meminfo(guest_ip)
        virsh_qemudmp(guest_name, memsize, dumploc+"_"+i)

        lgwrite_wrapper(dumploc+"_log_" + i, log_output)
        lgwrite_wrapper(dumploc+"_dmesg_" + i, dm_output)
        lgwrite_wrapper(dumploc+"_meminfo_" + i, meminfo_output)


"""
    adb_start_server(guest_ip)

    string -> None
    
    starts adb server and make it a root
"""
def adb_start_server(guest_ip):
    global DEVNULL

    subprocess.call(['adb', 'start-server'], stdout=DEVNULL, stderr=DEVNULL)
    subprocess.call(['adb', 'root'], stdout=DEVNULL, stderr=DEVNULL)
    subprocess.call(['adb', 'connect', guest_ip], stdout=DEVNULL, stderr=DEVNULL)


"""
    adb_meminfo(guest_ip, dest)

    string -> None

    write the result of meminfo command to destination
    
    return the result
"""

def adb_meminfo(guest_ip):
    global DEVNULL

    output = ''
    if "connected" in subprocess.check_output(["adb", "connect", guest_ip], stderr=subprocess.STDOUT):
        output = subprocess.check_output(["adb", "shell", 'dumpsys', 'meminfo'], stderr=DEVNULL)
    else:
        print "could not connect to " + guest_ip + " while adb_meminfo"

    return output

"""
"""
def adb_sendevent(guest_ip, cmds):
    global DEVNULL

    if "connected" in subprocess.check_output(["adb", "connect", guest_ip], stderr=subprocess.STDOUT):
        subprocess.call(["adb", "shell", "sendevent"] + cmds, stdout=DEVNULL, stderr=DEVNULL)
    else:
        print "could not connected to " + guest_ip + " while adb_sendevent"


"""
    pkg_location should be in host 
"""
def adb_install_package(guest_ip, pkg_location):
    global DEVNULL

    # I'll have to check pkg_location is file or not
    if "connected" in subprocess.check_output(["adb", "connect", guest_ip], stderr=subprocess.STDOUT):
        subprocess.call(["adb", "install", pkg_location], stdout=DEVNULL, stderr=DEVNULL)
    else:
        print "could not connected to " + guest_ip + " while adb_install_package"


"""
"""
def adb_start_app(guest_ip, app):
    global DEVNULL

    if "connected" in subprocess.check_output(["adb", "connect", guest_ip], stderr=subprocess.STDOUT):
        subprocess.call(["adb", "shell", "am", "start", "-a", "android.intent.action.MAIN", "-n", app], stdout=DEVNULL, stderr=DEVNULL)
    else:
        print "could not connected to " + guest_ip + " while adb_start_app"


"""
    adb_flush_log(guest_ip)

    string -> None

    flush logcat log and disconnect the connection
"""
def adb_flush_log(guest_ip):
    global DEVNULL

    if "connected" in subprocess.check_output(["adb", "connect", guest_ip], stderr=subprocess.STDOUT):
        subprocess.call(["adb", "logcat", '-c'], stdout=DEVNULL, stderr=DEVNULL)
    else:
        print "could not connect to " + guest_ip + " while adb_flush_log"


"""
    adb_log(guest_ip)

    string -> string, string

    connects to given ip address and query logcat, dmesg.
    return logcat and dmesg string buffer
"""
def adb_log(guest_ip):
    output = ""
    dmesg_output = ""

    if "connected" in subprocess.check_output(["adb", "connect", guest_ip],
                                               stderr=subprocess.STDOUT):
        output = subprocess.check_output(["adb", "logcat", '-d', '-v', 'threadtime'],
                                         stderr=subprocess.STDOUT)
        dmesg_output = subprocess.check_output(["adb", "shell", "dmesg", "-d"],
                                               stderr=subprocess.STDOUT)
    else:
        print "could not connect to " + guest_ip + " while adb_log"

    return output, dmesg_output


"""
    virsh_qemudmp(guest_name, memsize, dumploc)

    string, int, string -> None

    suspend guest and dump memory then resume it.
    since we're using virsh, we can suspend through virsh directly.
"""
def virsh_qemudmp(guest_name, memsize, dumploc):
    global DEVNULL

    # this call is equivalent to subprocess.call(['virsh', 'suspend', guest_name)
    subprocess.call(['virsh', 'qemu-monitor-command', '--hmp', guest_name, 'stop'],
                     stdout=DEVNULL, stderr=DEVNULL)


    print "dumping memory to " + dumploc + "..."
    # this call requires qemu monitor connection
    subprocess.call(['virsh', 'qemu-monitor-command', '--hmp', guest_name, 
                     'pmemsave 0 0x%x \"%s\"' % (memsize, dumploc)],
                     stdout=DEVNULL, stderr=DEVNULL)
    print "dumped %dMB to %s" % (memsize/(1024*1024), dumploc)

    # this call is equivalent to subprocess.call(['virsh', 'resume', guest_name)
    subprocess.call(['virsh', 'qemu-monitor-command', '--hmp', guest_name, 'cont'],
                     stdout=DEVNULL, stderr=DEVNULL)

    
"""
    lgwrite_wrapper(dest, content)

    string string -> None

    wrapper for writing string to designated file location
"""

def lgwrite_wrapper(dest, content):
    try:
        logfile = open(dest, 'w')
        logfile.write(content)
        logfile.close()
        print "logfile created with name " + dest
    except:
        print "please provide valid destination for log\n" \
            + "dumping log output to stdout...\n"          \
            + content

def main():
    global DEBUG
    global DEVNULL
    ip_address, guest_name, memsize, dumploc, g_capture = verify_input()

    DEVNULL = open(os.devnull, 'w')

    adb_start_server(ip_address)

    # TODO 1 if given ram > 5G, dump onto two separate dump file since qemu cannot dump over 4G at a time

    print "reading logcat output from the guest..."
    logcat_output, dmesg_output = adb_log(ip_address)
    meminfo_output = adb_meminfo(ip_address)

    virsh_qemudmp(guest_name, memsize, dumploc) 

    print "writing log..."
    lgwrite_wrapper(dumploc+"_log", logcat_output)
    lgwrite_wrapper(dumploc+"_dmesg", dmesg_output)
    lgwrite_wrapper(dumploc+"_meminfo", meminfo_output)

    print "testing timed_dump......."
    print "this will flush current logs and write what happened in 60 seconds" 
    timed_dump(60, 3, ip_address, guest_name, memsize, dumploc+"_timed")

    subprocess.call(['adb', 'kill-server'])
    DEVNULL.close()

if __name__ == "__main__":
    main()
