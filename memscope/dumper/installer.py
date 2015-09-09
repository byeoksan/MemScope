import subprocess
import sys
import os

available_format = [ 'vvfat', 'vpc', 'vmdk', 'vhdx', 'vdi', 'rbd', 'raw', 
                     'host_cdrom', 'host_floppy', 'host_device', 'file', 'qed', 'qcow2', 'qcow', 
                     'parallels', 'nbd', 'dmg', 'tftp', 'ftps', 'ftp', 'https', 
                     'http', 'cow', 'cloop', 'bochs', 'blkverify', 'blkdebug']

def main():
    if os.getuid() != 0:
        print "[Error] This script should run in root"
        sys.exit(1);

    if len(sys.argv) != 5:
        print "usage: %s GUESTNAME RAMSIZE HARDISK_LOCATION CD_LOCATION" % (sys.argv[0])
        sys.exit(1)

    cd_str = "--cdrom=" + sys.argv[4]
    disk_type = ""

    if not os.path.isfile(sys.argv[3]):
        output = "There is no disk created on " + sys.argv[3] + "\n" \
                 "Do you want to create one? : [y or N] "
        
        uin = raw_input(output)
        if uin[0] == 'y':
            size = raw_input("Size : ")
            fmt = raw_input("Format : ")
            if fmt in available_format:
                subprocess.call(['qemu-img', 'create', '-f', fmt, sys.argv[3], size])
            else:
                print "[Error] Invalid format. Abort installation"
                sys.exit(1)
        else:
            print "[Error] No disk found on " + sys.argv[3]
            sys.exit(1)

    if sys.argv[4] == "IMPORT":
        uin = raw_input("To import existing VM, we need the format of disk : ")
        if uin in available_format:
            cd_str = "--import"
            disk_type = ",type="+uin
        else :
            print "[Error] Invalid format. Abort installation"
            sys.exit(1)
    else:      
        cd_str = "--cdrom=" + sys.argv[4]
    
    if sys.argv[3][0:24] != "/var/lib/libvirt/":
        print "[Warning] virsh would not accept disk out of default disk pool\n" + \
              "/var/lib/libvirt/images/ until you change the config"

    subprocess.call(["virt-install", "-n", sys.argv[1], "-r", sys.argv[2], "--connect",
                     "qemu:///system", "--disk", "path=" + sys.argv[3] + disk_type,
                     cd_str,  "--os-type=linux", "--graphics",
                     "sdl" ,"--video=vga"])

if __name__ == "__main__":
    main()
