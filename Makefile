all:
	@echo "Nothing to build"

install:
	cp ./my_boxmaker.py ~/.config/inkscape/extensions
	cp ./my_boxmaker.inx ~/.config/inkscape/extensions
	cp ./ink_helper.py ~/.config/inkscape/extensions

.PHONY: all install 




