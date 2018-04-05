#!/usr/bin/python
# RSA NetWitness Endpoint - Downloaded File Renamer
# Author: RSA IR <nw-ir@rsa.com>
#
# TODO:
#	Add in copy ability
#	-r RECURSE??? (maybe for copy only)
#	Add in pre/suffix ability
#	Logging
# 	Handle >1 MachineName returned better
#
# Description:
# For each file in the supplied directory, script will get the associated MachineName from the ECAT DB and insert the MachineName into the filename.
#
# e.g.: SYSTEM_de5a16da1de6a30fa691170aac750915db96cfac0cb1fa9ef83aaedfba77f945_38271nm_ -> SYSTEM_MachineName_de5a16da1de6a30fa691170aac750915db96cfac0cb1fa9ef83aaedfba77f945_38271nm_
# Change Log
# .1 03May2016 
#	Initial Development
# .2 18Jul2017
#   Added in Getpass Support
# .3 05April2018
#	Added -r recursive directory traversal

import argparse
import os
import pyodbc


def SQL_Lookup_MachineName(db,filename):
	#Setup Cursor
	cursor = db.cursor()

	#setup Query
	query = """\
SELECT DISTINCT mn.MachineName FROM
	[dbo].[MachineDownloaded] AS [md] WITH(NOLOCK)
	INNER JOIN [dbo].[FileNames] AS [fn] WITH(NOLOCK) ON ([fn].[PK_FileNames] = [md].[FK_FileNames__RelativeFileName])
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON ([mn].[PK_Machines] = [md].[FK_Machines])
	WHERE fn.filename = '"""
	query = query + filename + "'"
	cursor.execute(query)
	list = cursor.fetchall()
	if len(list) == 1:
		cursor.close()
		return list[0][0]
	elif len(list) > 1:
		raise Exception('--More than one MachineNames returned.')
	else:
		raise Exception('--Zero MachineNames Returned.')

def main():
	parser = argparse.ArgumentParser(description='For each file in the supplied directory, script will get the associated MachineName from the ECAT DB and insert the MachineName into the filename.')
	parser.add_argument('-d','--dir', help='Directory where files are stored', metavar='<directory>', required=True)
	parser.add_argument('-u','--user', help='Username for SQL Database. Default: Windows Credentials', metavar='<user>')
	parser.add_argument('-p','--pass', dest='passwd', help='Password for SQL Database. Default: Windows Credentials', metavar='<password>')
	parser.add_argument('-s','--server', help='Hostname or IP for SQL Server. Default: localhost', metavar='<hostname or IP>', default='LOCALHOST')
	parser.add_argument('-db','--database', help='ECAT database', metavar='<database>', default='ECAT$PRIMARY')
	parser.add_argument('-r','--recursive', help='Recursively traverse directory', action='store_true', default=False)
	#parser.add_argument('-c','--copy', action='store_true', default=False, help='COPY files instead of rename (Requires -o <output directory> and it recommended you use -pre <prefix> or -suf <suffix>')
	#parser.add_argument('-o','--output', help='Output Directory used when -c (copy) is specified', metavar='<output_directory>')
	#parser.add_argument('-pre','--prefix', help='Prefix for files to rename or copy', metavar='<prefix>')
	#parser.add_argument('-suf','--suffix', help='Suffix for files to rename or copy', metavar='<suffix>')
	args = parser.parse_args()
	
	#DB CONNECTION
	#Check if only user is set and prompt for password
	if ((args.user) and (args.passwd is None)):
		import getpass
		print "Enter password: "
		args.passwd = getpass.getpass()

	#Check if password is set
	if ((args.user is None) and (args.passwd)):
		parser.error("-p Password specified but -u User not assigned")

	#Build query to connect to DB
	if args.user and args.passwd:
		conn = 'DRIVER={};SERVER={};DATABASE={};UID={};PWD={}'.format('{SQL Server}', args.server, args.database, args.user, args.passwd)
	else:
		conn = 'DRIVER={};SERVER={};DATABASE={};Trusted_Connection=yes'.format('{SQL Server}', args.server, args.database)

	#Connect to DB
	try:
		db = pyodbc.connect(conn)
	except pyodbc.Error as err:
		parser.error(err)
			
	#Recursively traverse directories or just look in single dir if -r not specified
	if (args.recursive):
		#Recursive directory
		dirlist = []
		for dirpath, dirnames, files in os.walk(args.dir):
		  for dirname in dirnames:
			dirlist.append(os.path.join(dirpath,dirname))

	else:
		dirlist = []
		dirlist.append(args.dir)
		
		
	for dir in dirlist:
		#Check if directory is exists
		if not (os.path.isdir(dir)):
			parser.error('Directory does not exist.')

		#Check if dir ends with a / or \
		if not (dir.endswith('\\') or dir.endswith('/')):
			#Append the appropriate slash
			#Check abs path to see if windows or linux dir structure
			print(os.path.abspath(dir))
			if '\\' in str(os.path.abspath(dir)):
				#path = str(os.path.abspath(dir) + '\\'
				dir = dir + '\\'
			elif '/' in str(os.path.abspath(dir)):
				#path = str(os.path.abspath(dir) + '\'
				dir = dir + '/'

		#If -c is set, check if -o is also set and vice versa
		#if ((args.copy and args.output is None) or (args.copy is None and args.output)):
		#	parser.error("-c (--copy) requires -o (--output) <output_directory>")

		#Check if both -pre and -suf are set as they are mutually exclusive
		#if (args.prefix and args.suffix):
		#	parser.error("-pre (--prefix) <prefix> and -suf (--suffix) <suffix> are mutally exclusive")



		#Lookup MachineName for each file in specificed Directory
		for file in os.listdir(dir):
			try:
				MachineName = SQL_Lookup_MachineName(db,file)
			except Exception as e:
				print('[-] Error looking up {} {}'.format(file,e))
			else:
				#Insert Systemname into Filename
				newfile = file.split('_')[0] + '_' + MachineName + '_'
				newfile_list = file.split('_')
				newfile_list.pop(0)	#Remove first entry we already used that
				for item in newfile_list:
					newfile = newfile + item + '_'

				#Rename the file
				try:
					os.rename(dir + file, dir + newfile)
				except OSError as err:
					print('[-] Error Renaming {} to {}...'.format(dir + file,newfile))
				else:
					print('[+] Renamed {} to {}...'.format(dir + file,newfile))
	#Close the DB
	db.close()

if __name__ == '__main__':
	main()
