#encoding: utf-8
#
# RSA Mass Triage (RMT)
# RSA Incident Response firstresponse@rsa.com incidentresponse.rsa.com
#
# TODO
# Cleanup? (delete file after parsing?)
# Further NTUSER.DAT Parsing.
# Further USERCLASS.DAT Parsing
# Rework csv format (headings/columns)
# Superfetch?
# SRUM?
# Speed up amcache parsing
#
# Change Log
# .1 3May2016 
#	Initial Development
# .2 23Jan2017
#	Changed Shimcache/Amcache parsing to append to csv after each file is parsed instead of all at once.
# .3 27Jan2017
#	Added JobParsing using jobparser.py
# .4 30Jan2017
#	Fixed RecentFileCache parsing
#	Added ability to overwrite output instead of append
# .5 30Jan2017
#	Changed to use Will Ballethin's amcache.py instead of built in logic.
# .6 15Feb2017
#	NTUSER.DAT User Assist
# .7 24April2017
#	Cleaned up some code errors
#	Added todo for adding option to delete file after parsing
# .8 11Oct2017
#	Change overwrite behavior to be default and append to be option.
# .9 05April2018
# 	Fixed issues with -m Muicache Parsing

from __future__ import unicode_literals

import argparse
import csv
import datetime
import io
import os
import struct
import sys
import unicodecsv
from collections import namedtuple

try:
	import ShimCacheParser
except ImportError:
	print('This script requires ShimCacheParser.py in the same path -- https://github.com/mandiant/ShimCacheParser')
	quit()
	
try:
	from Registry import Registry
except ImportError:
	print('This script requires python-registry Registry Directory in the same path: https://github.com/williballenthin/python-registry')
	quit()

try:
	from jobparser import Job
except ImportError:
	print('This script requires jobparser.py in the same path -- https://raw.githubusercontent.com/gleeda/misc-scripts/master/misc_python/jobparser.py')
	quit()

try:
	from prefetch import Prefetch
except ImportError:
	print('This script requires prefetch.py in the same path -- https://raw.githubusercontent.com/PoorBillionaire/Windows-Prefetch-Parser/master/windowsprefetch/prefetch.py')
	quit()

try:
	import amcache
except ImportError:
	print('This script requires amcache.py in the same path -- https://raw.githubusercontent.com/williballenthin/python-registry/master/samples/amcache.py')
	quit()

from jinja2 import Template, Environment, PackageLoader

try:
	import userassist
except ImportError:
	print('This script requires userassist.py in the same path as well as its dependancies to be installed -- https://raw.githubusercontent.com/sysforensics/python-regparse/master/plugins/userassist.py')
	quit()
	
try:
	import muicache
except ImportError:
	print('This script requires muicache.py in the same path -- https://raw.githubusercontent.com/timetology/registry/master/muicache.py')
	quit()

DATE_ISO = "%Y-%m-%d %H:%M:%S"
ShimCacheParser.g_timeformat = DATE_ISO
UNIX_TIMESTAMP_ZERO = amcache.parse_unix_timestamp(0)
WINDOWS_TIMESTAMP_ZERO = amcache.parse_windows_timestamp(0)
g_debug = False
g_outputfile = ''
g_overwrite = False

def getTotalFilesStartsWith(path, file_prefix):
	counter = 0
	for filename in TraversePath(path):
		fname = os.path.split(filename)[1]
		if fname.lower().startswith(file_prefix): 
			counter += 1
	return counter

def TraversePath(directory):
	for dirpath,_,filenames in os.walk(directory):
		for f in filenames:
			yield os.path.abspath(os.path.join(dirpath, f))

def getTotalFilesIn(match,path):
	total_files = 0
	for filename in TraversePath(path):
		fname = os.path.split(filename)[1]
		if match in fname.lower(): 
			total_files += 1
	return total_files

def getHostnameFromFilename(fname):
	#Get hostname from ECAT style Filename (e.g. Amcache_HOSTNAME_a65a302f04394842611b5def9871790e1dd1524a9227af2c4aca667f5a6775d3_21470nm)
	#Mofify this if your hostname is stored in the filename in a different format
	parts = fname.split('_')
	if len(parts) > 4 and len(parts[2]) == 64:
		return parts[1]
	else:
		if g_debug:
			print('[!] Error. Hostname not found in filename.')
		return 'N/A'

