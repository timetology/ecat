#
# RSA Mass analysis of ntuser.dat RunKeys
# RSA Incident Response firstresponse@rsa.com incidentresponse.rsa.com
#
# Change Log
# .1 11Oct2017
#	Initial Development


from __future__ import unicode_literals

import sys
import os
import argparse
import io
import unicodecsv


try:
	from Registry import Registry
except ImportError:
	print('This script requires python-registry Registry Directory in the same path: https://github.com/williballenthin/python-registry')
	quit()

DATE_ISO = "%Y-%m-%d %H:%M:%S"
g_debug = False
g_outputfile = ''
g_overwrite = False

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

def TraversePath(directory):
	for dirpath,_,filenames in os.walk(directory):
		for f in filenames:
			yield os.path.abspath(os.path.join(dirpath, f))

def getTotalFilesStartsWith(path, file_prefix):
	counter = 0
	for filename in TraversePath(path):
		fname = os.path.split(filename)[1]
		if fname.lower().startswith(file_prefix): 
			counter += 1
	return counter

def write_line(data):
	try:
		fh = io.open(g_outputfile, 'a+', encoding='utf-8')
	except IOError as err:
		print('[-] Error opening output file: {}'.format(err))
		return
	else:
		fh.write(data + '\n')

def processRunKeys(hive):
		run_key_list = []
		run_entries =   ["Microsoft\\Windows\\CurrentVersion\\Run",
						 "Microsoft\\Windows\\CurrentVersion\\RunOnce",
						 "Microsoft\\Windows\\CurrentVersion\\RunOnceEx",
						 "Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run",
						 "Microsoft\\Windows\\CurrentVersion\\RunServicesOnce"
						 "Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run",
						 "Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
						 "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
						 "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
						 "Software\\Microsoft\\Windows\\CurrentVersion\\RunServices",
						 "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run"]
		
		for k in run_entries:
			try:
				for v in  Registry.Registry(hive).open(k).values():
					last_write = Registry.Registry(hive).open(k).timestamp()
					if k:
						key_name = k
					else:
						key_name = "None"
					if v.name():
						name = v.name()
					else:
						name = "None"
					if v.value():
						value = v.value()
					else:
						value = "None"
					run_key_list.append([last_write, key_name, name, value])
					
			except Registry.RegistryKeyNotFoundException:
				continue
		
		dict = {}
		for entry in run_key_list:
			dict[entry[2]] = entry[0], entry[1], entry[3]			
		return(run_key_list)
		#return(dict)

def ParseNTUSER(ntuser_path):
	counter = 0
	total_files = getTotalFilesStartsWith(ntuser_path, 'ntuser_')
	print("NTuser.dat Hive Count: {}".format(total_files))

	for filename in TraversePath(ntuser_path):
		fname = os.path.split(filename)[1]
		if fname.lower().startswith('ntuser_'):
			parts = fname.split('_')
			#Get hostname from ECAT style Filename
			hostname = getHostnameFromFilename(filename)
			if g_debug:
				print('[+] Parsing file: {}'.format(filename))
			try:
				reg = Registry.Registry(filename)
			except:
				print('[!] Unable to open as NTUSER.DAT Hive as Registry : {}'.format(filename))
			else:
				try:
					output = processRunKeys(filename)
				except:
					print('[!] Unable to process Run Keys in: {}'.format(filename))
				else:
					#print output
					for e in output:
						ts = e[0]
						line = "{},{},{},{},{}".format(hostname, ts.strftime(DATE_ISO), e[1], e[2], e[3])
						write_line(line)
				counter += 1
				print('{:.1%} Complete'.format(float(counter) / float(total_files)))
def main():
	global g_outputfile
	global g_debug
	global g_overwrite
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-n', '--ntuser', help='NTUSER.dat Hive Directory', required=True)
	parser.add_argument('-o', '--output', help='Output CSV file', required=True)
	parser.add_argument('--debug', help='Enable Debug', action='store_true', required=False)
	#parser.add_argument('--delete', help='Delete files after parsing', action='store_true', required=False)
	parser.add_argument('--append', help='Append to Output File (instead of overwriting)', action='store_true', default=False, required=False)
	args = parser.parse_args()

	if args.debug:
		g_debug = True

	if args.output:
		g_outputfile = args.output

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
		fh.write('Hostname,Last Write,Key Name,Name,Value\n')
		fh.close()

	#Parse Things
	if args.ntuser:
		ParseNTUSER(args.ntuser)



if __name__ == '__main__':
	main()