REMOTEDIR:=$(shell ./find_live_remote_dir.sh)
DESTDIR=$(REMOTEDIR)/Alias8

.PHONY: install
install:
	mkdir -p '$(DESTDIR)'
	rm -f '$(DESTDIR)'/*.pyc
	install Alias8/__init__.py '$(DESTDIR)'
	install Alias8/alias.py '$(DESTDIR)'
