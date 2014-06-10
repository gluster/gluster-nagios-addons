
nodist_glusternagiosplugins_PYTHON = \
	capacity.so \
	$(NULL)

capacity.so: volCap.c setup.py
	(cd $(srcdir); $(PYTHON) setup.py build \
		--build-temp $(abs_builddir) --build-lib $(abs_builddir))
all-local: capacity.so

EXTRA_DIST = \
	__init__.py \
	setup.py \
	tests.py \
	volCap.c \
	$(NULL)

CLEANFILES = \
	volcap.o \
	capacity.so
