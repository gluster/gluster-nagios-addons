#!/usr/bin/python
#
# check_remote_host.py -- nagios plugin uses Mklivestatus to get the overall
#                         status
# of a host. The entities considered for the status of the host are -
# 	1. Host is reachable
# 	2. LV/Inode Service status
#	3. CPU Utilization
#	4. Memory Utilization
#	5. Network Utilization
#	6. Swap Utilization
#
# Copyright (C) 2014 Red Hat Inc
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,USA
#

import os
import sys
import shlex
import subprocess
import socket
import getopt

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3
_checkPingCommand = "/usr/lib64/nagios/plugins/check_ping"
_commandStatusStrs = {STATUS_OK: 'OK', STATUS_WARNING: 'WARNING',
                      STATUS_CRITICAL: 'CRITICAL', STATUS_UNKNOWN: 'UNKNOWN'}
_socketPath = '/var/spool/nagios/cmd/live'


# Class for exception definition
class checkPingCmdExecFailedException(Exception):
    message = "check_ping command failed"

    def __init__(self, rc=0, out=(), err=()):
        self.rc = rc
        self.out = out
        self.err = err

    def __str__(self):
        o = '\n'.join(self.out)
        e = '\n'.join(self.err)
        if o and e:
            m = o + '\n' + e
        else:
            m = o or e

        s = self.message
        if m:
            s += '\nerror: ' + m
        if self.rc:
            s += '\nreturn code: %s' % self.rc
        return s


# Method to execute a command
def execCmd(command):
    proc = subprocess.Popen(command,
                            close_fds=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    return (proc.returncode, out, err)


# Method to check the ing status of the host
def getPingStatus(hostAddr):
    cmd = "%s -H %s" % (_checkPingCommand, hostAddr)
    cmd += " -w 3000.0,80% -c 5000.0,100%"

    try:
        (rc, out, err) = execCmd(shlex.split(cmd))
    except (OSError, ValueError) as e:
        raise checkPingCmdExecFailedException(err=[str(e)])

    if rc != 0:
        raise checkPingCmdExecFailedException(rc, [out], [err])

    return rc


# Method to execute livestatus
def checkLiveStatus(hostAddr, srvc):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(_socketPath)

    # Write command to socket
    cmd = "GET services\nColumns: state\nFilter: "
    "description = %s\nFilter: host_address = %s\n" % (srvc, hostAddr)
    s.send(cmd)

    # Close socket
    s.shutdown(socket.SHUT_WR)

    # Read the answer
    answer = s.recv(1000000)

    # Parse the answer into a table
    table = [line.split(';') for line in answer.split('\n')[:-1]]

    if len(table) > 0 and len(table[0]) > 0:
        return int(table[0][0])
    else:
        return STATUS_UNKNOWN


# Method to show the usage
def showUsage():
    usage = "Usage: %s -H <Host Address>\n" % os.path.basename(sys.argv[0])
    sys.stderr.write(usage)


# Main method
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hH:", ["help", "host="])
    except getopt.GetoptError as e:
        print (str(e))
        showUsage()
        sys.exit(STATUS_CRITICAL)

    hostAddr = ''
    if len(opts) == 0:
        showUsage()
        sys.exit(STATUS_CRITICAL)
    else:
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                showUsage()
                sys.exit()
            elif opt in ("-H", "--host"):
                hostAddr = arg
            else:
                showUsage()
                sys.exit(STATUS_CRITICAL)

    # Check ping status of the node, if its not reachable exit
    try:
        pingStatus = getPingStatus(hostAddr)
    except (checkPingCmdExecFailedException) as e:
        print "Host Status %s - Host not reachable" % \
            (_commandStatusStrs[STATUS_UNKNOWN])
        sys.exit(_commandStatusStrs[STATUS_UNKNOWN])

    if pingStatus != STATUS_OK:
        print "Host Status %s - Host not reachable" % \
            (_commandStatusStrs[STATUS_UNKNOWN])
        sys.exit(pingStatus)

    # Check the various performance statuses for the host
    diskPerfStatus = checkLiveStatus(hostAddr, 'Disk Utilization')
    cpuPerfStatus = checkLiveStatus(hostAddr, 'Cpu Utilization')
    memPerfStatus = checkLiveStatus(hostAddr, 'Memory Utilization')
    swapPerfStatus = checkLiveStatus(hostAddr, 'Swap Utilization')
    nwPerfStatus = checkLiveStatus(hostAddr, 'Network Utilization')

    # Calculate the consolidated status for the host based on above status
    # details
    finalStatus = pingStatus | diskPerfStatus | cpuPerfStatus | \
        memPerfStatus | swapPerfStatus | nwPerfStatus

    # Get the list of ciritical services
    criticalSrvcs = []
    if diskPerfStatus == STATUS_CRITICAL:
        criticalSrvcs.append('Disk Utilization')
    if cpuPerfStatus == STATUS_CRITICAL:
        criticalSrvcs.append('Cpu Utilization')
    if memPerfStatus == STATUS_CRITICAL:
        criticalSrvcs.append('Memory Utilization')
    if swapPerfStatus == STATUS_CRITICAL:
        criticalSrvcs.append('Swap Utilization')
    if nwPerfStatus == STATUS_CRITICAL:
        criticalSrvcs.append('Network Utilization')

    # Return the status
    if finalStatus == STATUS_CRITICAL:
        print "Host Status %s - Service(s) %s in CRITICAL state" % \
            (_commandStatusStrs[STATUS_WARNING], criticalSrvcs)
        sys.exit(STATUS_WARNING)

    print "Host Status %s - Services in good health" % \
        _commandStatusStrs[STATUS_OK]
    sys.exit(STATUS_OK)