def write_line(data):
	try:
		fh = io.open(g_outputfile, 'a+', encoding='utf-8')
	except IOError as err:
		print('[-] Error opening output file: {}'.format(err))
		return
	else:
		fh.write(data + '\n')
	
def write_amcache(data):
	with io.open(g_outputfile, 'a+', encoding='utf-8') as f:
		for i in data:
			f.write(i + '\n')
	
		
def write_output(data):
	with open(g_outputfile, 'ab+') as f:
            csv_writer = unicodecsv.writer(f, encoding='utf-8')
            for i in data:
                #csv_writer.writerow(i.decode('utf-8') )
				#print i
				csv_writer.writerow(i)
	return


def RegistryGetHostname(hive):
	""" Parse a given SYSTEM registry hive to acquire system host name.
		Parses both ControlSet in case of name change.

	Args:
		hive: String of filename to parse.

	Returns:
		String of hostnames, or hostnames
	"""
	name1 = name2 = ''
	try:
		reg = Registry.Registry(hive)
	except Registry.RegistryParse.ParseException as err:
		print('[!] Error: {}'.format(err))
		return ''
	
	top_lvl = reg.root().subkeys()
	
	try:
		for key in top_lvl:
			if 'ControlSet' in key.name():
				cname = reg.open('{}\\Control\ComputerName'.format(key.name()))
				for subkey in cname.subkeys():
					if key.name() == 'ControlSet001':
						name1 = str(subkey['ComputerName'].value())
					elif key.name() == 'ControlSet002':
						name2 = str(subkey['ComputerName'].value()) 
					# Technically could incude ControlSet003 here, even 004.		 
	except:
		return ''

	if (name1 == name2) or not name2:
		return name1
	else:
		print("Hostname Change: {} == {}".format(name1, name2))
		return '{}_{}'.format(name1, name2)

def convert_win_timestamp(timestamp):
	epoch_start = datetime.datetime(year=1601, month=1,day=1)
	seconds_since_epoch = timestamp/10**7
	return (epoch_start + datetime.timedelta(seconds=seconds_since_epoch)).strftime(DATE_ISO)

def find_vol_guids_in_SYSTEM(SYSTEM_file):
	guid_list = list()
	registryBase_system_vol_guids = 'MountedDevices'

	try:
		Hive_SYSTEM = Registry.Registry(SYSTEM_file)
	except Registry.RegistryParse.ParseException as err:
		print('[!] find_vol_guids_in_SYSTEM() Error in parsing file: {}'.format(SYSTEM_file))
		print('[!] find_vol_guids_in_SYSTEM() Error given: {}'.format(err))
		return False

	
	SYSTEM_vol_root = Hive_SYSTEM.open(registryBase_system_vol_guids)
	for root_values in SYSTEM_vol_root.values():
		guid_system = root_values.name().strip('\\??\\Volume{').strip('}').strip('#{')
		if not guid_system.startswith('DosDevices'):
			guid_list.append(guid_system)
	return guid_list


