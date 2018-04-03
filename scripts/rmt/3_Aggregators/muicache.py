#!/usr/bin/python
#
# Python MuiCache parser
# Extracts the Last Write, name and data from the MuiCache in NTUSER.DAT or USRCLASS.DAT
#
# Author
# Copyright 2017 timetology@gmail.com Twitter: @timetology
#
# Change Log
# .1	17/Feb/2017 - Initial Development
#
# License
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import io
import os
import datetime
try:
	from Registry import Registry
except ImportError:
	print('This script requires python-registry Registry Directory in the same path: https://github.com/williballenthin/python-registry')
	quit()

g_debug = False
DATE_ISO = "%Y-%m-%d %H:%M:%S"

def PrintAllKeys(key, depth=0):
    print "\t" * depth + key.path()

    for subkey in key.subkeys():
        PrintAllKeys(subkey, depth + 1)


def parseMuiCacheNTUSER(reg):
	MuiCache = 'Software\\Microsoft\\Windows\\ShellNoRoam\\MuiCache'
	MuiCacheEntries = []
	
	key = reg.open(MuiCache)

	values = key.values()
	if values:
		for v in values:
			MuiCacheEntries.append((key.timestamp(), v.name(), v.value()))
			#print str(key.timestamp()) + ',' + v.name() + ',' + v.value()
	return MuiCacheEntries

def parseMuiCacheUSRCLASS(reg):
	MuiCache = 'Local Settings\\Software\\Microsoft\\Windows\\Shell\\MuiCache'
	MuiCacheEntries = []
	
	key = reg.open(MuiCache)

	values = key.values()
	if values:
		for v in values:
			MuiCacheEntries.append((key.timestamp(), v.name(), v.value()))
			#print str(key.timestamp()) + ',' + v.name() + ',' + v.value()
	return MuiCacheEntries

		
def main():
	global g_debug
	parser = argparse.ArgumentParser(description='MuiCache Parser for NTUSER.DAT and USRCLASS.DAT')
	parser.add_argument('-i', '--input', metavar='<NTUSER.DAT/USRCLASS.DAT>', help='NTUSER.DAT or USRCLASS.DAT Hive', required=True)
	parser.add_argument('--debug', help='Enable Debug', action='store_true', required=False)
	args = parser.parse_args()
	
	if args.debug:
		g_debug = True
	
	r = Registry.Registry(args.input)
	
	fname = os.path.split(args.input)[1]
	if fname.lower().startswith('ntuser'):
		try:
			entries = parseMuiCacheNTUSER(r)
		except Registry.RegistryKeyNotFoundException as e:
			if g_debug:
				print '[!] MuiCache not found in {}',format(args.input)
		else:
			print "Last Write,Name,Value" 
			for entry in entries:
				#print str(entry[0]) + ',' + entry[1] + ',' + entry[2]
				print entry[0].strftime(DATE_ISO) + ',' + entry[1] + ',' + entry[2]
	elif fname.lower().startswith('usrclass'):
		try:
			entries = parseMuiCacheUSRCLASS(r)
		except Registry.RegistryKeyNotFoundException as e:
			if g_debug:
				print '[!] MuiCache not found in {}',format(args.input)
		else:
			print "Last Write,Name,Value" 
			for entry in entries:
				#print str(entry[0]) + ',' + entry[1] + ',' + entry[2]
				print entry[0].strftime(DATE_ISO) + ',' + entry[1] + ',' + entry[2]
	else:
		print "[!] Not a NTUSER.DAT or USRCLASS.DAT Hive."
		exit()
		
if __name__ == '__main__':
	main()