#!/bin/bash

# To use this package without a problem, you would need libvirt-bin, virinst, virt-viewer packages

if [ "$#" -ne 4 ]; then
    echo "usage: $0 GUESTNAME RAMSIZE HARDISK_LOCATION CD_LOCATION"
    exit 1
fi

GUESTNAME=$1
RAMSIZE=$2
HDLOC=$3
CDLOC=$4

virt-install --arch i686 -n ${GUESTNAME} -r ${RAMSIZE} --connect qemu:///system --disk path=${HDLOC},bus=ide,format=qcow2 --cdrom=${CDLOC} --os-type=linux --graphics vnc --video=vga --vcpus=4
