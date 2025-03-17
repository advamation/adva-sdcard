# sdcard_smart_get: Makefile
CC=gcc
CFLAGS=-O2 -Wall -Wextra -pedantic -fpic -fpie -fstack-protector-all -fstack-protector-strong -D_FORTIFY_SOURCE=2
#-fstack-clash-protection
LDFLAGS=

all: adva_sdcard_smart_get adva_sdcard_smart adva_sdcard_info

adva_sdcard_smart_get: adva_sdcard_smart_get.o
	$(CC) $(CFLAGS) -o build/adva_sdcard_smart_get build/adva_sdcard_smart_get.o $(LDFLAGS)
adva_sdcard_smart:
	cp -p adva_sdcard_smart.py build/adva_sdcard_smart
adva_sdcard_info:
	cp -p adva_sdcard_info.py build/adva_sdcard_info

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o build/$@
clean:
	rm -f build/*

.PHONY: clean
