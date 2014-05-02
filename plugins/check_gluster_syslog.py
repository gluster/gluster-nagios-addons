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
import select
import logging

import nscautils
from glusternagios import utils

# skeleton config parameters
__pollPeriod = 0.75  # the number of seconds between polling for new messages
__maxAtOnce = 1024  # max no of messages that are processed within one batch


def findVolName(pattern):
    # pattern is of the form <graphid>-<volume name>-<translator name>
    return pattern[pattern.find('-') + 1:pattern.rfind('-')]


def getStatusCode(alertlevel):
    if alertlevel == 'ALERT':
        return utils.PluginStatusCode.CRITICAL
    else:
        return utils.PluginStatusCode.WARNING


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
                                       getStatusCode(alertlevel),
                                       alertMsg)


def processQuorumMsg(msgid, msg, level):
    logger = logging.getLogger("processQuorumMsg")
    pluginstatus = None
    #if msgid == 106002:
    if "[MSGID: 106002]" in msg or "[MSGID: 106001]" in msg:
        # [MSGID: 106002] Server quorum lost for volume dist.
        #  Stopping local bricks.
        # [MSGID: 106001] Server quorum not met. Rejecting operation.
        pluginstatus = utils.PluginStatusCode.CRITICAL
    #elif msgid == 106003:
    elif "[MSGID: 106003]" in msg:
        # [MSGID: 106003] Server quorum regained for volume dist.
        #  Starting local bricks.
        pluginstatus = utils.PluginStatusCode.OK

    if pluginstatus >= 0:
        serviceName = "Cluster - Quorum"
        alertMsg = "QUORUM:" + msg[msg.rfind(':') + 1:]
        ret = nscautils.send_to_nsca_subproc(nscautils.getNagiosClusterName(),
                                             serviceName,
                                             pluginstatus,
                                             alertMsg)
        logger.debug(" nsca ret code for alertMsg %s - %s" % (alertMsg, ret))


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


"""
-------------------------------------------------------
This is plumbing that DOES NOT need to be CHANGED
-------------------------------------------------------
Implementor's note: Python seems to very agressively
buffer stdouot. The end result was that rsyslog does not
receive the script's messages in a timely manner (sometimes
even never, probably due to races). To prevent this, we
flush stdout after we have done processing. This is especially
important once we get to the point where the plugin does
two-way conversations with rsyslog. Do NOT change this!
See also: https://github.com/rsyslog/rsyslog/issues/22
"""
if __name__ == '__main__':
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    keepRunning = 1
    while keepRunning == 1:
        while keepRunning and sys.stdin in \
                select.select([sys.stdin], [], [], __pollPeriod)[0]:
            msgs = []
            while keepRunning and sys.stdin in \
                    select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline()
                if line:
                    msgs.append(line)
                else:  # an empty line means stdin has been closed
                    keepRunning = 0
                if len(msgs) >= __maxAtOnce:
                    break
            if len(msgs) > 0:
                onReceive(msgs)
                sys.stdout.flush()  # important,Python buffers far too much
    sys.exit(0)
