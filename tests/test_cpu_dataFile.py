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

SHOW_CPU_STATUS_UNKNOWN_IP = {}

SHOW_CPU_STATUS_UNKNOWN_OP = \
    {'message': "CPU STATUS UNKNOWN", 'exit_status': 3}

SHOW_CPU_STATUS_OK_IP = \
    {'date': '2014-03-10', 'utc': '1',
     'cpu-load': {'cpu':
                  [{'iowait': '0.93',
                    'system': '0.71',
                    'number': 'all',
                    'idle': '94.89',
                    'user': '3.46',
                    'steal': '0.00',
                    'nice': '0.00'},
                   {'iowait': '0.63',
                    'system': '0.58',
                    'number': '0',
                    'idle': '94.91',
                    'user': '3.87',
                    'steal': '0.00',
                    'nice': '0.00'},
                   {'iowait': '2.00',
                    'system': '0.85',
                    'number': '1',
                    'idle': '94.24',
                    'user': '2.90',
                    'steal': '0.00',
                    'nice': '0.00'},
                   {'iowait': '0.82',
                    'system': '0.73',
                    'number': '2',
                    'idle': '94.97',
                    'user': '3.46',
                    'steal': '0.00',
                    'nice': '0.02'},
                   {'iowait': '0.28',
                    'system': '0.67',
                    'number': '3',
                    'idle': '95.43',
                    'user': '3.62',
                    'steal': '0.00',
                    'nice': '0.00'}]},
     'time': '13:22:01',
     'interval': '60'}

SHOW_CPU_STATUS_OK_OP = \
    {'message': "CPU Status OK: Total CPU:5.11% Idle CPU:94.89%"
     " | num_of_cpu=4 cpu_all_total=5.11%;60;90 cpu_all_system="
     "0.71% cpu_all_user=3.46% cpu_all_idle=94.89% cpu_0_total="
     "5.09%;60;90 cpu_0_system=0.58% cpu_0_user=3.87% cpu_0_"
     "idle=94.91% cpu_1_total=5.76%;60;90 cpu_1_system=0.85% "
     "cpu_1_user=2.90% cpu_1_idle=94.24% cpu_2_total=5.03%;60;"
     "90 cpu_2_system=0.73% cpu_2_user=3.46% cpu_2_idle=94.97%"
     " cpu_3_total=4.57%;60;90 cpu_3_system=0.67% cpu_3_user="
     "3.62% cpu_3_idle=95.43%", 'exit_status': 0}

SHOW_CPU_STATUS_WARNING_IP = \
    {'date': '2014-03-10', 'utc': '1',
     'cpu-load': {'cpu':
                  [{'iowait': '0.93',
                    'system': '0.71',
                    'number': 'all',
                    'idle': '94.89',
                    'user': '3.46',
                    'steal': '0.00',
                    'nice': '0.00'},
                   {'iowait': '0.63',
                    'system': '0.58',
                    'number': '0',
                    'idle': '94.91',
                    'user': '3.87',
                    'steal': '0.00',
                    'nice': '0.00'},
                   {'iowait': '2.00',
                    'system': '0.85',
                    'number': '1',
                    'idle': '94.24',
                    'user': '2.90',
                    'steal': '0.00',
                    'nice': '0.00'},
                   {'iowait': '0.82',
                    'system': '0.73',
                    'number': '2',
                    'idle': '94.97',
                    'user': '3.46',
                    'steal': '0.00',
                    'nice': '0.02'},
                   {'iowait': '0.28',
                    'system': '0.67',
                    'number': '3',
                    'idle': '95.43',
                    'user': '3.62',
                    'steal': '0.00',
                    'nice': '0.00'}]},
     'time': '13:22:01',
     'interval': '60'}

