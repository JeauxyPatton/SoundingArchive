"""
Authored by Joseph Patton (UMD/ESSIC/CISESS) on 9/12/2024
Last updated on 9/13/2024
Inspired by code from J. W. Thiesing III

Downloads and converts University of Wyoming archive sounding format to SHARPpy format.

WARNING: Station IDs are converted to Station numbers manually. Look for the Station_num section below
and add your radiosonde station to the list if it's not there already. You can use the U of Wyoming wesbite
(https://weather.uwyo.edu/upperair/sounding.html) to find the Station number.

Command line usage:
python3 download_WYO_sounding_convert_SHARPpy.py YYYYMMDDHHMM IDEN /path/to/output/dir/

"""

import numpy as np
import pandas as pd
import sys, requests
from datetime import datetime
from bs4 import BeautifulSoup

def downloadparse(requestdate, requestsite, station_ID):
	datestring = datetime.strftime(requestdate, "%Y%m%d%H%M")
	print('Requesting raw sounding data from the University of Wyoming archive for site ' + station_ID + ' at time ' + datestring)
	req_year = datetime.strftime(requestdate, "%Y")
	req_mnth = datetime.strftime(requestdate, "%m")
	req_dyhr = datetime.strftime(requestdate, "%d%H")
	url = f"http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR={req_year}&MONTH={req_mnth}&FROM={req_dyhr}&TO={req_dyhr}&STNM={requestsite}"
	data_raw = requests.get(url)
	if "Sorry" in data_raw.text:
		sys.exit(f"Download or parse failed. Exiting. URL: {url}")
	else:
		return data_raw.text

# Argument handling and variable initialization
args = sys.argv
if len(args) == 4:
	reqdate, site, outpath = args[1], args[2], args[3]
else:
	sys.exit("Incorrect number of arguments passed. Exiting.")

try:
	reqdate = datetime.strptime(reqdate, "%Y%m%d%H%M")
except:
	print("Incorrect date/time format.")

station_ID = site
if station_ID == 'KGSO':
	station_num = '72317'
if station_ID == 'KAMA':
	station_num = '72363'
if station_ID == 'KDDC':
	station_num = '72451'
if station_ID == 'KLIX':
	station_num = '72233'
if station_ID == 'KFWD':
	station_num = '72249'
if station_ID == 'KOUN':
	station_num = '72357'
if station_ID == 'KMAF':
	station_num = '72265'
if station_ID == 'KDRT':
	station_num = '72261'
if station_ID == 'KSHV':
	station_num = '72248'
if station_ID == 'KJAN':
	station_num = '72235'

# Load and parse data
data = downloadparse(reqdate, station_num, station_ID)

soup = BeautifulSoup(data, 'html.parser')
data_text = soup.get_text()
data_text_lines = data_text.splitlines()

print('The raw sounding data is: ')
print(data_text)

sounding_data_array = []
lines_done = 0
for row in data_text_lines:
 	#print('Now parsing row: ' + row)
 	lines_done += 1
 	if lines_done < 4:
 		continue
 	else:
 		if lines_done == 4:
 			short_station_ID = row[6:9]
 			print('The station is: ' + short_station_ID)
 	if lines_done > 10:
 		sounding_ob = row.split()
 		if sounding_ob[0] == 'Station':
 			print('Reached end of file with no errors.')
 			break
 		if len(sounding_ob) < 11:
 			pres = sounding_ob[0]
 			print('Missing data at pressure level: ' + pres)
 			break
 		pres = float(sounding_ob[0])
 		hgt = float(sounding_ob[1])
 		temp = float(sounding_ob[2])
 		dwpt = float(sounding_ob[3])
 		relh = float(sounding_ob[4])
 		mixr = float(sounding_ob[5])
 		winddrct = float(sounding_ob[6])
 		windspd = float(sounding_ob[7])
 		thta = float(sounding_ob[8])
 		thte = float(sounding_ob[9])
 		thtv = float(sounding_ob[10])

 		new_sounding_ob = [pres, hgt, temp, dwpt, winddrct, windspd]
 		sounding_data_array.append(new_sounding_ob)

print("Writing sounding data in SHARPpy format.")
outfile = open(outpath + reqdate.strftime("%y%m%d%H") + "." + short_station_ID, 'w')
outfile.write("%TITLE%\n")
title_date = reqdate.strftime("%y%m%d/%H%M")
outfile.write(" " + short_station_ID + "   " + title_date + "\n")
outfile.write("\n")
outfile.write("   LEVEL       HGHT       TEMP       DWPT       WDIR       WSPD\n")
outfile.write("-------------------------------------------------------------------\n")
outfile.write("%RAW%\n")
for line in sounding_data_array:
	pres, hgt, temp, dwpt, wdir, wspd = line[:]
	pres_str = f'{pres:.2f},    '
	hgt_str = f'{hgt:.2f},    '
	temp_str = f'{temp:.2f},    '
	dwpt_str = f'{dwpt:.2f},    '
	wdir_str = f'{wdir:.2f},    '
	wspd_str = f'{wspd:.2f}'
	new_ob_line = " " + pres_str + hgt_str + temp_str + dwpt_str + wdir_str + wspd_str + "\n"
	outfile.write(new_ob_line)
outfile.write("%END%")
outfile.close()
