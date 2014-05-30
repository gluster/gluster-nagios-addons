#!/usr/bin/python
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


import os
import re
import sys
import commands
from optparse import OptionParser
from glusternagios import utils

WARNING_LEVEL = 80
CRITICAL_LEVEL = 90
INVALID_STATUS_CODE = -1


def getVal(val):
    dmatch = re.compile('[0-9]+').match(val)
    if (dmatch):
        return float(eval(dmatch.group(0)))
    else:
        return 0


def getUsageAndFree(command, path, crit, warn, lvm):
    disk = {'path': None, 'usePcent': 0, 'avail': 0,
            'used': 0, 'size': 0, 'fs': None,
            'status': None, 'msg': None, 'availPcent': 0,
            'statusCode': utils.PluginStatusCode.UNKNOWN}

    # Check if device exists and permissions are ok
    if not os.access(path, os.F_OK):
        disk['status'] = "Device not found!"
        disk['msg'] = 'no device'
        disk['fs'] = path
        disk['statusCode'] = utils.PluginStatusCode.CRITICAL
        return disk

    if not os.access(path, os.R_OK):
        disk['status'] = "Unable to access the device"
        disk['msg'] = 'no access'
        disk['fs'] = path
        disk['statusCode'] = utils.PluginStatusCode.CRITICAL
        return disk

    status = commands.getstatusoutput(command)
    # Sample output
    # (0, 'Filesystem     1G-blocks  Used Available Use% Mounted on\n/dev/sda1
    #       290G  196G       79G  72% /')
    if status[0] != 0:
        disk['msg'] = 'error:%s' % status[0]
        if status[0] == 256:
            disk['status'] = "Brick/Device path not found!"
        else:
            disk['status'] = status[1]
        disk['statusCode'] = utils.PluginStatusCode.CRITICAL
        return disk

    status = status[1].split()
    disk['path'] = status[-1]
    disk['avail'] = getVal(status[-3])
    disk['used'] = getVal(status[-4])
    disk['size'] = getVal(status[-5])
    disk['fs'] = status[-6]
    disk['usePcent'] = getVal(status[-2])
    if disk['usePcent'] >= crit:
        disk['statusCode'] = utils.PluginStatusCode.CRITICAL
    elif disk['usePcent'] >= warn:
        disk['statusCode'] = utils.PluginStatusCode.WARNING
    elif disk['usePcent'] < warn:
        disk['statusCode'] = utils.PluginStatusCode.OK
    disk['availPcent'] = 100 - disk['usePcent']

    return disk


def getDisk(path, crit, warn, usage=None, lvm=False):
    if usage:
        return getUsageAndFree("df -B%s %s" % (usage, path),
                               path, crit, warn, lvm)
    else:
        return getUsageAndFree("df -BG %s" % path,
                               path, crit, warn, lvm)


def getInode(path, crit, warn, lvm=False):
    return getUsageAndFree("df -i %s" % path,
                           path, crit, warn, lvm)


def getMounts(searchQuery, excludeList=[]):
    mountPaths = []
    f = open("/etc/mtab")
    for i in f.readlines():
        if i.startswith(searchQuery):
            if not excludeList:
                mountPaths.append(i.split()[0])
            else:
                device = i.split()
                if not device[0] in options.exclude and\
                   not device[1] in options.exclude:
                    mountPaths.append(device[0])
    f.close()
    return mountPaths


def parse_input():
    parser = OptionParser()
    parser.add_option('-w', '--warning', action='store', type='int',
                      dest='warn',
                      help='Warning count in %', default=WARNING_LEVEL)
    parser.add_option('-c', '--critical', action='store', type='int',
                      dest='crit',
                      help='Critical count in %', default=CRITICAL_LEVEL)
    parser.add_option('-u', '--usage', action="store", dest='usage',
                      help='Usage in %/GB/MB/KB', default=None)
    parser.add_option('-l', '--lvm', action="store_true",
                      dest='lvm',
                      help='List lvm mounts', default=False)
    parser.add_option('-d', '--inode', action="store_true", dest='inode',
                      help='List inode usage along with disk/brick usage',
                      default=False)
    parser.add_option('-a', '--all', action="store_true",
                      dest='all',
                      help='List all mounts', default=False)
    parser.add_option('-n', '--ignore', action="store_true",
                      dest='ignore',
                      help='Ignore errors', default=False)
    parser.add_option('-i', '--include', action='append', type='string',
                      dest='mountPath',
                      help='Mount path', default=[])
    parser.add_option('-x', '--exclude', action="append", type='string',
                      dest='exclude',
                      help='Exclude disk/brick')
    return parser.parse_args()


def _getMsg(okList, warnList, critList):
    msg = ", ".join(critList)
    if critList and (warnList or okList):
        msg = "CRITICAL: " + msg
    if warnList:
        if msg:
            msg += "; WARNING: "
        msg += ", ".join(warnList)
    if okList:
        if msg:
            msg += "; OK: "
        msg += ", ".join(okList)
    return msg


def _getUnitAndType(val):
    unit = utils.convertSize(val, "GB", "TB")
    if unit >= 1:
        return unit, "TB"
    else:
        return val, "GB"