# Source: http://www.swiftforensics.com/2013/12/amcachehve-in-windows-8-goldmine-for.html
#+-------+-----------------------------------------+-------------------+
#| Value |				Description				|	 Data Type	 |
#+-------+-----------------------------------------+-------------------+
#| 0	 | Product Name							| UNICODE string	|
#| 1	 | Company Name							| UNICODE string	|
#| 2	 | File version number only				| UNICODE string	|
#| 3	 | Language code (1033 for en-US)		  | DWORD			 |
#| 4	 | SwitchBackContext						| QWORD			 |
#| 5	 | File Version							| UNICODE string	|
#| 6	 | File Size (in bytes)					| DWORD			 |
#| 7	 | PE Header field - SizeOfImage			| DWORD			 |
#| 8	 | Hash of PE Header (unknown algorithm)	| UNICODE string	|
#| 9	 | PE Header field - Checksum			  | DWORD			 |
#| a	 | Unknown								 | QWORD			 |
#| b	 | Unknown								 | QWORD			 |
#| c	 | File Description						| UNICODE string	|
#| d	 | Unknown, maybe Major & Minor OS version | DWORD			 |
#| f	 | Linker (Compile time) Timestamp		 | DWORD - Unix time |
#| 10	| Unknown								 | DWORD			 |
#| 11	| Last Modified Timestamp				 | FILETIME		  |
#| 12	| Created Timestamp						| FILETIME		  |
#| 15	| Full path to file						| UNICODE string	|
#| 16	| Unknown								 | DWORD			 |
#| 17	| Last Modified Timestamp 2				| FILETIME		  |
#| 100	| Program ID							  | UNICODE string	|
#| 101	| SHA1 hash of file						| UNICODE string	|
#+-------+-----------------------------------------+-------------------+
#
def amcache_retrieve_results(hostname, Hive_Amcache):
	registryBase_amcache_programs = 'Root\\File'
	Amcache_prog_root = Hive_Amcache.open(registryBase_amcache_programs)
	entries = list()

	for volume in Amcache_prog_root.subkeys():
		try:
			for exe_id in volume.subkeys():
				path = sha1 = ''
				size = created = modified1 = modified2 = 0
				for field in exe_id.values():
					if field.name() == '15':	path = field.value()
					elif field.name() == '6':	size = field.value()
					elif field.name() == '12':  convert_win_timestamp(field.value())
					elif field.name() == '11':  modified1 = convert_win_timestamp(field.value())
					elif field.name() == '17':  modified2 = convert_win_timestamp(field.value())
					elif field.name() == '101': sha1 = field.value()

					if path and (created or modified1 or modified2):
						if 'dll' not in path:
							#hostname,Last Modified,Last Update,File Path,File Size,Shimcache Exec Flag,SHA1 Hash,Data Source
							#entries.append((hostname, modified2, 'N/A', path, size, 'N/A', sha1, 'shimcache'))
							entries.append('{},{},{},{},{},{},{},{}'.format(hostname, modified2, 'N/A', path, size, 'N/A', sha1, 'amcache'))
							#yield '{},{},{},{},{},{},{},{}'.format(hostname, modified2, 'N/A', path, size, 'N/A', sha1, 'shimcache')
		except Registry.RegistryParse.ParseException:
			continue
	return entries

#def BuildVolumeList(path):
#	vols = {}
#	System_hives = TraversePath(path)
#	for hive in System_hives:
#		fname = os.path.split(hive)[1]
#		if fname.lower().startswith('system_'):
#			hostname = RegistryGetHostname(hive)
#			guids = find_vol_guids_in_SYSTEM(hive)
#			if guids:
#				vols[hostname] = guids
#			else:
#				print('[!] Weird. Found no volumes in file: {}'.format(hive))
#	return vols

def sort_list(seq, idfun=None): 
	if idfun is None:
		def idfun(x): return x
	seen = {}
	result = []
	for item in seq:
		marker = idfun(item)
		if marker in seen: continue
		seen[marker] = 1
		result.append(item)
	return result

def Process_Amcache(args):
	registryBase_amcache_guids = 'Root\\File'
	volumes = {}
	amcache_entries = list()

	total_files = getTotalFilesStartsWith(args.amcache, 'amcache_')
	print("Amcache Hive Count: {}".format(total_files))

	counter = 0
	for hive in TraversePath(args.amcache):
		hostname = host = ''
		#Get hostname from ECAT style Filename
		fname = os.path.split(hive)[1]
		if not fname.lower().startswith('amcache_'):
			continue
		parts = fname.split('_')
		if len(parts) > 4 and len(parts[2]) == 64:
			hostname = parts[1]
		if not hostname: 
			hostname = 'N/A'
			if g_debug:
				print('[!] Unable to find hostname for Amcache volume: {}'.format(fname))
		
		try:
			Hive_Amcache = Registry.Registry(hive)
		except Registry.RegistryParse.ParseException as err:
			print('[!] main() Error parsing file: {}'.format(hive))
			print('[!] main() Error given: {}'.format(err))
			continue

		Amcache_vol_root = Hive_Amcache.open(registryBase_amcache_guids)

		if g_debug:
			print('[+] Processing file: {} ==> {}'.format(fname, hostname))
		try:

			amcache_entries = amcache_retrieve_results(hostname, Hive_Amcache)
		except:
			print('[!] Unable to process Amcache volume: {}'.format(fname))
		else:
			counter += 1
			print('{:.1%} Complete'.format(float(counter) / float(total_files)))
			#print amcache_entries
			for entry in amcache_entries:
					entry = u','.join(str(i).decode('utf-8') for i in entry)
			write_amcache(amcache_entries)

