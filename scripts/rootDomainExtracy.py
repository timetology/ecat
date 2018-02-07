#!/usr/bin/python
import tldextract
import argparse

def main():
	parser = argparse.ArgumentParser(description='Root Domain Extractor')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-f','--file', help='File list of Domains', metavar='<file>')
	group.add_argument('-u','--url', help='URL list of Domains', metavar='<url>')
	parser.add_argument('-s','--sql', help='Output in ECAT SQL Format', action='store_true', default=False)
	args = parser.parse_args()

	if args.sql:
		print """SELECT
mn.MachineName, 
na.FirstConnectionUTC, 
na.LastConnectionUTC, 
pn.Filename, 
sfn.Filename, 
na.Port, 
dom.Domain, 
na.IP, 
na.UserAgent, 
LaunchArguments

FROM
    [dbo].[mocNetAddresses] AS [na] WITH(NOLOCK)

    LEFT JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [na].[FK_MachineModulePaths])
    LEFT JOIN [dbo].[FileNames] AS [sfn] WITH(NOLOCK) ON ([sfn].[PK_FileNames] = [mp].[FK_FileNames])
    LEFT JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [na].[FK_Machines]
    LEFT JOIN [dbo].[Filenames] AS [pn] WITH(NOLOCK) ON ([pn].[PK_FileNames] = [na].[FK_FileNames__Process])
    LEFT JOIN [dbo].[Domains] AS [dom]  WITH(NOLOCK) ON ([dom].[PK_Domains] = [na].[FK_Domains__DomainHost])
    LEFT JOIN [dbo].[LaunchArguments] as [sla] WITH(NOLOCK) ON ([sla].[PK_LaunchArguments] = [na].[FK_LaunchArguments])

WHERE
[dom].[Domain] <> ''"""
	if args.file:
		with open(args.file) as f:  
			line = f.readline()
			count = 1

			while line:
				extracted = tldextract.extract(line)
				if args.sql:
					print "AND [dom].[Domain] LIKE N'%" + '{}.{}'.format(extracted.domain, extracted.suffix) + "'"
				else: 
					print '{}.{}'.format(extracted.domain, extracted.suffix)
				line = f.readline()
				count += 1
	if args.url:
		import urllib2
		count = 0
		for line in urllib2.urlopen(args.url):
			extracted = tldextract.extract(line)
			if args.sql:
				print "AND [dom].[Domain] LIKE N'%" + '{}.{}'.format(extracted.domain, extracted.suffix) + "'"
			else: 
				print '{}.{}'.format(extracted.domain, extracted.suffix)
			count += 1


if __name__ == '__main__':
	main()
