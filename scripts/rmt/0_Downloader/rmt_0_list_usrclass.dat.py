#!/usr/bin/python
# DBHunter
# Author: RSA IR <firstresponse@rsa.com>
# Version: .10
#
# Description: For each SQL file in the supplied directory (traversed recursively), run the SQL Query
# and return the requested data in a CSV
#
# Example
# >python dbhunter.py -d <SQLDir> -o <OutputDir> --progressbar
# 100%|#######################################| 23/23 [4:59:25<00:00, 182.96s/it]
#
# Change Log
# 01May2016 - Initial Development
# 06Oct2016 - Added functionality to read SQL files recursively from directory provided
# 20Oct2016 - Changed Error Handling to Warn on no data return instead of Error
# 08Nov2016 - Modified so that recursive directory traversal was optional
# 08Nov2016 - Prompt for password if not specified on command line
# 14Nov2016 - Fixed bug with --progressbar option
#
# TODO
# Handle Unicode Better
# Allow specified time range for tracking events (e.g. last 24 hours)

import argparse
import os
import pyodbc
import csv
from datetime import datetime
import sys
import timeit
#import unicodecsv
#from cStringIO import StringIO
global g_debug
g_debug = False

def write_csv(output,directory,filepath):
	#print myfile + '_' + str(datetime.now().strftime("%Y%m%d-%H%M%S")) + '.csv'
	mydate = str(datetime.now().strftime("%Y%m%d-%H%M%S"))
	#outfile = myfile + '_' + mydate + '.csv'

	#chomp end of file
	mydir, myfile = os.path.split(filepath)
	outfile = directory + mydate + '_' + myfile + '.csv'
	if g_debug:
		print('[+] Writing output to {}'.format(outfile))
	try:
		csv_writer = csv.writer(file(outfile, 'wb'), delimiter=',')
		for row in output:
			#row.strip().encode("utf-8")
			try:
				csv_writer.writerow(row)
				#row = row.encode('ascii')
				#csv_writer.writerow(row)
			except IOError, err:
				if g_debug:
					print('[-] Error writing row: {}'.format(str(err)))
			except UnicodeEncodeError, err:
				if g_debug:
					print('[-] Error writing row: {}'.format(str(err)))
			except:
				if g_debug:
					print "[-] Unexpected Error writing row:", sys.exc_info()[0]

	except IOError, err:
		if g_debug:
			print('[-] Error writing output file: {}'.format(str(err)))
		return
	except:
		if g_debug:
			print "[-] Unexpected error:", sys.exc_info()[0]
		return

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


def main():
	parser = argparse.ArgumentParser(description='Get List of NTUser Locations')
	#parser.add_argument('-d','--dir', help='Directory where .SQL files are stored', metavar='<directory>', required=True)
	parser.add_argument('-u','--user', help='Username for SQL Database. Default: Windows Credentials', metavar='<user>')
	parser.add_argument('-p','--pass', dest='passwd', help='Password for SQL Database. (If user specified with no pass then you will be prompted for the pass)', metavar='<password>')
	parser.add_argument('-s','--server', help='Hostname or IP for SQL Server. Default: localhost', metavar='<hostname or IP>', default='LOCALHOST')
	parser.add_argument('-db','--database', help='ECAT database', metavar='<database>', default='ECAT$PRIMARY')
	#parser.add_argument('-o','--output', help='Output Directory', metavar='<output_dir>', default=os.getcwd())
	#parser.add_argument('-r','--recursive', help='Recursively traverse directory for .sql files', action='store_true', default=False)
	parser.add_argument('--debug', help='Enable Debug Messages', action='store_true', default=False)
	#parser.add_argument('--progressbar', help='Include Progress bar (requires tqdm)', action='store_true', default=False)

	args = parser.parse_args()


	g_debug = args.debug



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

	if g_debug:
		print '\n'

	#Process SQL


	query = """
SELECT DISTINCT path from dbo.paths
WHERE path LIKE N'%:\Users\%'
AND path NOT LIKE N'HKEY_CURRENT_USER\%'"""
	try:
		output = Run_SQL(db,query)
	except Exception as e:
		if g_debug:
			if '[-]' not in str(e.args):
				print(' [-] Error: {}'.format(e))
			else:
				print('{}'.format(e))
	else:
		if g_debug:
			print('[+] Processed Query')
		#print output
		#write_csv(output,args.output,file)
		result = list()
		for i in output:
			s = i[0].encode('ascii','ignore')
			s = s.split('\\')
			#s = str(i[0]).split('\\')
			result.append(s[0] + '\\' + s[1] + '\\' + s[2] + '\\AppData\\Local\\Microsoft\\Windows\\USRCLASS.DAT')
			#print item[0]
		result = sorted(set(result))
		for i in result:
			print i
	#Close the DB
	db.close()

if __name__ == '__main__':
	main()
