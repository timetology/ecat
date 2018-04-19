#!/usr/bin/python
# 
# Author: RSA IR <firstresponse@rsa.com>
# 
# Description: Crawl NetWitness Endpoint looking for possible locations of USRCLASS.DAT and then download them
#
# Example
#
# Change Log
# .1	01Feb2017 - Initial Development
# .2	15Feb2017 - Cleanup
# TODO
# Provide list of machines to only download from

import argparse
import os
import pyodbc
from datetime import datetime
import sys
import timeit
from tqdm import *
from time import sleep
global g_debug
g_debug = False


def Run_SQL(db,query):
	if g_debug:
		print('[+] Processing SQL')
		start_time = timeit.default_timer()

	#print txt.read()
	#Setup Cursor
	cursor = db.cursor()

	#setup Query
	cursor.execute(query)
	list = cursor.fetchall()

	if g_debug:
		elapsed = timeit.default_timer() - start_time
		print('[+] Processed SQL in {} Seconds'.format(str(elapsed)))
	if len(list) > 0:
		#columns = [column[0] for column in cursor.description]
		#list.insert(0,columns)
		return list
	else:
		raise Exception("[-] Warning: query returned no data")
		#raise Warning(filename + " returned no data")
		#print('[-] Warning: {}' + filename + " returned no data")
		
def getMachineList(db):
	if g_debug:
		print "[+] Retrieving Machine List"
	txt = "select PK_Machines from dbo.Machines where dbo.Machines.FK_OSTypes = 1 AND dbo.Machines.MarkedAsDeleted = 0"
	try:
		machinelist = Run_SQL(db,txt)
	except Exception as e:
		print(' [!] Error: {}'.format(e))
		exit()
	else:
		return machinelist
	
def DownloadFile(db,machine,filename,maximumFiles):
	if g_debug:
		print('[+]Downloading {} {}'.format(machine,filename))
	cursor = db.cursor()
	sql_header = "declare @p1 dbo.uty_PrimaryKeyList\n"

	sql_header = sql_header + "insert into @p1 values(" + str(machine) + ")\n"


	sql = sql_header
	sql = sql + "declare @p5 dbo.uty_MachineCommandParams\n"
	sql = sql + "insert into @p5 values(N'Path',N'" + filename + "')\n"
	sql = sql + "insert into @p5 values(N'MaximumFiles',N'" + maximumFiles + "')\n"
	sql = sql + "exec dbo.usp_InsertMachineCommand @MachinesPKList=@p1,@Type=256,@Comment=N'Download RSA File Download',@IsAutomatic=0,@CommandParams=@p5"
	
	try:
		cursor.execute(sql)
		db.commit()
	except Exception as e:
		print('[!] Error: {}'.format(e))
		
def processPaths(db,machinelist):
	#For each machine get it's paths
	for m in tqdm(machinelist):
		txt = """
SELECT DISTINCT pa.Path from
[dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK)
INNER JOIN [dbo].[Paths] as [pa] WITH(NOLOCK) ON [pa].[PK_Paths] = mp.FK_Paths
WHERE mp.FK_Machines = '"""
		txt += str(m[0])
		txt += """' AND 
pa.path LIKE N'%:\Users\%'
AND pa.path NOT LIKE N'HKEY_CURRENT_USER\%'"""

		try:
			output = Run_SQL(db,txt)
		except Exception as e:
			if g_debug:
				print(' [!] Error: {}'.format(e))
		else:
			dirlist = list()
			for o in output:
				s = o[0].encode('ascii','ignore')
				s = s.split('\\')
				dirlist.append(s[0] + '\\' + s[1] + '\\' + s[2] + '\\AppData\\Local\\Microsoft\\Windows\\USRCLASS.DAT')
			dirlist = sorted(set(dirlist))
			for i in dirlist:
				if g_debug:
					print '[+] Processing: ' + str(m[0]) + "," + str(i)
				try:
					DownloadFile(db,str(m[0]),str(i),'1')
				except:
					print('[!] Error: {}'.format(e))
				else:
					sleep(.1)
def main():
	parser = argparse.ArgumentParser(description='Download USRCLASS.DAT')
	parser.add_argument('-u','--user', help='Username for SQL Database. Default: Windows Credentials', metavar='<user>')
	parser.add_argument('-p','--pass', dest='passwd', help='Password for SQL Database. (If user specified with no pass then you will be prompted for the pass)', metavar='<password>')
	parser.add_argument('-s','--server', help='Hostname or IP for SQL Server. Default: localhost', metavar='<hostname or IP>', default='LOCALHOST')
	parser.add_argument('-db','--database', help='ECAT database', metavar='<database>', default='ECAT$PRIMARY')
	parser.add_argument('--debug', help='Enable Debug Messages', action='store_true', default=False)

	args = parser.parse_args()

	g_debug = args.debug

	#Check if only user is set and prompt for password
	if ((args.user) and (args.passwd is None)):
		import getpass
		print "Enter password: "
		args.passwd = getpass.getpass()

	#Check if password is set
	if ((args.user is None) and (args.passwd)):
		parser.error("-p <Password> specified but -u <User> not assigned")

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
	else:
		#Get Machine List
		machinelist = getMachineList(db)

		#Process Paths & Download
		processPaths(db,machinelist)
		
		db.close()

if __name__ == '__main__':
	main()
