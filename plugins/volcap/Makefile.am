
dist_glusternagiosplugins_PYTHON = \
	volcap.so \
	$(NULL)

volcap.so: volCap.c setup.py
	(cd $(srcdir); $(PYTHON) setup.py build \
		--build-temp $(abs_builddir) --build-lib $(abs_builddir))
all-local: volcap.so

EXTRA_DIST = \
	$(NULL)

EXTRA_DIST = \
	__init__.py \
	volCap.c \
	tests.py \
	setup.py

CLEANFILES = \
	volcap.o \
	volcap.so
