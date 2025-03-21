# Makefile for adva-sdcard
#
# :Author:  Advamation / Roland Freikamp <support@advamation.de>
# :Version: 2025-03-17

ifeq ($(prefix),)
    prefix := /usr/local
endif 

build:
	cd src; make
clean:
	cd src; make clean
install:
	install -d $(DESTDIR)/$(prefix)/bin
	install -d $(DESTDIR)/$(prefix)/share/doc/adva-sdcard
	install -d $(DESTDIR)/$(prefix)/share/man/man8
	cd src; make
	install -m 0755 src/build/adva-sdcard-smart-get $(DESTDIR)/$(prefix)/bin
	install -m 0755 src/build/adva-sdcard-smart     $(DESTDIR)/$(prefix)/bin
	install -m 0755 src/build/adva-sdcard-info      $(DESTDIR)/$(prefix)/bin
	ln -s adva-sdcard-smart-get $(DESTDIR)/$(prefix)/bin/adva_sdcard_smart_get
	ln -s adva-sdcard-smart     $(DESTDIR)/$(prefix)/bin/adva_sdcard_smart
	ln -s adva-sdcard-info      $(DESTDIR)/$(prefix)/bin/adva_sdcard_info
	install -m 0644 LICENSE NEWS README.md $(DESTDIR)/$(prefix)/share/doc/adva-sdcard
	install -m 0644 doc/*.8 $(DESTDIR)/$(prefix)/share/man/man8
uninstall:
	rm -f  $(DESTDIR)/$(prefix)/bin/adva-sdcard-smart-get
	rm -f  $(DESTDIR)/$(prefix)/bin/adva-sdcard-smart
	rm -f  $(DESTDIR)/$(prefix)/bin/adva-sdcard-info
	rm -f  $(DESTDIR)/$(prefix)/bin/adva_sdcard_smart_get
	rm -f  $(DESTDIR)/$(prefix)/bin/adva_sdcard_smart
	rm -f  $(DESTDIR)/$(prefix)/bin/adva_sdcard_info
	rm -rf $(DESTDIR)/$(prefix)/share/doc/adva-sdcard
	rm -rf $(DESTDIR)/$(prefix)/share/man/man8/adva-sdcard-*.8
	rm -rf $(DESTDIR)/$(prefix)/share/man/man8/adva_sdcard_*.8

.PHONY: build clean install uninstall
