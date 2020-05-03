#!/usr/bin/python
#
# Author: RSA IR <firstresponse@rsa.com>
#
# Description: RSA Download Files from Windows Hosts via NetWitness Endpoint (ECAT)
#
# Notes: Requires permission to issue exec commands (GRANT EXECUTE ON dbo.usp_InsertMachineCommand TO [userName])
#
#
# Change Log
# .1	06Dec2016 - Initial Development
# .2	08Dec2016 - Fix for large systems, issues download command to 100 systems at a time.
# .3	15Feb2017 - Implemented .1 second delay & Now Reads in Artifact list from file
# .4	25Apr2017 - Changed maxfiles from variable to command line arg defaulting to 100. Adjusted sleep time to .05 seconds. Changed behavior for when --debug is used
#
# TODO
# Determine Interaction with a multiserver environment
# Add option to only download from systems which have not yet been downloaded
# Fix percentage
# Provide list of machine names to only download from.

import argparse
import pyodbc
import math
from time import sleep
from tqdm import *

global g_debug
#g_debug = False



def main():
	parser = argparse.ArgumentParser(description='Download files using NWEndpoint from a supplied list of files')
	parser.add_argument('-f','--filename', help='Input list of files to download', required=True)
	#parser.add_argument('-n','--new', help='Download from new systems only (No previous download)',action='store_true', default=False)
	parser.add_argument('-m','--maxfiles', help='Maximum number of files to download when wildcard (*) is used. Default 100', default='100')
	parser.add_argument('-b','--batch', help='Number of systems to request download from per batch. Default 100', default='100')
	parser.add_argument('-u','--user', help='Username for SQL Database. Default: Windows Credentials', metavar='<user>')
	parser.add_argument('-p','--pass', dest='passwd', help='Password for SQL Database. (If user specified with no pass then you will be prompted for the pass)', metavar='<password>')
	parser.add_argument('-s','--server', help='Hostname or IP for SQL Server. Default: localhost', metavar='<hostname or IP>', default='LOCALHOST')
	parser.add_argument('-db','--database', help='ECAT database', metavar='<database>', default='ECAT$PRIMARY')
	parser.add_argument('--debug', help='Enable Debug Messages', action='store_true', default=False)

	args = parser.parse_args()

	#global g_debug
	g_debug = args.debug
	filename = args.filename

	#Check if only user is set and prompt for password
	if ((args.user) and (args.passwd is None)):
		import getpass
		print "Enter password: "
		args.passwd = getpass.getpass()

	#Check if password is set
	if ((args.user is None) and (args.passwd)):
		parser.error("-p Password specified but -u User not assigned")

	try:
		with open(filename) as f:
			artifactList = f.read().splitlines()
	except IOError:
		raise Exception("[!] Could not read file:" + filename)
	else:
		if g_debug:
			print('[+] Processing {}'.format(filename))
			print('[+] ArtifactList Length {}'.format(len(artifactList)))
			print('[+] MaxFiles {}'.format(args.maxfiles))
		f.close()

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

	#Get Machine List (OSType = 1 is Windows)
	txt = "select PK_Machines from dbo.Machines where dbo.Machines.FK_OSTypes = 1 AND dbo.Machines.MarkedAsDeleted = 0"

	#Setup Cursor
	cursor = db.cursor()

	#Get List of Systems
	cursor.execute(txt)
	rows = cursor.fetchall()
	total_files = len(rows)
	if g_debug:
		print 'Number of Systems: ' + str(len(rows)) + '\n'

	#if (len(rows) < 1000):
		#Split list into chunks
		#numchunks = int(math.ceil(len(rows) / 1000.00))

		#print "\nnumchunks " + str(numchunks)
		#print zip(*[iter(rows)]*numchunks)
		#print zip(rows*1000)
		#for item in zip(*[iter(rows)]*1000):
		#	print item[0]
		#	print '\n*********************************************\n'

	lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
	
	count = 0
	if g_debug:
		#Process args.batch (default 100) at a time NO tqdm
		for list in lol(rows,int(args.batch)):
			#print item
			count += 1
			if g_debug:
				print '[+] Processing Batch: ' + str(count)
			sql_header = "declare @p1 dbo.uty_PrimaryKeyList\n"
			for entry in list:
				sql_header = sql_header + "insert into @p1 values(" + str(entry.PK_Machines) + ")\n"

			#Process Artifact List Downloads
			for artifact in artifactList:
				if g_debug:
					print('    [+] Batch [{}] - Processing {}'.format(count,artifact))
				sql = sql_header
				sql = sql + "declare @p5 dbo.uty_MachineCommandParams\n"
				sql = sql + "insert into @p5 values(N'Path',N'" + artifact + "')\n"
				sql = sql + "insert into @p5 values(N'maxfiles',N'" + args.maxfiles + "')\n"
				sql = sql + "exec dbo.usp_InsertMachineCommand @MachinesPKList=@p1,@Type=256,@Comment=N'Download RSA File Download',@IsAutomatic=0,@CommandParams=@p5"

				try:
					cursor.execute(sql)
					db.commit()
				except Exception as e:
					print('[!] Error: {}'.format(e))

				#Wait
				if g_debug:
					print '    [+] Sleeping .05 seconds'
					print('{:.1%} Complete'.format(float(count) / float(total_files)))
				sleep(0.05)
	else:
		#Process args.batch (default 100) at a time
		for list in tqdm(lol(rows,int(args.batch))):
			#print item
			count += 1
			if g_debug:
				print '[+] Processing Batch: ' + str(count)
			sql_header = "declare @p1 dbo.uty_PrimaryKeyList\n"
			for entry in list:
				sql_header = sql_header + "insert into @p1 values(" + str(entry.PK_Machines) + ")\n"

			#Process Artifact List Downloads
			for artifact in artifactList:
				if g_debug:
					print('    [+] Batch [{}] - Processing {}'.format(count,artifact))
				sql = sql_header
				sql = sql + "declare @p5 dbo.uty_MachineCommandParams\n"
				sql = sql + "insert into @p5 values(N'Path',N'" + artifact + "')\n"
				sql = sql + "insert into @p5 values(N'maxfiles',N'" + args.maxfiles + "')\n"
				sql = sql + "exec dbo.usp_InsertMachineCommand @MachinesPKList=@p1,@Type=256,@Comment=N'Download RSA rmt_0_downloader_windows',@IsAutomatic=0,@CommandParams=@p5"

				try:
					cursor.execute(sql)
					db.commit()
				except Exception as e:
					print('[!] Error: {}'.format(e))

				#Wait
				if g_debug:
					print '    [+] Sleeping .05 seconds'
					print('{:.1%} Complete'.format(float(count) / float(total_files/args.batch)))
				sleep(0.05)
	#Close the DB
	db.close()

if __name__ == '__main__':
	main()
