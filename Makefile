PREFIX = /usr
PROGNAME = pymontage

build:
	true

install:
	install -m 0755 $(PROGNAME).py $(PREFIX)/bin/$(PROGNAME)
