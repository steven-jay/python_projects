import subprocess
import os
import re
from configparser import ConfigParser


def getImportedFiles(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            # used to remove duplicates ending with _1.dav, _2.dav etc.
            regex = r"_[0-9]\.dav$"
            if '.dav' in file and re.search(regex, file) is None:
                files.append(os.path.join(r, file))
    return files


def convertFiles(files, convertPath):
    convertedFiles = []
    for file in files:
        splitFilename = file.split("/")
        fileWithoutPath = dropDav(splitFilename[len(splitFilename)-1])
        newFilename = convertPath + fileWithoutPath + '.mp4'
        if checkFile(newFilename) == False:
            bashCommand = f'ffmpeg -i {file} {newFilename}'
            subprocess.run(bashCommand, shell=True, capture_output=True)
        convertedFiles.append(newFilename)
    print('Successfully converted all files')
    return convertedFiles


def checkFile(file):
    print(f'Checking existence of file: {file}')
    if os.path.exists(file):
        return True
    else:
        return False


def splitFilename(file):
    return file.split("_")


def dropDav(file):
    return file.replace('.dav', '')


def dropMp4(file):
    return file.replace('.mp4', '')


# Compare end timestamp with beginning timestamp of next file
# If they match, group them so that they can be concatenated
def groupFiles(files):
    group = []
    subgroup = []
    for i, file in enumerate(files):
        if i != len(files)-1:
            startTimestamp = splitFilename(files[i+1])[3].strip()
            endTimestamp = dropMp4(splitFilename(files[i])[4].strip())
            if len(subgroup) == 0:
                if startTimestamp == endTimestamp:
                    subgroup.append(file)
                else:
                    next
            else:
                if startTimestamp == endTimestamp:
                    subgroup.append(file)
                else:
                    subgroup.append(file)
                    group.append(subgroup)
                    subgroup = []
    return group


def readableTimestamp(timestamp):
    return str(timestamp[0:8]) + '_' + str(timestamp[8:])


def mergeGroup(groupedFiles, mergePath):
    for i, group in enumerate(groupedFiles):
        with open('temp.txt', 'w') as f:
            for i, file in enumerate(group):
                if i == 0:
                    startTimestamp = readableTimestamp(
                        splitFilename(file)[3].strip())
                if i == len(group) - 1:
                    endTimestamp = readableTimestamp(
                        dropMp4(splitFilename(file)[4].strip()))
                f.write(f'file \'{file}\'\n')
            f.close()
        fileName = mergePath + startTimestamp + '_' + endTimestamp
        bashCommand = f'ffmpeg -f concat -safe 0 -i temp.txt -c copy {fileName}.mp4\n'
        print(
            f'Running following command: ffmpeg -f concat -safe 0 -i temp.txt -c copy {fileName}.mp4')
        subprocess.run(bashCommand, shell=True)
        subprocess.run('rm temp.txt', shell=True)


def getPaths(config):
    parser = ConfigParser()
    parser.read(config)
    importPath = parser['PATHS']['importPath']
    convertPath = parser['PATHS']['convertPath']
    mergePath = parser['PATHS']['mergePath']
    return {'importPath': importPath, 'convertPath': convertPath, 'mergePath': mergePath}


paths = getPaths('config.ini')
importedFiles = getImportedFiles(paths['importPath'])
convertedFiles = convertFiles(importedFiles, paths['convertPath'])
sortedFiles = sorted(convertedFiles)
groupedFiles = groupFiles(sortedFiles)
mergeGroup(groupedFiles, paths['mergePath'])
