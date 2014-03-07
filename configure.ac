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

# Autoconf initialization
AC_INIT([gluster-nagios-addons],
        [m4_esyscmd([build-aux/pkg-version --version])],
        [rhs-bugs@redhat.com])
AC_CONFIG_AUX_DIR([build-aux])

m4_include([m4/ax_python_module.m4])

# Package release
AC_SUBST([PACKAGE_RELEASE],
         [m4_esyscmd([build-aux/pkg-version --release])])

# Testing for version and release
AS_IF([test "x$PACKAGE_VERSION" = x],
      AC_MSG_ERROR([package version not defined]))
AS_IF([test "x$PACKAGE_RELEASE" = x],
      AC_MSG_ERROR([package release not defined]))

# Automake initialization
AM_INIT_AUTOMAKE([-Wno-portability])

# Checking for build tools
AC_PROG_CC
AC_PROG_LN_S
AM_PATH_PYTHON([2.6])

# Users and groups
AC_SUBST([NAGIOSUSER], [nagios])
AC_SUBST([NAGIOSGROUP], [nagios])

# default paths
AC_SUBST([nagiospluginsdir], ['${libdir}/nagios/plugins'])
AC_SUBST([glusternagiospluginsdir], ['${nagiospluginsdir}/gluster'])
AC_SUBST([glusternagioscommonpylibdir], ['${pyexecdir}/glusternagios'])
AC_SUBST([glusternagiosaddonstestsdir], ['${datarootdir}/${PACKAGE_NAME}/tests'])

# Checking for pyflakes
AC_PATH_PROG([PYFLAKES], [pyflakes])
if test "x$PYFLAKES" = "x"; then
  AC_MSG_WARN([pyflakes not found])
fi

# Checking for pep8
AC_PATH_PROG([PEP8], [pep8])
if test "x$PEP8" = "x"; then
  AC_MSG_WARN([python-pep8 not found])
fi

# Checking for python-devel
AC_PATH_PROG([PYTHON_CONFIG], [python-config])
if test "x$PYTHON_CONFIG" = "x"; then
  AC_MSG_ERROR([python-devel not found, please install it.])
fi

# Checking for nosetests
AC_PATH_PROG([NOSETESTS], [nosetests])
if test "x$NOSETESTS" = "x"; then
  AC_MSG_ERROR([python-nose not found, please install it.])
fi

# Checking for python modules (sorted, please keep in order)
AX_PYTHON_MODULE([argparse], [fatal])
AX_PYTHON_MODULE([ethtool], [fatal])
AX_PYTHON_MODULE([glusternagios], [fatal])
AX_PYTHON_MODULE([netaddr], [fatal])
AX_PYTHON_MODULE([pthreading], [fatal])
AX_PYTHON_MODULE([pyinotify], [fatal])
AX_PYTHON_MODULE([selinux], [fatal])

# Keep sorted
AC_CONFIG_FILES([
	Makefile
	gluster-nagios-addons.spec
	plugins/Makefile
	tests/Makefile
	tests/run_tests_local.sh
	tests/run_tests.sh
])

AC_OUTPUT([], [
    chmod +x tests/run_tests.sh
    chmod +x tests/run_tests_local.sh
])
