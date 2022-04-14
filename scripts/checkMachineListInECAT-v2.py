#!/usr/bin/python
#

import argparse
import pyodbc

global g_debug


def main():
	parser = argparse.ArgumentParser(description='Check if list of systems is in ecat')
	parser.add_argument('-f','--filename', help='Input list of machinenames to compare', required=True)
	parser.add_argument('-u','--user', help='Username for SQL Database. Default: Windows Credentials', metavar='<user>')
	parser.add_argument('-p','--pass', dest='passwd', help='Password for SQL Database. (If user specified with no pass then you will be prompted for the pass)', metavar='<password>')
	parser.add_argument('-s','--server', help='Hostname or IP for SQL Server. Default: localhost', metavar='<hostname or IP>', default='LOCALHOST')
	parser.add_argument('-db','--database', help='ECAT database', metavar='<database>', default='ECAT$PRIMARY')
	parser.add_argument('--count', help='Print count of matches, not the list of matches.', action='store_true', default=False)
	#parser.add_argument('--debug', help='Enable Debug Messages', action='store_true', default=False)
	args = parser.parse_args()

	g_debug = args.count
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
		with open(filename, 'rb') as f:
			machineCheckList = f.read().splitlines()
	except IOError:
		raise Exception("[!] Could not read file:" + filename)
	else:
		if g_debug:
			print('List of Machines to Match: {}'.format(filename))
			print('Number of Machines to Match: {}'.format(len(machineCheckList)))
			exit()
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

	#Setup Cursor
	cursor = db.cursor()

	#Get List of Systems
	hosts = "select MachineName from dbo.Machines where dbo.Machines.MarkedAsDeleted = 0"
	cursor.execute(hosts)
	rows = cursor.fetchall()
	hostnames = []
	for row in rows:
		hostnames.append(row[0])
	total_files = len(hostnames)
	if g_debug:
		print('Total Number of Systems in ECAT: ' + str(len(rows)))

	#print(machineCheckList)
	#print(hostnames)
	#matches = set(machineCheckList).intersection(hostnames)
	for item in machineCheckList:
		if item in hostnames:
			print(item + ',Under Investigation')
		else:
			print(item + ',Not Found')
	#if g_debug:
	#	print('Number of Matches: ' + str(len(matches)))
	#	exit()
	#for match in matches:
	#	print(match)
	
	#Close the DB
	db.close()

if __name__ == '__main__':
	main()
