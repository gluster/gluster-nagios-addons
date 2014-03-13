#!/usr/bin/python
# sadf.py -- nagios plugin uses sadf output for perf data
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
import commands
from optparse import OptionParser


def getUsageAndFree(command, lvm):
    status = commands.getstatusoutput(command)[1].split()
    path = status[-1]
    usagePer = status[-2]
    availSpace = status[-3]
    usedSpace = status[-4]
    device = status[-6].split("-")[-1]
    dmatch = re.compile('[0-9]+').match(usagePer)
    if (dmatch):
        usage = eval(dmatch.group(0))
        return (float(usage), float(100 - usage), usedSpace,
                availSpace, device, path)
    else:
        return None, None, None, None, None, None


def getDisk(path, readable=False, lvm=False):
    if readable:
        return getUsageAndFree("df -m %s" % path, lvm)
    else:
        return getUsageAndFree("df -kh %s" % path, lvm)


def getInode(path, readable=False, lvm=False):
    return getUsageAndFree("df -i %s" % path, lvm)


def appendStatus(lst, level, typ, device, mpath, usage):
    if 2 == level:
        level = "crit"
    elif 1 == level:
        level = "warn"
    else:
        level = "ok"
    lst.append("%s:%s:%s;%s;%s" % (level, device, mpath, usage))


def getMounts(searchQuery=None, excludeList=[]):
    mountPaths = []
    f = open("/etc/mtab")
    for i in f.readlines():
        if searchQuery and i.startswith(searchQuery):
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
                      dest='warn', help='Warning count in %', default=80)
    parser.add_option('-c', '--critical', action='store', type='int',
                      dest='crit', help='Critical count in %', default=90)
    parser.add_option('-u', '--usage', action="store_true", dest='usage',
                      help='Output disk and inode usage', default=False)
    parser.add_option('-l', '--lvm', action="store_true",
                      dest='lvm', help='List lvm mounts', default=False)
    parser.add_option('-a', '--all', action="store_true",
                      dest='all', help='List all mounts', default=False)
    parser.add_option('-n', '--ignore', action="store_true",
                      dest='ignore', help='Ignore errors', default=False)
    parser.add_option('-i', '--include', action='append', type='string',
                      dest='mountPath', help='Mount path', default=[])
    parser.add_option('-x', '--exclude', action="append", type='string',
                      dest='exclude', help='Exclude disk')
    return parser.parse_args()


if __name__ == '__main__':
    disk = []
    warnList = []
    critList = []
    diskList = []
    mounts = []
    level = -1
    (options, args) = parse_input()

    if len(args) > 2:
        if args[0].isdigit() and args[1].isdigit():
            warn = int(args[0])
            crit = int(args[1])
            options.mountPath = args[2:]
        else:
            warn = 80
            crit = 90
            options.mountPath = args
    else:
        crit = options.crit
        warn = options.warn

    if options.lvm:
        searchQuery = "/dev/mapper"
    elif options.all:
        searchQuery = None
    else:
        searchQuery = "/"

    if not options.mountPath or options.lvm or options.all:
        options.mountPath += getMounts(searchQuery, options.exclude)

    #if not options.mountPath:
    #    parser.print_help()
    #    sys.exit(1)

    for path in options.mountPath:
        diskUsage, diskFree, used, avail, dev, mpath = getDisk(path,
                                                               options.usage,
                                                               options.lvm)
        inodeUsage, inodeFree, iused, iavail, idev, ipath = getInode(
            path,
            options.usage,
            options.lvm)
        if mpath in mounts:
            continue
        if not used or not iused:
            if options.ignore:
                continue
            else:
                sys.exit(3)

        mounts.append(mpath)
        if options.usage:
            total = (float(used) + float(avail)) / 1000
            itot = (float(iused) + float(iavail)) / 1000
            disk.append("%s=%.1f;%.1f;%.1f;0;%.1f %s=%.1f;%.1f;%.1f;0;%.1f" % (
                mpath, float(used)/1000, warn*total/100, crit*total/100, total,
                ipath, float(iused)/1000, warn*itot/100, crit*itot/100, itot))
        else:
            disk.append("%s=%.2f;%s;%s;0;100 %s=%.2f;%s;%s;0;100" % (
                mpath, diskUsage, warn, crit, ipath, inodeUsage, warn, crit))

        if diskUsage >= crit or inodeUsage >= crit:
            if diskUsage >= crit:
                critList.append("crit:disk:%s;%s;%s" % (dev, mpath, diskUsage))
            else:
                critList.append("crit:inode:%s;%s;%s" % (idev, ipath,
                                                         inodeUsage))
            if not level > 1:
                level = 2
        elif (diskUsage >= warn and diskUsage < crit) or (
                inodeUsage >= warn and inodeUsage < crit):
            if diskUsage >= warn:
                warnList.append("warn:disk:%s;%s;%s" % (dev, mpath, diskUsage))
            else:
                warnList.append("warn:inode:%s;%s;%s" % (idev, ipath,
                                                         inodeUsage))
            if not level > 0:
                level = 1
        else:
            diskList.append("%s:%s" % (dev, mpath))

    msg = " ".join(critList + warnList)
    if not msg:
        msg += " disks:mounts:(" + ",".join(diskList) + ")"

    if 2 == level:
        print "CRITICAL : %s | %s" % (msg, " ".join(disk))
        sys.exit(2)
    elif 1 == level:
        print "WARNING : %s | %s" % (msg, " ".join(disk))
        sys.exit(1)
    else:
        print "OK : %s | %s" % (msg, " ".join(disk))