SHOW_CPU_STATUS_WARNING_OP = \
    {'message': "CPU Status WARNING: Total CPU:5.11% Idle"
     " CPU:94.89% | num_of_cpu=4 cpu_all_total=5.11%;5;10"
     " cpu_all_system=0.71% cpu_all_user=3.46% cpu_all_idle"
     "=94.89% cpu_0_total=5.09%;5;10 cpu_0_system=0.58% "
     "cpu_0_user=3.87% cpu_0_idle=94.91% cpu_1_total=5.76%"
     ";5;10 cpu_1_system=0.85% cpu_1_user=2.90% cpu_1_idle="
     "94.24% cpu_2_total=5.03%;5;10 cpu_2_system=0.73% "
     "cpu_2_user=3.46% cpu_2_idle=94.97% cpu_3_total=4.57%"
     ";5;10 cpu_3_system=0.67% cpu_3_user=3.62% "
     "cpu_3_idle=95.43%", 'exit_status': 1}

SHOW_CPU_STATUS_CRITICAL_IP = \
    {'date': '2014-03-10', 'utc': '1',
     'cpu-load': {'cpu':
                  [{'iowait': '0.93',
                    'system': '0.71',
                    'number': 'all',
                    'idle': '94.89',
                    'user': '3.46',
                    'steal': '0.00',
                    'nice': '0.00'},
                   {'iowait': '0.63',
                    'system': '0.58',
                    'number': '0',
                    'idle': '94.91',
                    'user': '3.87',
                    'steal': '0.00',
                    'nice': '0.00'},
                   {'iowait': '2.00',
                    'system': '0.85',
                    'number': '1',
                    'idle': '94.24',
                    'user': '2.90',
                    'steal': '0.00',
                    'nice': '0.00'},
                   {'iowait': '0.82',
                    'system': '0.73',
                    'number': '2',
                    'idle': '94.97',
                    'user': '3.46',
                    'steal': '0.00',
                    'nice': '0.02'},
                   {'iowait': '0.28',
                    'system': '0.67',
                    'number': '3',
                    'idle': '95.43',
                    'user': '3.62',
                    'steal': '0.00',
                    'nice': '0.00'}]},
     'time': '13:22:01',
     'interval': '60'}

SHOW_CPU_STATUS_CRITICAL_OP = \
    {'message': "CPU Status CRITICAL: Total CPU:5.11% "
     "Idle CPU:94.89% | num_of_cpu=4 cpu_all_total=5.11%"
     ";3;4 cpu_all_system=0.71% cpu_all_user=3.46% "
     "cpu_all_idle=94.89% cpu_0_total=5.09%;3;4 cpu_0_"
     "system=0.58% cpu_0_user=3.87% cpu_0_idle=94.91% "
     "cpu_1_total=5.76%;3;4 cpu_1_system=0.85% cpu_1_us"
     "er=2.90% cpu_1_idle=94.24% cpu_2_total=5.03%;3;4 "
     "cpu_2_system=0.73% cpu_2_user=3.46% cpu_2_idle="
     "94.97% cpu_3_total=4.57%;3;4 cpu_3_system=0.67% "
     "cpu_3_user=3.62% cpu_3_idle=95.43%", 'exit_status': 2}

SHOW_CPU_STATUS_EXCEPTION_IP = \
    {'date': '2014-03-10', 'utc': '1',
     'cpu-load': {},
     'time': '13:22:01',
     'interval': '60'}\

SHOW_CPU_STATUS_EXCEPTION_OP = \
    {'message': "key: 'cpu' not found",
     'exit_status': 3}

SHOW_CPU_STATUS_SINGLE_CORE_IP = \
    {'date': '2014-03-10', 'utc': '1',
     'cpu-load': {'cpu':
                  [{'iowait': '0.63',
                    'system': '0.58',
                    'number': 'all',
                    'idle': '94.91',
                    'user': '3.87',
                    'steal': '0.00',
                    'nice': '0.00'},
                   {'iowait': '0.63',
                    'system': '0.58',
                    'number': '0',
                    'idle': '94.91',
                    'user': '3.87',
                    'steal': '0.00',
                    'nice': '0.00'}]},
     'time': '13:22:01',
     'interval': '60'}

SHOW_CPU_STATUS_SINGLE_CORE_OP = \
    {'message': "CPU Status OK: Total CPU:5.09% Idle CPU:94.91%"
     " | num_of_cpu=1 cpu_all_total=5.09%;60;90 cpu_all_system="
     "0.58% cpu_all_user=3.87% cpu_all_idle=94.91%", 'exit_status': 0}
