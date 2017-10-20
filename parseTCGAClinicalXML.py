#test parsing tcga clinical xml

import xml.etree.ElementTree as ET
import csv

#parse XML node tag to easily readable text
def parseTag(tag):
    tagElements = tag.strip().split('}')
    return tagElements[1]

#get clinical information from a TCGA clinical xml file
def getClinicalInfo(xmlPath):
    tree = ET.parse(xmlPath)
    root = tree.getroot()
    clinicalDictionary = dict()
    for child in root:
        if parseTag(child.tag) == 'patient':
            for grandchild in child:
                if len(list(grandchild)) == 0:
                    clinicalDictionary[parseTag(grandchild.tag)] = grandchild.text
    return clinicalDictionary

#write clincal information from multiple TCGA clinical xml files to csv format
def parseTCGAClinicalXML(outputcsv, xmlPathList):
    clinicalList = list()
    labelSet = set()
    for path in xmlPathList:
        clinicalDict = getClinicalInfo(path)
        clinicalList.append(clinicalDict)
        labelSet = labelSet.union(set(clinicalDict.keys()))
    with open(outputcsv, 'w') as csvfile:
       fieldnames = sorted(list(labelSet))
       writer = csv.DictWriter(csvfile, fieldnames)
       writer.writeheader()
       for line in clinicalList:
           writer.writerow(line)
    
#read TCGA clinical xml file paths from a text file and creat a clincal csv file from these xml files
def parseTCGAClinicalXMLfromPathFile(outputcsv, pathfile):
    paths = open(pathfile, 'r')
    pathList = list()
    for path in paths:
        pathList.append(path.strip())
    parseTCGAClinicalXML(outputcsv, pathList)

if __name__ == "__main__":
    import sys
    parseTCGAClinicalXMLfromPathFile(str(sys.argv[1]), str(sys.argv[2]))