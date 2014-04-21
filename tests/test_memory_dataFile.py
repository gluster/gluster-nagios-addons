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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#
SHOW_MEMORY_STATUS_UNKNOWN_IP = {}

SHOW_MEMORY_STATUS_UNKNOWN_OP = \
    {'message': "MEMORY STATUS UNKNOWN", 'exit_status': 3}

SHOW_MEMORY_STATUS_OK_IP = \
    {'date': '2014-03-10', 'utc': '1',
     'interval': '60',
     'time': '12:18:01',
     'memory': {'memused-percent': '46.97',
                'cached': '1519240',
                'unit': 'kB', 'per': 'second',
                'memfree': '4174044', 'inactive': '1495848',
                'commit-percent': '13.20', 'active': '1825260',
                'commit': '3805776', 'memused': '3696340',
                'buffers': '376704', 'dirty': '1696'}}

SHOW_MEMORY_STATUS_OK_OP = \
    {'message': "OK- 46.97% used(3.53GB out of 7.51GB)|"
     "Total=7.51GB;4.50;5.25;0;7.51 Used=3.53GB "
     "Buffered=0.36GB Cached=1.45GB", 'exit_status': 0}

SHOW_MEMORY_STATUS_WARNING_IP = \
    {'date': '2014-03-10', 'utc': '1',
     'interval': '60',
     'time': '12:18:01',
     'memory': {'memused-percent': '46.97',
                'cached': '1519240',
                'unit': 'kB', 'per': 'second',
                'memfree': '4174044', 'inactive': '1495848',
                'commit-percent': '13.20', 'active': '1825260',
                'commit': '3805776', 'memused': '3696340',
                'buffers': '376704', 'dirty': '1696'}}

SHOW_MEMORY_STATUS_WARNING_OP = \
    {'message': "WARNING- 46.97% used(3.53GB out of 7.51GB)"
     "|Total=7.51GB;3.00;4.50;0;7.51 Used=3.53GB"
     " Buffered=0.36GB Cached=1.45GB", 'exit_status': 1}

SHOW_MEMORY_STATUS_CRITICAL_IP = \
    {'date': '2014-03-10', 'utc': '1',
     'interval': '60',
     'time': '12:18:01',
     'memory': {'memused-percent': '46.97',
                'cached': '1519240',
                'unit': 'kB', 'per': 'second',
                'memfree': '4174044', 'inactive': '1495848',
                'commit-percent': '13.20', 'active': '1825260',
                'commit': '3805776', 'memused': '3696340',
                'buffers': '376704', 'dirty': '1696'}}

SHOW_MEMORY_STATUS_CRITICAL_OP = \
    {'message': "CRITICAL- 46.97% used(3.53GB out of 7.51GB)|"
     "Total=7.51GB;2.25;3.00;0;7.51 Used=3.53GB "
     "Buffered=0.36GB Cached=1.45GB", 'exit_status': 2}

SHOW_MEMORY_STATUS_EXCEPTION_IP = \
    {'date': '2014-03-10', 'utc': '1',
     'interval': '60',
     'time': '12:18:01',
     'memory': {'memused-percent': '46.97',
                'cached': '1519240',
                'unit': 'kB', 'per': 'second',
                'memfree': '4174044', 'inactive': '1495848',
                'commit-percent': '13.20', 'active': '1825260',
                'commit': '3805776',
                'buffers': '376704', 'dirty': '1696'}}

SHOW_MEMORY_STATUS_EXCEPTION_OP = \
    {'message': "key: 'memused' not found",
     'exit_status': 3}