def readRFC(hostname, fname):
	magics = [b'\xfe\xff\xee\xff', b'\x11\x22\x00\x00', b'\x03\x00\x00\x00', b'\x01\x00\x00\x00']

	filesize = os.path.getsize(fname)
	if filesize <= 20:
		return

	with open(fname, "rb") as fh:
		fh.seek(0)
		for i in range(0, len(magics)):
			header = fh.read(4)
			if not header == magics[i]:
				return
		volumeID = fh.read(4) # Disregard this value
		
		while fh.tell() < filesize:
			tmp_buffer = fh.read(4)
			entry_len = (struct.unpack('<i', tmp_buffer)[0]) * 2 # For unicode
			entry = fh.read(entry_len)
			#hostname, Last Modified, Last Update, path, File Size, Exec Flag, sha1, source_file
			#return('{},,,{},,,,recentfilecache'.format(hostname, entry.decode('utf-16')))
			write_line('{},,,{},,,,recentfilecache'.format(hostname, entry.decode('utf-16')))
			fh.read(2) # Disregard last two unicode null terminators as they break in decode
	fh.close()

#def ParseRFCs(rfc_path):
def Process_RecentFileCache(rfc_path):
	counter = 0
	total_files = getTotalFilesStartsWith(rfc_path, 'recentfilecache_')
	print('RecentFileCache Count: {}'.format(total_files))

	for filename in TraversePath(rfc_path):
		fname = os.path.split(filename)[1]
		if fname.lower().startswith('recentfilecache'):
			parts = fname.split('_')
			#Get hostname from ECAT style Filename
			if len(parts) > 4 and len(parts[2]) == 64:
				hostname = parts[1]
				if g_debug:
					print('[+] Parsing file: {}'.format(filename))
				readRFC(hostname, filename)
				counter += 1
				print('{:.1%} Complete'.format(float(counter) / float(total_files)))
				#temp = readRFC(hostname, filename)
				#if temp: 
				#	yield(temp)

def ParseShimcache(system_path):
	counter = 0
	total_files = getTotalFilesStartsWith(system_path, 'system_')
	print("System Hive Count: {}".format(total_files))

	for filename in TraversePath(system_path):
		fname = os.path.split(filename)[1]
		if fname.lower().startswith('system_'):
			counter += 1
			print('{:.1%} Complete'.format(float(counter) / float(total_files)))
			entries = ''
			if g_debug:
				print('[+] Parsing file: {}'.format(filename))

			try:
				entries = ShimCacheParser.read_from_hive(filename)
				# Remove the CSV header
				entries.pop(0)
			except:
				continue
			if not entries:
				continue

			fname = os.path.split(filename)[1]
			if fname.lower().startswith('system'):
				parts = fname.split('_')
			#Get hostname from ECAT style Filename
			if len(parts) > 4 and len(parts[2]) == 64:
				hostname = parts[1]
				#print hostname
			else:
				#print('[!] Error. Hostname not found in filename.')
				#try from system hive itself
				try:
					hostname = RegistryGetHostname(filename)
				except:
					print('[!] Error. Unable to obtain Hostname from SYSTEM Hive.')
					hostname = 'N/A'

			for entry in entries:
				entry.insert(0, hostname)
				entry.insert(6, '') #SHA1 Hash field
				entry.insert(7, 'shimcache') #Data Source field
				#print entry
				try:
					#result = u','.join(i.decode('utf-8') for i in entry)
					#result = u','.join(str(i).decode('utf-8') for i in entry)
					#print entry
					#print 'CONVERT!!!!'
					entry = u','.join(str(i).decode('utf-8') for i in entry)
					#print entry
					#print result
					#yield(result)
				except UnicodeDecodeError:
					pass
				except AttributeError:
					pass
			write_output(entries)

