#!/usr/bin/python
#
# Author: RSA IR <firstresponse@rsa.com>
#
# Description: RSA Download Files from Machine / File Tuple list via NetWitness Endpoint (ECAT)
#
# Notes: Requires permission to issue exec commands (GRANT EXECUTE ON dbo.usp_InsertMachineCommand TO [userName])
#
#
# Change Log
# .2	14Jun2017 - Initial Development
#
# TODO
# Determine Interaction with a multiserver environment
# Add option to only download from systems which have not yet been downloaded
# Fix percentage
# Use output from RMT format... maybe?

import argparse
import pyodbc
import math
from time import sleep
from tqdm import *

global g_debug



def main():
	parser = argparse.ArgumentParser(description='Download files using NWEndpoint from a supplied list of files')
	parser.add_argument('-f','--filename', help='Input list of machinename/files to download', required=True)
	#parser.add_argument('-n','--new', help='Download from new systems only (No previous download)',action='store_true', default=False)
	parser.add_argument('-m','--maxfiles', help='Maximum number of files to download when wildcard (*) is used. Default 100', default='100')
	#parser.add_argument('-b','--batch', help='Number of systems to request download from per batch. Default 100', default='100')
	parser.add_argument('-u','--user', help='Username for SQL Database. Default: Windows Credentials', metavar='<user>')
	parser.add_argument('-p','--pass', dest='passwd', help='Password for SQL Database. (If user specified with no pass then you will be prompted for the pass)', metavar='<password>')
	parser.add_argument('-s','--server', help='Hostname or IP for SQL Server. Default: localhost', metavar='<hostname or IP>', default='LOCALHOST')
	parser.add_argument('-db','--database', help='NWE (ECAT) Database', metavar='<database>', default='ECAT$PRIMARY')
	parser.add_argument('-c','--comment', help='Comment for Download', metavar='<comment>', default='RSA File Download')
	parser.add_argument('--debug', help='Enable Debug Messages', action='store_true', default=False)

	args = parser.parse_args()

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

	#Read in TupleList
	try:
		with open(filename) as f:
			DownloadList = f.read().splitlines()
	except IOError:
		raise Exception("[!] Could not read file:" + filename)
	else:
		if g_debug:
			print('[+] Processing {}'.format(filename))
			print('[+] MachineFileList Length {}'.format(len(DownloadList)))
			#print('[+] MaxFiles {}'.format(args.maxfiles))
		total_files = len(DownloadList)
		f.close()
	
	#print DownloadList
	#for entry in DownloadList:
	#	print entry.split(',')[0]
		#print entry

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
		
	#Get Machine List
	txt = "select PK_Machines,MachineName from dbo.Machines where dbo.Machines.MarkedAsDeleted = 0"

	#Setup Cursor
	cursor = db.cursor()

	#Get List of Systems
	cursor.execute(txt)
	rows = cursor.fetchall()

	#print rows
	Machines = {}
	for row in rows:
		#print row
		Machines[row[1].rstrip().encode('ascii','ignore').lower()] = row[0]
	#MachinesDict = dict((rows[0],rows[1]) for row in rows)
	#print Machines
	#print Machines['GOLDSYSTEM1'.lower()]
	
	count = 0
	if g_debug:
		count += 1

		for entry in DownloadList:
			sql = "declare @p1 dbo.uty_PrimaryKeyList\n"
			machine = entry.split(',')[0].lower()
			if g_debug:
				print '[+] Processing: ' + entry.lower()
			try:
				machineid = Machines[machine]
				#print machineid
			except KeyError, e:
				print '[!] Error ' + machine + ' Not Found!'
			else:
				sql += "insert into @p1 values(" + str(machineid) + ")\n"

				sql += "declare @p5 dbo.uty_MachineCommandParams\n"
				sql += "insert into @p5 values(N'Path',N'" + str(entry.split(',')[1]) + "')\n"
				sql += "insert into @p5 values(N'maxfiles',N'" + args.maxfiles + "')\n"
				sql += "exec dbo.usp_InsertMachineCommand @MachinesPKList=@p1,@Type=256,@Comment=N'" + args.comment + "',@IsAutomatic=0,@CommandParams=@p5"

				#print sql
				#exit()
				try:
					cursor.execute(sql)
					db.commit()
				except Exception as e:
					print('[!] Error: {}'.format(e))

				#Wait
				if g_debug:
					#print '[+] Sleeping .05 seconds'
					print('{:.1%} Complete'.format(float(count) / float(total_files)))
				sleep(0.05)
	else:

		for entry in tqdm(DownloadList):
			sql = "declare @p1 dbo.uty_PrimaryKeyList\n"
			machine = entry.split(',')[0].lower()
			if g_debug:
				print '[+] Processing: ' + entry.lower()
			try:
				machineid = Machines[machine]
				#print machineid
			except KeyError, e:
				print '[!] Error ' + machine + ' Not Found!'
			else:
				sql += "insert into @p1 values(" + str(machineid) + ")\n"

				sql += "declare @p5 dbo.uty_MachineCommandParams\n"
				sql += "insert into @p5 values(N'Path',N'" + str(entry.split(',')[1]) + "')\n"
				sql += "insert into @p5 values(N'maxfiles',N'" + args.maxfiles + "')\n"
				sql += "exec dbo.usp_InsertMachineCommand @MachinesPKList=@p1,@Type=256,@Comment=N'" + args.comment + "',@IsAutomatic=0,@CommandParams=@p5"

				#print sql
				#exit()
				try:
					cursor.execute(sql)
					db.commit()
				except Exception as e:
					print('[!] Error: {}'.format(e))

				#Wait
				if g_debug:
					#print '[+] Sleeping .05 seconds'
					print('{:.1%} Complete'.format(float(count) / float(total_files)))
				sleep(0.05)
	#Close the DB
	db.close()

if __name__ == '__main__':
	main()
