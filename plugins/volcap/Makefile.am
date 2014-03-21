
dist_glusternagiosplugins_PYTHON = \
	capacity.so \
	$(NULL)

capacity.so: volCap.c setup.py
	(cd $(srcdir); $(PYTHON) setup.py build \
		--build-temp $(abs_builddir) --build-lib $(abs_builddir))
all-local: capacity.so

EXTRA_DIST = \
	$(NULL)

EXTRA_DIST = \
	__init__.py \
	volCap.c \
	tests.py \
	setup.py

CLEANFILES = \
	volcap.o \
	capacity.so
