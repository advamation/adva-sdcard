# adva-sdcard: Makefile
CC=gcc
CFLAGS=-O2 -Wall -Wextra -pedantic -fpic -fpie -fstack-protector-all -fstack-protector-strong -D_FORTIFY_SOURCE=2
#-fstack-clash-protection
LDFLAGS=

all: adva-sdcard-smart-get adva-sdcard-smart adva-sdcard-info

adva-sdcard-smart-get: adva-sdcard-smart-get.o
	$(CC) $(CFLAGS) -o build/adva-sdcard-smart-get build/adva-sdcard-smart-get.o $(LDFLAGS)
adva-sdcard-smart:
	cp -p adva-sdcard-smart.py build/adva-sdcard-smart
adva-sdcard-info:
	cp -p adva-sdcard-info.py build/adva-sdcard-info

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o build/$@
clean:
	rm -f build/*

.PHONY: clean
