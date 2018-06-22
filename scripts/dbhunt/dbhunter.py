#!/usr/bin/python
# DBHunter
# Author: RSA IR <firstresponse@rsa.com>
#
# Description: For each SQL file in the supplied directory (traversed recursively), run the SQL Query
# and return the requested data in a CSV
#
# Example
# >python dbhunter.py -d <SQLDir> -o <OutputDir> --progressbar
# 100%|#######################################| 23/23 [4:59:25<00:00, 182.96s/it]
#
# Change Log
# .1-.5	01May2016 - Initial Development
# .6	06Oct2016 - Added functionality to read SQL files recursively from directory provided
# .7	20Oct2016 - Changed Error Handling to Warn on no data return instead of Error
# .8	08Nov2016 - Modified so that recursive directory traversal was optional
# .9	08Nov2016 - Prompt for password if not specified on command line
# .10	14Nov2016 - Fixed bug with --progressbar option
# .11	01May2017 - Switched to using unicodecsv for writing output
# .12	22Jun2017 - Added option to connecting to db via ssl (if enabled on db)
#
# TODO
# Allow specified time range for tracking events (e.g. last 24 hours)
# MultiThreaded? (add sql to process to list, remove when thread starts processing?)
# 
# NOTE
# for systems with Instance names use -s <servername>\<instancename>, for servers with different port use -s <servername>,<port>, 
# for systems with Instance name and non standard port use -s <servername>\<instancename>,<port>
# e.g. -s localhost\sql1,52000

import argparse
import os
import pyodbc
import csv
from datetime import datetime
import sys
import timeit
import unicodecsv
#from cStringIO import StringIO
g_debug = False

def write_csv_unicode(output,directory,filepath):
	global g_debug
	#print myfile + '_' + str(datetime.now().strftime("%Y%m%d-%H%M%S")) + '.csv'
	mydate = str(datetime.now().strftime("%Y%m%d-%H%M%S"))
	#outfile = myfile + '_' + mydate + '.csv'

	#chomp end of file
	mydir, myfile = os.path.split(filepath)
	outfile = directory + mydate + '_' + myfile + '.csv'
	if g_debug:
		print('[+] Writing output to {}'.format(outfile))
	with open(outfile, 'ab+') as f:
		csv_writer = unicodecsv.writer(f, encoding='utf-8')
		for row in output:
			#csv_writer.writerow(i.decode('utf-8') )
			#print i
			csv_writer.writerow(row)
	return

def write_csv(output,directory,filepath):
	global g_debug
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

def Run_SQL(db,filename):
	global g_debug
	try:
		txt = open(filename, 'rb')
	except IOError:
		raise Exception("Could not read file:" + filename)
		#raise Exception("[-] Error: Could not read file:" + filename)
	else:
		if g_debug:
			print('[+] Processing {}'.format(filename))
			start_time = timeit.default_timer()

		#print txt.read()
		#Setup Cursor
		cursor = db.cursor()

		#setup Query
		cursor.execute(txt.read())
		list = cursor.fetchall()

		if g_debug:
			elapsed = timeit.default_timer() - start_time
			print('[+] Processed SQL in {} Seconds'.format(str(elapsed)))
		if len(list) > 0:
			columns = [column[0] for column in cursor.description]
			list.insert(0,columns)
			return list
		else:
			raise Exception("[-] Warning: " + filename + " returned no data")
			#raise Warning(filename + " returned no data")
			#print('[-] Warning: {}' + filename + " returned no data")


