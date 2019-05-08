#test parsing tcga clinical xml

import xml.etree.ElementTree as ET
import csv
import unicodedata

#parse XML node tag to easily readable text
def parseTag(tag):
    tagElements = tag.strip().split('}')
    return tagElements[1]

#test if a string can be converted to integer
def isInt(x):
    try:
        a = int(x)
    except ValueError:
        return False
    else:
        return True

#get clinical information from a TCGA clinical xml file
def getPatientInfo(xmlPath):
    tree = ET.parse(xmlPath)
    root = tree.getroot()
    clinicalDictionary = dict()
    for child in root:
        if parseTag(child.tag) == 'patient':
            for grandchild in child:
                if len(list(grandchild)) == 0:
                    value = unicode(grandchild.text)
                    clinicalDictionary[parseTag(grandchild.tag)] = value.encode('ascii', 'ignore')
    return clinicalDictionary

def getFollowupInfo(xmlPath):
    tree = ET.parse(xmlPath)
    root = tree.getroot()
    followupDictionary = dict()
    followupDictionaryList = list()
    for child in root:
        if parseTag(child.tag) == 'patient':
            for grandchild in child:
                if parseTag(grandchild.tag) == 'follow_ups':
                    followups = list(grandchild)
                    for followup in followups:
                        for followupFields in followup:
                            value = unicode(followupFields.text)
                            followupDictionary[parseTag(followupFields.tag)] = value.encode('ascii', 'ignore')
                        followupDictionaryList.append(followupDictionary)
                        followupDictionary = dict()
    return followupDictionaryList

#construct survival dictionary list
def constructSuvivalDictionary(clinicalList, followupList):
    survivalDictDictionary = dict()
    survivalDictionary = dict()
    for clinical in clinicalList:
        survivalDictionary['bcr_patient_barcode'] = clinical['bcr_patient_barcode']
        try:
            survivalDictionary['vital_status'] =  clinical['vital_status']
        except:
            survivalDictionary['vital_status'] = 'Unknown'
        if survivalDictionary['vital_status'] == 'Alive':
            survivalDictionary['survival'] = clinical['days_to_last_followup']
        elif survivalDictionary['vital_status'] == 'Dead':
            survivalDictionary['survival'] = clinical['days_to_death']
        else:
            try:
                survivalDictionary['survival'] = clinical['days_to_last_followup']
            except:
                survivalDictionary['survival'] = 'Unknown'
        survivalDictDictionary[survivalDictionary['bcr_patient_barcode']] = survivalDictionary
        survivalDictionary = dict()
    for followup in followupList:
        barcode = followup['bcr_followup_barcode'][0:12]
        clinical = survivalDictDictionary[barcode]
        if clinical['vital_status'] != followup['vital_status']:
            if followup['vital_status'] == 'Dead':
                survivalDictDictionary[barcode]['vital_status'] = 'Dead'
            if clinical['vital_status'] == 'None':
                survivalDictDictionary[barcode]['vital_status'] = followup['vital_status']
        if followup['vital_status'] == 'Dead':
            if isInt(followup['days_to_death']):
                survivalDictDictionary[barcode]['survival'] = int(followup['days_to_death'])
        elif followup['vital_status'] == 'Alive':
            if isInt(clinical['survival']) and isInt(followup['days_to_last_followup']):
                survivalDictDictionary[barcode]['survival'] = max(int(clinical['survival']), int(followup['days_to_last_followup']))
            elif isInt(followup['days_to_last_followup']):
                survivalDictDictionary[barcode]['survival'] = int(followup['days_to_last_followup'])
    return survivalDictDictionary



#write clincal information from multiple TCGA clinical xml files to csv format
def parseTCGAXML(outputcsv, xmlPathList, type):
    clinicalList = list()
    labelSet = set()
    if(type == 'patient'):
        for path in xmlPathList:
            clinicalDict = getPatientInfo(path)
            clinicalList.append(clinicalDict)
            labelSet = labelSet.union(set(clinicalDict.keys()))
    elif(type == 'followup'):
        for path in xmlPathList:
            followupDicts = getFollowupInfo(path)
            clinicalList = clinicalList + followupDicts
            for followupDict in followupDicts:
                labelSet = labelSet.union(set(followupDict.keys()))
    with open(outputcsv, 'w') as csvfile:
       fieldnames = sorted(list(labelSet))
       writer = csv.DictWriter(csvfile, fieldnames)
       writer.writeheader()
       for line in clinicalList:
           writer.writerow(line)

def parseTCGAXMLSurvival(outputcsv, xmlPathList):
    clinicalList = list()
    followupList = list()
    for path in xmlPathList:
        clinicalList.append(getPatientInfo(path))
        followupList = followupList + getFollowupInfo(path)
    survivalDictionary = constructSuvivalDictionary(clinicalList, followupList)
    with open(outputcsv, 'w') as csvfile:
        fieldnames = ['bcr_patient_barcode', 'vital_status', 'survival']
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        for key in survivalDictionary:
            writer.writerow(survivalDictionary[key])

   
#read TCGA clinical xml file paths from a text file and creat a clincal csv file from these xml files
def parseTCGAXMLfromPathFile(outputcsv, pathfile, type):
    paths = open(pathfile, 'r')
    pathList = list()
    for path in paths:
        pathList.append(path.strip())
    if type == 'patient' or type == 'followup':
        parseTCGAXML(outputcsv, pathList, type)
    elif type == 'survival':
        parseTCGAXMLSurvival(outputcsv, pathList)
    

if __name__ == "__main__":
   import sys
   parseTCGAXMLfromPathFile(str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3]))