def Process_Jobs(path):
	total_files = 0
	for filename in TraversePath(path):
		fname = os.path.split(filename)[1]
		if '.job' in fname.lower(): 
			total_files += 1
	print("Jobs file Count: {}".format(total_files))
	
	counter = 0
	for filename in TraversePath(path):
		fname = os.path.split(filename)[1]
		if '.job' in fname.lower():
			counter += 1
			print('{:.1%} Complete'.format(float(counter) / float(total_files)))

			if g_debug:
				print('[+] Parsing file: {}'.format(filename))
			try:
				#file = open(os.path.join(dir, fname), "rb")
				file = open(filename, "rb")
			except:
				print('[!] Unable to open file: {}'.format(filename))
			
			#theJob = Job(file.read())
			#theJob = MyJob(file.read())
			try:
				theJob = Job(file.read())	
			except:
				print('[!] Unable to parse Job file: {}'.format(filename))
			else:
				if theJob:
					#Get hostname from ECAT style Filename
					if '.job' in fname.lower():
						parts = fname.split('_')
					if len(parts) > 4 and len(parts[2]) == 64:
						hostname = parts[1]
					#print hostname
					else:
						hostname = 'N/A'
						if g_debug:
							print('[!] Error. Hostname not found in filename.')

					line = hostname + ',' + str(theJob.RunDate) + ',' + ',' + str(theJob.Name) + ',,,,' + 'job'
					write_line(line)

					#write additional job parsing to another file
					result =  "*" * 72
					result += "\nFile: " + fname + '\n'
					result += str(theJob._get_job_info)
					result += "*" * 72
				
					if g_overwrite:
						if g_debug:
							print('[+] Overwritting output file: {}'.format(g_outputfile + '_joboutput.txt'))
						f = open(g_outputfile + '_joboutput.txt', 'w')
						f.write(result)
						f.close()
					else:
						f = open(g_outputfile + '_joboutput.txt', 'a+')
						if g_debug:
							print('[+] Writing output file: {}'.format(g_outputfile + '_joboutput.txt'))
						f.write(result)
						f.close()
						
def Process_Prefetch(path):
	total_files = getTotalFilesIn('.pf',path)
	print("Prefetch file Count: {}".format(total_files))
	
	counter = 0
	for filename in TraversePath(path):
		fname = os.path.split(filename)[1]
		if '.pf' in fname.lower():
			counter += 1
			print('{:.1%} Complete'.format(float(counter) / float(total_files)))

			if g_debug:
				print('[+] Parsing file: {}'.format(filename))
			#try:
				#file = open(os.path.join(dir, fname), "rb")
			#	file = open(filename, "rb")
			#except:
			#	print('[!] Unable to open file: {}'.format(filename))
	
			try:
				p = Prefetch(filename)	
			except:
				print('[!] Unable to parse Prefetch file: {}'.format(filename))
			else:
				if p:
					#for item in p.__dict__:
					#	print item
					#print p.__dict__
					#return
					
					#Get hostname from ECAT style Filename
					hostname = getHostnameFromFilename(fname)
					FilePath = p.executableName
					
					for resource in p.resources:
						if p.executableName in resource:
							FilePath = resource
					for resource in p.resources:
						if resource.endswith(p.executableName):
							FilePath = resource
					#'Hostname,Time Stamp,Last Update,File Path,File Size,Shimcache Exec Flag,SHA1 Hash,Data Source\n')
					#print "{},{},{},{},{}".format(p.timestamps[0], p.mftSeqNumber, p.mftRecordNumber, p.executableName, p.runCount)
					line = "{},{},{},{},{},{},{},{}".format(hostname, p.timestamps[0], "", FilePath, "", "", "", "prefetch")
					#line = hostname + ',' + str(theJob.RunDate) + ',' + ',' + str(theJob.Name) + ',,,,' + 'job'
					write_line(line)
