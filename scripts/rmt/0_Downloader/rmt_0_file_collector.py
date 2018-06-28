from os.path import exists, join
from os import pathsep
from string import split
import argparse
import os
import pyodbc
import shutil
import mmap

# Function to search downloaded files by artifact regex
def find_SQL_file(db, filename):
	cursor = db.cursor()
	query = """\
	SELECT pa.path + fn.filename AS LOCATION

FROM
   [dbo].[MachineDownloaded] AS [md] WITH(NOLOCK)
    INNER JOIN [dbo].[Machines] AS [ma] WITH(NOLOCK) ON ([md].[FK_Machines] = [ma].[PK_Machines])
   INNER JOIN [dbo].[FileNames] AS [fn] WITH(NOLOCK) ON ([fn].[PK_FileNames] = [md].[FK_FileNames__RelativeFileName])
   INNER JOIN [dbo].[Paths] AS [pa] WITH(NOLOCK) ON ([pa].[PK_Paths] = [md].[FK_Paths__RelativePath])

WHERE fn.filename LIKE '"""
	if (filename == "SYSTEM"):
		argument = "system[_]%nm[_]'"
	elif (filename == "AMCACHE"):
		argument = "amcache[_]%nm[_]'"
	elif (filename == "SECURITY"):
		argument = "security[_]%nm.evtx[_]'"
	elif (filename == "SOFTWARE"):
		argument = "software[_]%nm[_]'"
	elif (filename == "NTUSER"):
		argument = "ntuser[_]%nm.dat[_]'"
	elif (filename == "PREFETCH"):
		argument = "%nm.pf[_]'"
	elif (filename == "MFT"):
		argument = "$MFT[_]%nm[_]'"
	elif (filename == "EVTX"):
		argument = "%[_]%nm.evtx[_]'"
	elif (filename == "JUMPLIST"):
		argument = "%nm.%Destinations-ms[_]'"
	else:
		raise Exception('--Not a Valid or Supported Artifact.')
	
	# Add applicable regex to SQL statement
	query = query + argument
	# Run SQL query
	cursor.execute(query)
	list = cursor.fetchall()
	# Check to make sure something came back
	if len(list) >= 1:
		cursor.close()
		return list
	elif len(list) < 1:
		raise Exception('--No Artifacts Downloaded or Found')
		
# Function to copy downloaded files from ECAT Files directory to analyst specified directory
def copy_files(src,dst):
	try:
		shutil.copy(src,dst)
	except Exception as e:
		print('[-] Error copying file {} to {}: {}'.format(src,dst,e))
		
# Main function
def main():
	parser = argparse.ArgumentParser(description='For an artifact type, will copy all downloaded copies of artifact to working directory for analysis.')
	parser.add_argument('-a','--artifact', help='Artifact to Collect: SYSTEM, AMCACHE, SECURITY', metavar='<artifact>')
	parser.add_argument('-d','--dir', help='Directory to Store Files', metavar='<dir>')
	parser.add_argument('-f','--files', dest='fileloc', help='Path to ECAT Files Directory, including trailing slash: (C:\ECAT\Server\Files\)', metavar='<fileloc>', default='C:\\ECAT\\Server\\Files')
	parser.add_argument('-db','--database', help='ECAT Database', metavar='<database>', default='ECAT$PRIMARY')
	parser.add_argument('-u','--user', help='Username for SQL Database. Default: Windows Credentials', metavar='<user>')
	parser.add_argument('-p','--pass', dest='passwd', help='Password for SQL Database. (If user specified with no pass then you will be prompted for the pass)', metavar='<password>')
	parser.add_argument('-s','--server', help='Hostname or IP for SQL Server. Default: localhost', metavar='<server>', default='LOCALHOST')
	args = parser.parse_args()

	# Open file for artifact tracking across multiple executions.
	# File is considered 'downloaded' not when ECAT downloads from host, but when artifact
	# is collected for evidence.  This ensures that the artifacts that are being tracked are
	# artifacts that the analyst 'should' have, so effectively performs two checks:
	#	1. The artifact was downloaded from the host
	#	2. The artifact was extracted from the files directory for collection, archival, and analysis
	tracking = open("./downloaded_artifacts.txt","a+")
	check = mmap.mmap(tracking.fileno(), 0, access=mmap.ACCESS_READ)
	path = args.fileloc
	conn = 'DRIVER={};SERVER={};DATABASE={};Trusted_Connection=yes'.format('{SQL Server}', args.server, args.database)
	try:
		db = pyodbc.connect(conn)
	except pyodbc.Error as err:
		parser.error(err)

	if (args.artifact):
		try:
			filelist = find_SQL_file(db,args.artifact)
			total_files = len(filelist)
		except Exception as e:
			print('[-] Error looking up {} {}'.format(args.artifact,e))
		else:
			for file in filelist:
				full_path = path + str(file[0])
				# Check to make sure we haven't already copied the artifact.  If so, do not copy.
				if check.find(full_path) != -1:
					print('File {} already downloaded. Skipping...'.format(full_path))
				else:
					tracking.write("%s\r\n" % full_path)
					print('Copying {} to {}'.format(full_path,args.dir))
					copy_files(full_path,args.dir)
					
		print('Total Records: {}'.format(total_files))
	db.close()
if __name__ == '__main__':
	main()