def showDiskUsage(warn, crit, mountPaths, toListInode, usage=False,
                  isLvm=False, ignoreError=False):
    diskPerf = []
    warnList = []
    critList = []
    okList = []
    mounts = []
    statusCode = INVALID_STATUS_CODE
    totalUsed = 0
    totalSize = 0
    noOfMounts = len(mountPaths)
    maxPercentUsed = 0

    for path in mountPaths:
        disk = getDisk(path, crit, warn, usage, isLvm)
        inode = getInode(path, crit, warn, isLvm)

        if disk['path'] in mounts:
            continue
        if not disk['used'] or not inode['used']:
            if not ignoreError:
                sys.exit(utils.PluginStatusCode.UNKNOWN)

        if disk['path']:
            mounts.append(disk['path'])
        data = ""
        if usage and disk['path']:
            data = "%s=%.1f%s;%.1f;%.1f;0;%.1f" % (
                disk['path'],
                disk['used'],
                usage,
                warn * disk['size'] / 100,
                crit * disk['size'] / 100,
                disk['size'])
            if toListInode:
                data += " %s=%.1f;%.1f;%.1f;0;%.1f" % (
                    inode['path'],
                    inode['used'],
                    warn * inode['used'] / 100,
                    crit * inode['used'] / 100,
                    inode['size'])
        elif disk['path']:
            data = "%s=%.2f%%;%s;%s;0;%sGB" % (
                disk['path'],
                disk['usePcent'],
                warn,
                crit,
                disk['size'])

            if toListInode:
                data += " %s=%.2f%%;%s;%s;0;%s" % (
                    inode['path'],
                    inode['usePcent'],
                    warn,
                    crit,
                    inode['size'])
        diskPerf.append(data)

        totalUsed += disk['used']
        totalSize += disk['size']
        if disk['usePcent'] > maxPercentUsed:
            maxPercentUsed = disk['usePcent']

        # adding into status message if there is any
        # specfic status found (short msg for list of disks)
        msg = ""
        if disk['status'] and disk['msg']:
            if noOfMounts == 1:
                msg = "%s=%s(%s)" % (disk['fs'], disk['path'],
                                     disk['status'])
            else:
                msg = "%s(%s)" % (disk['fs'], disk['msg'])
        else:
            if noOfMounts == 1:
                msg = "%s=%s" % (disk['fs'], disk['path'])
            else:
                msg = "%s" % (disk['path'])

        if disk['statusCode'] == utils.PluginStatusCode.CRITICAL or \
           inode['statusCode'] == utils.PluginStatusCode.CRITICAL:
            statusCode = utils.PluginStatusCode.CRITICAL
            critList.append(msg)
        elif (disk['statusCode'] == utils.PluginStatusCode.WARNING or
              inode['statusCode'] == utils.PluginStatusCode.WARNING):
            # if any previous disk statusCode is not critical
            # we should not change the statusCode into warning
            if statusCode != utils.PluginStatusCode.CRITICAL:
                statusCode = utils.PluginStatusCode.WARNING
            # just adding warning values into the list
            warnList.append(msg)
        elif disk['statusCode'] == utils.PluginStatusCode.OK:
            if statusCode == INVALID_STATUS_CODE or \
               statusCode == utils.PluginStatusCode.OK:
                statusCode = utils.PluginStatusCode.OK
            okList.append(msg)
        else:
            # added \ to fix E125 pep8 error
            if statusCode != utils.PluginStatusCode.CRITICAL or \
               statusCode != utils.PluginStatusCode.WARNING:
                statusCode = utils.PluginStatusCode.UNKNOWN
            okList.append(msg)

    msg = _getMsg(okList, warnList, critList)

    if totalUsed == 0 and totalSize == 0:
        # avoid zero div error
        return statusCode, "mount: %s" % msg, diskPerf
    if totalUsed == 0:
        # avoid zero div error
        totUsagePercent = 0
    elif len(mounts) > 1:
        totUsagePercent = totalUsed / totalSize * 100
    else:
        totUsagePercent = maxPercentUsed
    usageMsg = ""
    if not usage:
        totUsedSz, totUsedSzUnit = _getUnitAndType(totalUsed)
        totSpaceSz, totSpaceSzUnit = _getUnitAndType(totalSize)
        usageMsg = "%.1f%% used (%s%s out of %s%s)\n" % (totUsagePercent,
                                                         totUsedSz,
                                                         totUsedSzUnit,
                                                         totSpaceSz,
                                                         totSpaceSzUnit)
    else:
        usageMsg = "%.1f%% used (%s%s out of %s%s)\n" % (totUsagePercent,
                                                         totalUsed,
                                                         usage,
                                                         totalSize,
                                                         usage)

    if usageMsg:
        msg = "%s:mount(s): (%s)" % (usageMsg, msg)
    return statusCode, msg, diskPerf


if __name__ == '__main__':
    (options, args) = parse_input()

    if options.lvm:
        searchQuery = "/dev/mapper"
    else:
        searchQuery = "/"

    if not options.mountPath or options.lvm or options.all:
        options.mountPath += getMounts(searchQuery, options.exclude)

    statusCode, msg, diskPerf = showDiskUsage(options.warn,
                                              options.crit,
                                              options.mountPath,
                                              options.inode,
                                              options.usage,
                                              options.lvm,
                                              options.ignore)

    if utils.PluginStatusCode.CRITICAL == statusCode:
        sys.stdout.write("%s : %s | %s\n" % (
            utils.PluginStatus.CRITICAL,
            msg,
            " ".join(diskPerf)))
        sys.exit(utils.PluginStatusCode.CRITICAL)
    elif utils.PluginStatusCode.WARNING == statusCode:
        sys.stdout.write("%s : %s | %s\n" % (
            utils.PluginStatus.WARNING,
            msg,
            " ".join(diskPerf)))
        sys.exit(utils.PluginStatusCode.WARNING)
    else:
        sys.stdout.write("%s : %s | %s\n" % (
            utils.PluginStatus.OK,
            msg,
            " ".join(diskPerf)))
