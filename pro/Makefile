VENV=venv
build: venv
	. $(VENV)/bin/activate && ./scripts/build.sh
venv: requirements.txt
	python3 -m venv $(VENV) && . $(VENV)/bin/activate && pip install -r requirements.txt
	touch $(VENV)
test:
	. $(VENV)/bin/activate && fontbakery check-googlefonts -l FAIL fonts/variable/*.ttf
clean:
	rm -rf fonts/variable fonts/ttf fonts/webfonts sources/instance_ufos \
	  sources/OdraSansPro-LightItalic.ufo sources/OdraSansPro-BlackItalic.ufo \
	  sources/OdraSansPro-Italic.designspace
.PHONY: build test clean
