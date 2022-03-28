import glob
import re
import pathlib
import os
import subprocess
import sys
from multiprocessing import Pool
import multiprocessing
import time
import csv
import pathlib as path
# import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET

try:
    time.clock()
except:
    time.process_time()

fileLoc_str = sys.argv[1]
fileloc = pathlib.Path(sys.argv[1])
extrLoc = pathlib.Path(sys.argv[2])
imextXML = pathlib.Path(sys.argv[3])
# name_format = sys.argv[4]
Console = sys.argv[4]
process = int(sys.argv[5])
CSV_check = int(sys.argv[6])
# print(Console)


def parprocfun(file):

    destLoc = path.Path(extrLoc)

    if CSV_check:
        csv_data    = file.split(',')
        temp_file   = csv_data[5] + '\\' + csv_data[6] + '.log'
        log_name = csv_data[6]
        file_path   = path.Path(temp_file)
        start_time  = csv_data[8]
        stop_time   = csv_data[9]
        logger_name = csv_data[12]
    else:
        file_path = path.Path(file)

    # This creates the a new directory reference and this will be called.
    # newdir = destLoc / file_path.parent.name / file_path.stem
    # print(f"The new directory generated = {str(newdir)}")

    newdir = destLoc / file_path.stem

    if not os.path.exists(newdir):
        print(f"{datetime.now().strftime('%m/%d/%Y %H:%M:%S')} : Running for file {file}")

        # Creating a unique folder for each log. This also prevents any issues with folder duplicates.
        if CSV_check:
            pathlib.Path(newdir).mkdir(parents=True, exist_ok=True)
        else:
            # folder_temp = destLoc / file_path.parent.name
            # pathlib.Path(folder_temp).mkdir(parents=True, exist_ok=True)
            image_dest = newdir / 'Images'
            pathlib.Path(image_dest).mkdir(parents=True, exist_ok=True)

            logExtractor_dest = newdir / 'LogExtractor'
            pathlib.Path(logExtractor_dest).mkdir(parents=True, exist_ok=True)

            canLog_dest = newdir / 'CanLog'
            pathlib.Path(canLog_dest).mkdir(parents=True, exist_ok=True)

            tree = ET.parse(imextXML)
            root = tree.getroot()

            for plugin in root.iter('plugin'):
                if plugin.attrib['name'] == 'Log Player0':
                    # print(plugin.attrib['type'])
                    for lev in plugin:
                        if lev.tag =='logName':
                            lev.text = str(file_path).replace('\\', '/')
                            # print(lev.tag, lev.text)
                if plugin.attrib['name'] == 'Log Extractor0':
                    # print(plugin.attrib['type'])
                    for lev in plugin:
                        if lev.tag =='defaultDirectoryPath':
                            lev.text = str(logExtractor_dest).replace('\\', '/')
                            # print(lev.tag, lev.text)
                if plugin.attrib['name'] == 'Image Extractor':
                    # print(plugin.attrib['type'])
                    for lev in plugin:
                        if lev.tag =='directoryPath':
                            lev.text = str(image_dest).replace('\\', '/')
                            # print(lev.tag, lev.text)
                if plugin.attrib['name'] == 'CAN Extractor0':
                    # print(plugin.attrib['type'])
                    for lev in plugin:
                        if lev.tag =='defaultDirectoryPath':
                            lev.text = str(canLog_dest).replace('\\', '/')
                            # print(lev.tag, lev.text)

            try:
                temp_time = time.clock()
            except:
                temp_time = time.process_time()

            # Creating a temporary XML file with CPU runtime to prevent overwrite
            imextXML_temp = imextXML.stem + '_' + str((int(temp_time * 100000))) + '.xml'

            # Creating the cleaned version of the temp_path
            temp_path = path.Path(imextXML_temp)
            temp_path = temp_path.absolute()
            temp_path_str = str(temp_path).replace('\\', '/')

            # print(ET.tostring(root, encoding='utf8').decode('utf8'))
            # Creating the local copy of the modified XML
            # tree.write(imextXML_temp, encoding="utf-8", xml_declaration=True)

            with open(imextXML_temp, "w", encoding='UTF-8') as xf:
                doc_type = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE RoboticsSystem>'
                tostring = ET.tostring(root).decode('utf-8')
                file = f"{doc_type}{tostring}"
                xf.write(file)

            # # do something with the updated line
            with open(os.devnull, 'w') as FNULL:
                # print([Console, str(temp_path_str)])
                subprocess.call([Console, str(temp_path_str)], stdout=FNULL, stderr=FNULL, shell=False)

            # Removing the temporarily created XML file.
            os.remove(imextXML_temp)

        # print(f'The folder for {file} already exists.')

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)


if __name__ == "__main__":
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()
    # starting time
    start = time.time()
    # print("The program has started")
    print(f"The number of multi process enabled : {process} ")
    print(fileloc)
    if CSV_check == 1:
        print("Processing from CSV")
        files = []
        s = ","
        with open(fileloc, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
        data.pop(0)
        for line in data:
            files.append(s.join(line))
    else:
        files = glob.glob(fileLoc_str + r'\**\*.log', recursive=True)
    # print(files)
    with Pool(int(process)) as p:
        time.sleep(0.25)
        p.map(parprocfun, files)

    # end time
    end = time.time()

    # total time taken
    print(f"Runtime of the program is {convert(end - start)}")