def Parse_Amcache(path):
	total_files = getTotalFilesStartsWith(path, 'amcache_')
	print("Amcache Hive Count: {}".format(total_files))
	counter = 0
	for filename in TraversePath(path):
		fname = os.path.split(filename)[1]

		if fname.lower().startswith('amcache_'):
			#Get hostname from ECAT style Filename
			hostname = getHostnameFromFilename(fname)

			#entries = ''
			if g_debug:
				print('[+] Parsing file: {}'.format(filename))
			try:
				r = Registry.Registry(filename)
			except:
				print('[!] Unable to open as Amcache Hive as Registry : {}'.format(filename))
			else:
				try:
					ee = amcache.parse_execution_entries(r)
				except:
					print('[!] Unable to parse Amcache Hive : {}'.format(filename))
				else:
					entries = []
					TimelineEntry = namedtuple("TimelineEntry", ["timestamp", "type", "entry"])
					#print ee
					for e in ee:
						for t in ["source_key_timestamp", "created_timestamp", "modified_timestamp", "modified_timestamp2", "linker_timestamp"]:
							ts = getattr(e, t)
							if ts == UNIX_TIMESTAMP_ZERO:
								continue
							if ts == WINDOWS_TIMESTAMP_ZERO:
								continue
							if ts == datetime.datetime.min:
								continue
							#print ts
							#print e
							#print type(e)
							#for i in e:
								#print i
								
							#print e.entry.path
							#print e.entry.sha1
							entries.append(TimelineEntry(ts, t, e))
							#print (hostname, ts, e.entry.path, e.entry.sha1)
							#write_line(hostname, e.timestamp, e.entry.path, e.entry.sha1)
							#entries.append(ts,e)
					
					#w = unicodecsv.writer(sys.stdout, delimiter="|", quotechar="\"",quoting=unicodecsv.QUOTE_MINIMAL, encoding="utf-8")
					#w.writerow(["timestamp", "timestamp_type", "path", "sha1"])
					#for e in sorted(entries, key=lambda e: e.timestamp):
						#print e
						#print (hostname, [e.timestamp, e.entry.path, e.entry.sha1])
						#line = hostname + e.timestamp, e.type, e.entry.path, e.entry.sha1
					#	w.writerow([e.timestamp, e.type, e.entry.path, e.entry.sha1])
					for e in entries:
						#('Hostname,Time Stamp,Last Update,File Path,File Size,Shimcache Exec Flag,SHA1 Hash,Data Source\n')
						ts = e.timestamp
						#print type(ts)
						#print ts.strftime("%B %d, %Y")
						#timestamp = ts.strftime(DATE_ISO)
						line = "{},{},{},{},{},{},{},{}".format(hostname, ts.strftime(DATE_ISO), "", e.entry.path, "", "", e.entry.sha1, "amcache")
						#line = hostname + ts.strftime(DATE_ISO) + e.entry.path + e.entry.sha1
						#print line
						write_line(line)
			counter += 1
			print('{:.1%} Complete'.format(float(counter) / float(total_files)))

def Process_UserAssist(path):
	total_files = getTotalFilesStartsWith(path, 'ntuser_')
	print("NTUSER.DAT Hive Count: {}".format(total_files))
	counter = 0
	for filename in TraversePath(path):
		fname = os.path.split(filename)[1]

		if fname.lower().startswith('ntuser_'):
			#Get hostname from ECAT style Filename
			hostname = getHostnameFromFilename(fname)

			#entries = ''
			if g_debug:
				print('[+] Parsing file: {}'.format(filename))
			#plugin = userassist.PluginClass()
			#entry = plugin.getUserAssist(filename)
			#print entry
			#entry = userassist.getUserAssist(filename)
			#print entry
			try:
				plugin = userassist.PluginClass()
				entry = plugin.getUserAssist(filename)
			except:
				print('[!] Unable to parse NTUSER.DAT Hive : {}'.format(filename))
			else:
				#print entry
				#for en in entry:
				#	last_write = entry[0]
				#	sub_key = entry[1]
				#	runcount = entry[2]
				#	windate = entry[3]
				#	data = entry[4] 
				#print('#last_write,sub_key,runcount,windate,data')
				for e in entry:
					#print e
					last_write = e[0]
					#sub_key = e[1]
					#runcount = e[2]
					windate = e[3]
					data = e[4]
					#print windate
					#print datetime.datetime.now().strftime(DATE_ISO)
					#fh.write('Hostname,Time Stamp,Last Update,File Path,File Size,Shimcache Exec Flag,SHA1 Hash,Data Source\n')
					
					try:
						#print last_write.strftime(DATE_ISO)
						line = "{},{},{},{},{},{},{},{}".format(hostname, windate.strftime(DATE_ISO), last_write.strftime(DATE_ISO), data, "", "", "", "userassist")
					except:
						line = "{},{},{},{},{},{},{},{}".format(hostname, "", last_write.strftime(DATE_ISO), data, "", "", "", "userassist")
					#line = hostname + ',' + str(theJob.RunDate) + ',' + ',' + str(theJob.Name) + ',,,,' + 'job'
					write_line(line)
					#print windate.strftime("%Y-%m-%d %H:%M:%S")
					#datetime.strptime(date_string, format)
					#datetime.strptime(windate, DATE_ISO)
					#windate.strptime(DATE_ISO)
					#print windate
					#print windate
					
