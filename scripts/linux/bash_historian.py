# Bash Historian
# Author: RSA IR <firstresponse@rsa.com>
# Version: .2
# Description
# Frequency Analysis (default) or Uniq list
# Can accept input from RSA DBHunt Bash History or any list of items where frequency or uniq is needed.
# Todo
# Command (COUNT)
#   - User (COUNT OF THAT COMMAND)
#-Command(Count)
#  - User ( Count)
#  - Hostname ( Count)
# Also maybe handle grep/vgrep or maybe just do that ahead of time.
# Handle the timestamps from bash history.
# Handle any arbitrary input csv


from collections import Counter
#from collections import OrderedDict
import argparse
import os

global g_debug


def main():
	parser = argparse.ArgumentParser(description='Bash Historian Frequency analysis (default) or Uniq list')
	parser.add_argument('-i','--input', help='File Containing Bash History',metavar='<input_file>', required=True)
	parser.add_argument('-e','--ecat', help='Output is from ECAT DBHUNT Bash_History.sql and Prints User,Command frequency', action='store_true', default=False)
	parser.add_argument('--user', help='Use with --ecat and only prints user frequency', action='store_true', default=False)
	parser.add_argument('--command', help='Use with --ecat and only command frequency', action='store_true', default=False)
	parser.add_argument('-f','--freq', help='Frequency Analysis', action='store_true', default=False)
	parser.add_argument('-u','--uniq', help='Unique list of values', action='store_true', default=False)
	parser.add_argument('-o','--output', help='Output Directory', metavar='<output_dir>', default=os.getcwd())
	#parser.add_argument('-c','--customcsv', help='Custom CSV input', metavar='<Column selection(s)>')
	#parser.add_argument('-g','--grep', help='Search for term (grep)')
	#parser.add_argument('-v','--vgrep', help='Non-matching terms (grep -v)')
	parser.add_argument('--debug', help='Enable Debug Messages', action='store_true', default=False)

	args = parser.parse_args()

	if args.freq and args.uniq:
		parser.error('Frequency (-f) and Uniques (-u) are mutually exclusive.')
		exit()
	#if args.freq is None and args.uniq is None:
	#	args.freq = True

	if (args.user or args.command and not args.ecat):
		args.ecat = True


	g_debug = args.debug

	### Handle directory
	if not (os.path.isdir(args.output)):
		parser.error('Output Directory does not exist.')

	#Check if dirs end with OS path separator and add if not
	if not args.output.endswith(os.path.sep):
		args.output = args.output + os.path.sep

	#Read in Bash History
	try:
		with open(args.input) as f:
			bashhistory = f.read().splitlines()
	except IOError:
		raise Exception("[!] Could not read file:" + args.input)
	else:
		if g_debug:
			print('[+] Processing {}'.format(args.input))
			print('[+] Bash History Length {}'.format(len(bashhistory)))
		f.close()

	#If it's from the ECAT DBHUNT OUTPUT then normalize
	if args.ecat:
		if args.user:
			i = 0
			for line in bashhistory:
				try:
					bashhistory[i] = line.split(',')[1] #Split by comma and return only the second to last element
				except IndexError as e:
					if args.debug:
						print "IndexError Exception: " + str(e)
						print line
						print line.split(',')
				i += 1
		elif args.command:
			i = 0
			for line in bashhistory:

				bashhistory[i] = line.split(',')[-1] #Split by comma and return only the last element
				i += 1
		else:
			i = 0
			for line in bashhistory:
				bashhistory[i] = ','.join(line.split(',')[-2:]) #Split by comma and return last two elements
				i += 1

	if args.uniq:
		# equal to list(set(words))
		for line in Counter(bashhistory).keys():
			print line
	else:
		# counts the elements' frequency
		myfreq = []
		myfreq = Counter(bashhistory).items()
		myfreq.sort(key=lambda tup:tup[1],reverse=True)
		for line in myfreq:
			print line[0] + ',' + str(line[1])







if __name__ == '__main__':
	main()