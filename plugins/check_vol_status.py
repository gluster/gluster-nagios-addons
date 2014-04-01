#!/usr/bin/python

import re
import argparse
import commands
import xml.etree.ElementTree as ET
from glusternagios import utils
import nscautils


def parseXml(xmldoc, searchStr):
    root = ET.fromstring(xmldoc)
    #statusStr = root.findall("./volInfo/volumes/volume/bricks/brick")
    statusStr = root.findall(searchStr)
    return statusStr


def getVolumeStatus(vol_status_out):
    xmlElemList = parseXml(vol_status_out, "./opRet")
    #print xmlElemList[0].text
    if xmlElemList[0].text == "0":
        #print "Started"
        vol_status = "Started"
    else:
        #print "Stopped"
        vol_status = "Stopped"
    return vol_status


def showBrickStatus(vol_status_out):
    ipPat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    xmlElemList = []
    brickName = ""
    #brickStatus = ""
    exitStatus = utils.PluginStatusCode.OK
    resultString = ""
    brickIP = ""
    vol_status = getVolumeStatus(vol_status_out)
    if vol_status == "Started":
        xmlElemList = parseXml(vol_status_out,
                               "./volStatus/volumes/volume/node")
        for node in xmlElemList:
            if ipPat.match(node.find('hostname').text):
                brickIP = node.find('hostname').text
                brickName = "Brick-"
                brickName += brickIP
                brickName += ":"
                brickName += node.find('path').text
                brickName += "-Status"
                #print brickName
                if node.find('status').text == "1":
                    exitStatus = utils.PluginStatusCode.OK
                    resultString = "Brick Status: OK"
                else:
                    exitStatus = utils.PluginStatusCode.CRITICAL
                    resultString = "Brick Status: CRITICAL"
                nscautils.send_to_nsca(brickIP,
                                       brickName,
                                       exitStatus,
                                       resultString)


def showVolumeStatus(vol_status_out, volName, clusterName):
    xmlElemList = []
    no_of_bricks = 0
    brick_online = 0
    brick_offline = 0
    #brick_list = []
    resultString = ""
    exitStatus = utils.PluginStatusCode.OK
    serviceName = nscautils.vol_service_name(volName)
    ipPat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    vol_status = getVolumeStatus(vol_status_out)
    if vol_status == "Started":
        xmlElemList = parseXml(vol_status_out,
                               "./volStatus/volumes/volume/node")
        for node in xmlElemList:
            if ipPat.match(node.find('hostname').text):
                #brick_list.insert(0,node.find('hostname').text)
                no_of_bricks += 1
                if node.find('status').text == "1":
                    brick_online += 1
                else:
                    brick_offline += 1
        #no_of_bricks = len(brick_list)
        #print len(brick_list)

    if vol_status != "Started":
        resultString = "Volume Status CRITICAL: Volume Stopped Total" \
                       " Bricks: %s|Bricks Online=%s" % (no_of_bricks,
                                                         brick_online)
        exitStatus = utils.PluginStatusCode.CRITICAL
    elif brick_offline == no_of_bricks:
        resultString = "Volume Status CRITICAL: All Bricks are Down Total" \
                       " Bricks: %s|Bricks Online=%s" % (no_of_bricks,
                                                         brick_online)
        exitStatus = utils.PluginStatusCode.CRITICAL
    elif brick_online != no_of_bricks:
        resultString = "Volume Status WARNING: Some Bricks are Down Total" \
                       " Bricks: %s|Bricks Online=%s" % (no_of_bricks,
                                                         brick_online)
        exitStatus = utils.PluginStatusCode.WARNING
    else:
        resultString = "Volume Status OK: Total" \
                       " Bricks: %s|Bricks Online=%s" % (no_of_bricks,
                                                         brick_online)
        exitStatus = utils.PluginStatusCode.OK

    nscautils.send_to_nsca(clusterName, serviceName, exitStatus, resultString)


def parse_input():

    parser = argparse.ArgumentParser(usage='%(prog)s [-h] <volume> <cluster>')
    parser.add_argument("volume", help="Name of the volume to get the Status")
    parser.add_argument("cluster",
                        help="Name of the cluster, volume belongs to")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_input()
    #Get the volume status
    command_vol_status = "sudo gluster volume status " + args.volume + " --xml"
    vol_status_out = commands.getoutput(command_vol_status)
    showVolumeStatus(vol_status_out, args.volume, args.cluster)
    showBrickStatus(vol_status_out)
