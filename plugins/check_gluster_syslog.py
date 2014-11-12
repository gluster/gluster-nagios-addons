#! /usr/bin/python
# check_gluster_syslog.py
# Script to act on syslog messages related to gluster
# and send output to Nagios via nsca
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
#
import re
import sys

import nscautils
from glusternagios import utils


def findVolName(pattern):
    # pattern is of the form <graphid>-<volume name>-<translator name>
    return pattern[pattern.find('-') + 1:pattern.rfind('-')]


def processQuotaMsg(msg, alertlevel):
    quotapat = re.compile(r'\b\d*-[a-zA-Z0-9_-]*-quota\b')
    matches = quotapat.search(msg)
    if matches:
        volname = findVolName(matches.group())
        # Now get the actual msg
        alertMsg = "QUOTA: " + msg[msg.rfind(matches.group()) +
                                   len(matches.group()) + 1:]
        serviceName = nscautils.vol_service_name(volname, "Quota")
        nscautils.send_to_nsca_subproc(nscautils.getNagiosClusterName(),
                                       serviceName,
                                       utils.PluginStatusCode.WARNING,
                                       alertMsg)


def processQuorumMsg(msgid, msg, level):
    pluginstatus = None
    # if msgid == 106002:
    if "[MSGID: 106002]" in msg or "[MSGID: 106001]" in msg:
        # [MSGID: 106002] Server quorum lost for volume dist.
        #  Stopping local bricks.
        # [MSGID: 106001] Server quorum not met. Rejecting operation.
        alertMsg = "QUORUM: Cluster server-side quorum lost."
        pluginstatus = utils.PluginStatusCode.CRITICAL
    # elif msgid == 106003:
    elif "[MSGID: 106003]" in msg:
        # [MSGID: 106003] Server quorum regained for volume dist.
        #  Starting local bricks.
        alertMsg = "QUORUM: Cluster server-side quorum regained."
        pluginstatus = utils.PluginStatusCode.OK

    if pluginstatus >= 0:
        serviceName = "Cluster - Quorum"
        nscautils.send_to_nsca_subproc(nscautils.getNagiosClusterName(),
                                       serviceName,
                                       pluginstatus,
                                       alertMsg)


def processMsg(msg):
    'Check if msg is indeed from gluster app'
    custom_logvars = msg[:msg.find(' ')]
    level = custom_logvars.split('/')[2]
    msgid = custom_logvars.split('/')[0]
    # if msgid in ([106001,106002,106003]):
    # msgid is not populated correctly, so for now use below
    if "[MSGID: 10600" in msg:
        return processQuorumMsg(msgid, msg, level)
    # For gluster messages, need to check the source of message
    logsource = msg[msg.rfind('['):msg.rfind(']')]
    if logsource.find('quota') > -1:
        return processQuotaMsg(msg, level)


def onReceive(msgs):
    """This is the entry point where actual work needs to be done. It receives
       a list with all messages pulled from rsyslog. The list is of variable
       length, but contains all messages that are currently available. It is
       suggested NOT to use any further buffering, as we do not know when the
       next message will arrive. It may be in a nanosecond from now, but it
       may also be in three hours...
    """
    for msg in msgs:
        processMsg(msg)


if __name__ == '__main__':
    keepRunning = 1
    while keepRunning == 1:
        msgs = []
        line = sys.stdin.readline()
        if line:
            msgs.append(line)
        else:  # an empty line means stdin has been closed
            keepRunning = 0
        if len(msgs) > 0:
            onReceive(msgs)
            sys.stdout.flush()  # important,Python buffers far too much
    sys.exit(0)
