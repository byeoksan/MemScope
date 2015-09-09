"""
adb.py

author : Park Eru <eru1729@kaist.ac.kr>


Main objective

    Simple sciprt helper function set for adb commands


System Requirements

    1. python2.7 or higher
    2. android-tools-adb

"""

import subprocess


"""
    adb_start_server(guest_ip)

    string -> None
    
    starts adb server and make it a root
"""
def adb_start_server(guest_ip, redirect=subprocess.STDOUT):
    subprocess.call(['adb', 'start-server'], stdout=redirect, stderr=redirect)
    subprocess.call(['adb', 'root'], stdout=redirect, stderr=redirect)
    subprocess.call(['adb', 'connect', guest_ip], stdout=redirect, stderr=redirect)


"""
    adb_meminfo(guest_ip, dest)

    string int -> None

    write the result of meminfo command to destination
    
    return the result
"""

def adb_meminfo(guest_ip, redirect=subprocess.STDOUT):
    output = ''
    if "connected" in subprocess.check_output(["adb", "connect", guest_ip], stderr=subprocess.STDOUT):
        output = subprocess.check_output(["adb", "shell", 'dumpsys', 'meminfo'], stderr=redirect)
    else:
        print "could not connect to " + guest_ip + " while adb_meminfo"

    return output


"""
    adb_flush_log(guest_ip)

    string -> None

    flush logcat log and disconnect the connection
"""
def adb_flush_log(guest_ip, redirect=subprocess.STDOUT):
    if "connected" in subprocess.check_output(["adb", "connect", guest_ip], stderr=subprocess.STDOUT):
       subprocess.call(["adb", "logcat", '-c'], stdout=redirect, stderr=redirect)
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

    if "connected" in subprocess.check_output(["adb", "connect", guest_ip], stderr=subprocess.STDOUT):
        output = subprocess.check_output(["adb", "logcat", '-d', '-v', 'threadtime'], stderr=subprocess.STDOUT)
        dmesg_output = subprocess.check_output(["adb", "shell", "dmesg", "-d"], stderr=subprocess.STDOUT)
    else:
        print "could not connect to " + guest_ip + " while adb_log"

    return output, dmesg_output



"""
    adb_send_key(guest_ip, keycode, redirect=subprocess.STDOUT):

    string, string, int -> None
"""
def adb_send_key(guest_ip, keycode, redirect=subprocess.STDOUT):
    if "connected" in subprocess.check_output(["adb", "connect", guest_ip], stderr=subprocess.STDOUT):
       subprocess.call(["adb", "shell", 'input', 'keyevent', keycode], stdout=redirect, stderr=redirect)
    else:
        print "could not connect to " + guest_ip + " while adb_flush_log"

"""
    adb_send_touch(guest_ip, coord, redirect=subprocess.STDOUT):

    string, int, tuple -> None
"""
def adb_send_touch(guest_ip, coord, redirect=subprocess.STDOUT):
    if "connected" in subprocess.check_output(["adb", "connect", guest_ip], stderr=subprocess.STDOUT):
       subprocess.call(["adb", "shell", 'input', 'tap', coord[0], coord[1]], stdout=redirect, stderr=redirect)
    else:
        print "could not connect to " + guest_ip + " while adb_flush_log"

"""
    adb_send_key(guest_ip, input_str, redirect=subprocess.STDOUT):

    string, int, string -> None
"""
def adb_send_key(guest_ip, input_str, redirect=subprocess.STDOUT):
    if "connected" in subprocess.check_output(["adb", "connect", guest_ip], stderr=subprocess.STDOUT):
       subprocess.call(["adb", "shell", 'input', 'text', input_str], stdout=redirect, stderr=redirect)
    else:
        print "could not connect to " + guest_ip + " while adb_flush_log"

"""
"""

def adb_install_pkg(guest_ip, pkgloc, redirect):
    pass

"""
"""
def adb_uninstall_pkg(guest_ip, redirect, pkgname):
    pass
