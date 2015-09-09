
EXTRA_CFLAGS = -g -I/home/trance/android/source/common/include/

ifdef KERNELRELEASE

obj-m := module.o
module-y := main.o


else


all:
	$(MAKE) -C /lib/modules/`uname -r`/build M=`pwd` modules
clean:
	$(MAKE) -C /lib/modules/`uname -r`/build M=`pwd` clean
	$(RM) Module.markers modules.order


endif

