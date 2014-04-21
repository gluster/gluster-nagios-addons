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
SHOW_SWAP_STATUS_UNKNOWN_IP = {}

SHOW_SWAP_STATUS_UNKNOWN_OP = \
    {'message': "SWAP STATUS UNKNOWN", 'exit_status': 3}

SHOW_SWAP_STATUS_OK_IP = \
    {'date': '2014-03-10',
     'utc': '1', 'interval': '60',
     'time': '12:40:01', 'memory': {
         'swpused-percent': '0.00',
         'swpused': '0', 'per': 'second',
         'swpcad': '0', 'swpfree': '20971516',
         'swpcad-percent': '0.00',
         'unit': 'kB'}}

SHOW_SWAP_STATUS_OK_OP = \
    {'message': "OK- 0.00% used(0.00GB out of 20.00GB)|"
     "Used=0.00GB;10.00;16.00;0;20.00", 'exit_status': 0}

SHOW_SWAP_STATUS_WARNING_IP = \
    {'date': '2014-03-10',
     'utc': '1', 'interval': '60',
     'time': '12:40:01', 'memory':
     {'swpused-percent': '50.00',
      'swpused': '10485758', 'per': 'second',
      'swpcad': '0', 'swpfree': '10485758',
      'swpcad-percent': '0.00',
      'unit': 'kB'}}

SHOW_SWAP_STATUS_WARNING_OP = \
    {'message': "WARNING- 50.00% used(10.00GB out "
     "of 20.00GB)|Used=10.00GB;8.00;12.00;0;20.00",
     'exit_status': 1}

SHOW_SWAP_STATUS_CRITICAL_IP = \
    {'date': '2014-03-10',
     'utc': '1', 'interval': '60',
     'time': '12:40:01', 'memory':
     {'swpused-percent': '50.00',
      'swpused': '10485758', 'per': 'second',
      'swpcad': '0', 'swpfree': '10485758',
      'swpcad-percent': '0.00',
      'unit': 'kB'}}

SHOW_SWAP_STATUS_CRITICAL_OP = \
    {'message': "CRITICAL- 50.00% used(10.00GB out "
     "of 20.00GB)|Used=10.00GB;6.00;8.00;0;20.00",
     'exit_status': 2}

SHOW_SWAP_STATUS_EXCEPTION_IP = \
    {'date': '2014-03-10',
     'utc': '1', 'interval': '60',
     'time': '12:40:01', 'memory':
     {'swpused-percent': '50.00',
      'swpused': '10485758', 'per': 'second',
      'swpcad': '0',
      'swpcad-percent': '0.00',
      'unit': 'kB'}}

SHOW_SWAP_STATUS_EXCEPTION_OP = \
    {'message': "key: 'swpfree' not found",
     'exit_status': 3}
