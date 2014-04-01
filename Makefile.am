#
# Copyright 2014 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Refer to the README and COPYING files for full details of the license
#

# keep sorted
SUBDIRS = \
	config \
	plugins \
	$(NULL)

# The tests should be always last as they need the rest of the source to be
# prepared before running.
SUBDIRS += tests

EXTRA_DIST = \
	build-aux/pkg-version \
	gluster-nagios-addons.spec \
	gluster-nagios-addons.spec.in

CLEANFILES = \
	gluster-nagios-addons.spec \
	$(DIST_ARCHIVES) \
	$(NULL)

check-local:
	find . -path './.git' -prune -type f -o \
		-name '*.py' -o -name '*.py.in'  | xargs $(PYFLAKES) | \
		while read LINE; do echo "$$LINE"; false; done
	$(PEP8) --version
	$(PEP8) --filename '*.py,*.py.in' $(top_srcdir)
	@if test -f .gitignore; then \
	  for i in `git ls-files \*.in`; do \
	    if ! grep -q -x $${i%%.in} .gitignore; then \
	      echo "Missing $${i%%.in} in .gitignore"; exit 1; fi; \
	  done; \
	fi;

all-local: \
	gluster-nagios-addons.spec

.PHONY: srpm rpm

srpm: dist
	rpmbuild -ts $(if $(BUILDID),--define="extra_release .$(BUILDID)") $(DIST_ARCHIVES)

rpm: dist
	rpmbuild -ta $(if $(BUILDID),--define="extra_release .$(BUILDID)") \
				$(WITH_HOOKS) $(DIST_ARCHIVES)

dist-hook: gen-VERSION gen-ChangeLog
.PHONY: gen-VERSION gen-ChangeLog

gen-ChangeLog:
	if test -d .git; then \
	  $(top_srcdir)/build-aux/gitlog-to-changelog \
	    > $(distdir)/ChangeLog; \
	fi

gen-VERSION:
	if test -d .git; then \
	  $(top_srcdir)/build-aux/pkg-version --full \
	    > $(distdir)/VERSION; \
	fi
