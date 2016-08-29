all:
	@echo "Nothing to build"

install:
	cp ./my_boxmaker.py ~/.config/inkscape/extensions 
	cp ./my_boxmaker.inx ~/.config/inkscape/extensions
	cp ./ink_helper.py ~/.config/inkscape/extensions
	cp ./my_panel.py ~/.config/inkscape/extensions
	cp ./my_edge.py ~/.config/inkscape/extensions
	cp ./my_box.py ~/.config/inkscape/extensions
	cp ./my_slots.py ~/.config/inkscape/extensions

.PHONY: all install 