def Process_MuiCache(path):
	total_files = 0
	total_files += getTotalFilesStartsWith(path, 'ntuser_')
	total_files += getTotalFilesStartsWith(path, 'usrclass_')
	print("NTUSER.DAT/USRCLASS.DAT Hive Count: {}".format(total_files))
	counter = 0
	for filename in TraversePath(path):
		fname = os.path.split(filename)[1]

		if (fname.lower().startswith('ntuser_') or fname.lower().startswith('usrclass_')):
			#Get hostname from ECAT style Filename
			hostname = getHostnameFromFilename(fname)
			#open Registry as r
			r = Registry.Registry(filename)
			
			#entries = ''
			if g_debug:
				print('[+] Parsing file: {}'.format(filename))
			
			if fname.lower().startswith('ntuser'):
				try:
					entries = muicache.parseMuiCacheNTUSER(r)
				except Registry.RegistryKeyNotFoundException as e:
					if g_debug:
						print '[!] MuiCache not found in {}',format(filename)
				else:
					for e in entries:
						lastwrite = e[0]
						name = e[1]
						#data = e[2]
						line = "{},{},{},{},{},{},{},{}".format(hostname, "", lastwrite.strftime(DATE_ISO), name, "", "", "", "muicache")
						write_line(line)
			elif fname.lower().startswith('usrclass'):
				try:
					entries = muicache.parseMuiCacheUSRCLASS(r)
				except Registry.RegistryKeyNotFoundException as e:
					if g_debug:
						print '[!] MuiCache not found in {}',format(filename)
				else:
					for e in entries:
						lastwrite = e[0]
						name = e[1]
						#data = e[2]
						line = "{},{},{},{},{},{},{},{}".format(hostname, "", lastwrite.strftime(DATE_ISO), name, "", "", "", "muicache")
						write_line(line)
def main():
	global g_outputfile
	global g_debug
	global g_overwrite
	print(r"""
             / /
          (\/_//`)
           /   '/
          0  0   \
         /        \
        /    __/   \
       /,  _/ \     \_
       `-./ )  |     ~^~^~^~^~^~^~^~\~.
           (   /                     \_}
              |        R S A  /      |
              ;     |         \      /
               \/ ,/           \    |
               / /~~|~|~~~~~~|~|\   |
              / /   | |      | | `\ \
             / /    | |      | |   \ \
            / (     | |      | |    \ \
           /,_)    /__)     /__)   /,_/
     ''''''''''''''''''''''''''''''''''''''''
     ''''''''''   RSA Mass Triage   '''''''''
     ''''''''''''''''''''''''''''''''''''''''
    """)
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-s', '--system', help='SYSTEM Hive Directory', required=False)
	parser.add_argument('-a', '--amcache', help='Amcache.hve Directory', required=False)
	parser.add_argument('-r', '--rfc', help='RecentFileCache.BCF Directory', required=False)
	parser.add_argument('-j', '--jobs', help='.Job Directory', required=False)
	parser.add_argument('-p', '--prefetch', help='Prefetch (.PF)  Directory', required=False)
	parser.add_argument('-u', '--userassist', help='UserAssist entries from NTUSER.DAT Directory', required=False)
	parser.add_argument('-m', '--muicache', help='Muicache entries from NTUSER.DAT/USRCLASS.DAT Directory', required=False)
	parser.add_argument('-o', '--output', help='Output CSV file', required=True)
	parser.add_argument('--debug', help='Enable Debug', action='store_true', required=False)
	#parser.add_argument('--delete', help='Delete files after parsing', action='store_true', required=False)
	parser.add_argument('--append', help='Append to Output File (instead of overwriting)', action='store_true', default=False, required=False)
	args = parser.parse_args()

	if args.debug:
		g_debug = True

	if args.output:
		g_outputfile = args.output
	#results = list()


	
	#Handle Output
	if (not args.append):
		if g_debug:
			print('[+] Writing output file: {}'.format(args.output))
		try:
			# This is Python2 way
			fh = io.open(g_outputfile, 'w', encoding='utf-8')
		except IOError as err:
			print('[-] Error opening output file: {}'.format(err))
			return
		fh.write('Hostname,Last Write, Key Name, Name, Value\n')
		fh.close()

	#Parse Things
	if args.system:
		ParseShimcache(args.system)

	if args.rfc:
		Process_RecentFileCache(args.rfc)
		
	if args.jobs:
		Process_Jobs(args.jobs)
	
	if args.prefetch:
		Process_Prefetch(args.prefetch)
		
	if args.userassist:
		Process_UserAssist(args.userassist)
		
	if args.muicache:
		Process_MuiCache(args.muicache)
	
	if args.amcache:
		#OLD WAY
		#Process_Amcache(args)
		#New way Using Ballenthin's amcache.py
		Parse_Amcache(args.amcache)
if __name__ == '__main__':
	main()