def main():
	parser = argparse.ArgumentParser(description='For each SQL file in the supplied directory, script run the SQL Query and return the requested Data in a CSV')
	parser.add_argument('-d','--dir', help='Directory where .SQL files are stored', metavar='<directory>', required=True)
	parser.add_argument('-u','--user', help='Username for SQL Database. Default: Windows Credentials', metavar='<user>')
	parser.add_argument('-p','--pass', dest='passwd', help='Password for SQL Database. (If user specified with no pass then you will be prompted for the pass)', metavar='<password>')
	parser.add_argument('-s','--server', help='Hostname or IP for SQL Server. Default: localhost', metavar='<hostname or IP>', default='LOCALHOST')
	parser.add_argument('-db','--database', help='ECAT database', metavar='<database>', default='ECAT$PRIMARY')
	parser.add_argument('-o','--output', help='Output Directory', metavar='<output_dir>', default=os.getcwd())
	parser.add_argument('-r','--recursive', help='Recursively traverse directory for .sql files', action='store_true', default=False)
	parser.add_argument('--ssl', help='Use SSL', action='store_true', default=False)
	parser.add_argument('--debug', help='Enable Debug Messages', action='store_true', default=False)
	parser.add_argument('--progressbar', help='Include Progress bar (requires tqdm)', action='store_true', default=False)

	args = parser.parse_args()

	global g_debug
	g_debug = args.debug

	### Handle directory
	#Check if directory exists
	if not (os.path.isdir(args.dir)):
		parser.error('Directory does not exist.')

	if not (os.path.isdir(args.output)):
		parser.error('Output Directory does not exist.')

	#Check if dirs end with OS path separator and add if not
	if not args.dir.endswith(os.path.sep):
		args.dir = args.dir + os.path.sep
	if not args.output.endswith(os.path.sep):
		args.output = args.output + os.path.sep

	#Recursively traverse directories or just look in single dir if -r not specified
	if (args.recursive):
		#Recursive directory
		filelist = []
		for dirpath, dirs, files in os.walk(args.dir):
		  for filename in files:
			fname = os.path.join(dirpath,filename)
			if fname.lower().endswith('.sql'):
				filelist.append(fname)
	else:
		filelist = []
		for filename in os.listdir(args.dir):
			fname = os.path.join(args.dir,filename)
			if fname.lower().endswith('.sql'):
				filelist.append(fname)

	#Check if only user is set and prompt for password
	if ((args.user) and (args.passwd is None)):
		import getpass
		print "Enter password: "
		args.passwd = getpass.getpass()

	#Check if password is set
	if ((args.user is None) and (args.passwd)):
		parser.error("-p Password specified but -u User not assigned")


	#Build query to connect to DB
	if args.ssl:
		if args.user and args.passwd:
			conn = 'DRIVER={};SERVER={};DATABASE={};UID={};PWD={};Encrypt=yes;TrustServerCertificate=YES'.format('{ODBC Driver 13 for SQL Server}', args.server, args.database, args.user, args.passwd)
		else:
			conn = 'DRIVER={};SERVER={};DATABASE={};Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=YES'.format('{ODBC Driver 13 for SQL Server}', args.server, args.database)
	else:
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
	if args.progressbar:
		try:
			from tqdm import tqdm
		except ImportError:
			print('This script requires the tqdm module to print a progress bar. pip install tqdm (https://pypi.python.org/pypi/tqdm) or omit --progressbar')
			quit()

		for file in tqdm(filelist):
			try:
				output = Run_SQL(db,file)
			except Exception as e:
				if g_debug:
					if '[-]' not in str(e.args):
						print(' [-] Error: {}'.format(e))
					else:
						print('{}'.format(e))
			else:
				if g_debug:
					print('[+] Processed {}'.format(args.file))
				write_csv_unicode(output,args.output,file)
	else:
		for file in filelist:
			try:
				output = Run_SQL(db,file)
			except Exception as e:
				if g_debug:
					if '[-]' not in str(e.args):
						print(' [-] Error: {}'.format(e))
					else:
						print('{}'.format(e))
			else:
				if g_debug:
					print('[+] Processed {}'.format(file))
				write_csv_unicode(output,args.output,file)

	#Close the DB
	db.close()

if __name__ == '__main__':
	main()
