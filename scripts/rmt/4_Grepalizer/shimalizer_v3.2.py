#!/usr/bin/python
# The Shimalizer
# 
# Script: Shimalizer v3.1
# Author: H Bojaxhi
# Date:   February 2015
#
# Changelog:
# Version 3.0 - 18 Nov 15
#       Rewritten into Python by B Baskin
# Version 3.1 - 29 Apr 16
#       Added global g_timeformat to adjust to changes in ShimCacheParser - S Brzozowski
# Version 3.1.1 - 17 May 16
#       Changed file output from write to append to store all IOC regex results.
#       Added basic debugging
#       ioc-terms.txt and ioc-dates.txt are literal. Don't use quotes!
# Version 3.2 - 24 Jun 16
#       Fixed regex patterns to Real strings to get all results.
#       Fixed groupings when making frequency analysis summary
#
#
# TO-DO
# Better debug output

import argparse
import collections
import csv
import os
import re
import sys

from Registry import Registry

try:
    import ShimCacheParser
except ImportError:
    print 'This script requires the legit ShimCacheParser.py in the same path'
    quit()

g_debug = False
DATE_MDY = "%m/%d/%y %H:%M:%S"
DATE_ISO = "%Y-%m-%d %H:%M:%S"
ShimCacheParser.g_timeformat = DATE_ISO

searches = {r'(tomcat|inetpub|wwwroot|webapps|clientaccess)' : 'webFolders.txt', 
            r'(explorer.exe|iexplore.exe|svchost.exe|ctfmon.exe|dllhost.exe)' : 'reservedNames.txt',
            r'(:\\windows\\.{1,15},)' : 'Windowsfolder.txt',
            r'(\\system32\\.)' : 'sys32folder.txt',
            r'\,([0-9]{2})\,N\/A' : 'LessThan100bytes.txt',
            r'\,([0-9]{3})\,N\/A' : 'Files100-999bytes.txt',
            r'(\.bin,|\.dat,|\.log,|\.gif,|\.txt,|\.jpg,|\.rar,|\.tar,|\.sql,|\.zip,)' : 'interestingExtensions.txt',
            r'(\.tmp,)' : 'tmpExtension.txt',
            r'\\.\....,' : '1char.txt',
            r'\\..\....,' : '2char.txt',
            r'(:\\[a-zA-Z0-9]{1,12}\\[a-zA-Z0-9]*\....,)' : '1deep.txt',
            r'(\\.{1,10}\.bat,)' : 'BATextension.txt'}



def file_exists(fname):
    return os.path.exists(fname) and os.access(fname, os.R_OK)


def TraversePath(directory):
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           yield os.path.abspath(os.path.join(dirpath, f))
        

def write_it(rows, outfile=None):
    # Rewrite of ShimCacheParser's write_it to not overwrite the output file.
    try:
        if not rows:
            print('[-] No data to write...')
            return
        
        if not outfile:
            for row in rows:
                print(''.join(["%s"%x for x in row]))
        else:
            print('[+] Writing output to {}...'.format(outfile))
            try:
                csv_writer = csv.writer(file(outfile, 'ab'), delimiter=',')
                csv_writer.writerows(rows)
            except IOError, err:
                print('[-] Error writing output file: {}'.format(str(err)))
                return
            
    except UnicodeEncodeError, err:
        print('[-] Error writing output file: {}'.format(err))
        return


def regex_string(regex, entries, negative=False):
    results = []
    for entry in entries:
        matches = re.search(regex, entry, re.IGNORECASE)
        if negative:
            if not matches:
                results.append(entry.strip())
        else:
            if matches:
                results.append(entry.strip())
    return results


def shimalizer_output_cleanup(entries):
    results = []
    filenames = []
    
    # Print header to show Count and Filename
    for entry in entries:
        filenames.append(entry.split(',')[3].lower())
        #.lower ensures that the summary groups by case insensitive

    exe_list = collections.Counter(filenames)
    exe_count_list = collections.OrderedDict(exe_list.most_common())
    
    for fn in exe_count_list.iterkeys():
        results.append('{:4d} {}'.format(exe_count_list[fn], fn))
    
    results.append('=' * 50)
    results = results + entries
    
    return results


def RegistryGetHostname(hive):
    try:
        reg = Registry.Registry(hive)
    except Registry.RegistryParse.ParseException, err:
        print('[!] Error: {}'.format(err))
        return ''
    top_lvl = reg.root().subkeys()
    try:
        for key in top_lvl:
            if 'controlset' in key.name().lower():
                if g_debug:
                    print('[DEBUG] Pulling hostname from file {} and controlset: {}'.format(hive, key.name()))
                cname = reg.open('{}\\Control\ComputerName'.format(key.name()))
                for subkey in cname.subkeys():
                    hostname = str(subkey['ComputerName'].value())
                    if g_debug:
                        print('[DEBUG] Found hostname: {}'.format(hostname))
    except:
        if g_debug:
            print('[DEBUG] Could not find hostname for file: {}'.format(hive))
        return ''
    return hostname


def WriteListToFile(folder, values, filename):
    if values:
        if g_debug:
            print('[DEBUG] {} items written to file: {}'.format(len(values), filename))
        if not os.path.exists(folder):
            os.makedirs(folder)
        fh = open(os.path.join(folder, filename), 'a')
        for value in values:
            fh.write('{}\n'.format(value))
        fh.close()
        print('[+] Notable output written to {}'.format(filename))


def getArgs():
    global g_debug

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', help='Folder containing SYSTEM hives', required=False)
    parser.add_argument('-o', '--output', help='Output folder and CSV name', required=True)
    parser.add_argument('-c', '--csv', help='Import CSV file name', required=False)
    parser.add_argument('--debug', help='Enable debug mode', action='store_true', required=False)
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    if args.debug:
        g_debug = True
    if args.dir and not file_exists(args.dir):
        print '[!] Folder not found: {}'.format(args.dir)
        quit()
    return args


def main():
    print r"""
             / /
          (\/_//`)
           /   '/
          0  0   \
         /        \
        /    __/   \
       /,  _/ \     \_
       `-./ )  |     ~^~^~^~^~^~^~^~\~.
           (   /                     \_}
              |        R S A  /      |
              ;     |         \      /
               \/ ,/           \    |
               / /~~|~|~~~~~~|~|\   |
              / /   | |      | | `\ \
             / /    | |      | |   \ \
            / (     | |      | |    \ \
           /,_)    /__)     /__)   /,_/
     ''''''''''''''''''''''''''''''''''''''''
     '''''''''' The Shimalizer 3.2 ''''''''''
    """

    args = getArgs()
    if not args.csv:
    # No CSV. Create one.
        output_path = os.path.split(os.path.normpath(args.output))[-1]
        output_csv = output_path + '.csv'

        if not file_exists(args.output):
            os.mkdir(args.output)
        
        hives = TraversePath(args.dir)

        for hive in hives:        
            entries = ''
            print('[+] Parsing file: {}'.format(hive))
            try:
                entries = ShimCacheParser.read_from_hive(hive)
                if g_debug:
                    print('[DEBUG] {} Entries found (incuding header row)'.format(len(entries)))
                # Remove the CSV header
                entries.pop(0)
            except:
                if g_debug:
                    print('[DEBUG] Unknown error found within ShimCacheParser.py. Run ShimCacheParser.py directly to see error message.')
                continue
            if not entries:
                if g_debug:
                    print('[DEBUG] No shim entries found within file: {}'.format(hive))
                continue

            hostname = RegistryGetHostname(hive)
            if not hostname:
                print('[!] Error. Hostname not found in SYSTEM hive.')
                continue
            for entry in entries:
                entry.insert(0, hostname)

            write_it(entries, output_csv)


    # Open CSV, either from arg or naturally from previous
    csv_filename = ''
    if args.csv:
        csv_filename = args.csv
    else:
        csv_filename = output_csv

    print('[+] Reading CSV data from {}'.format(csv_filename))
    try:
        shim_entries = open(csv_filename, 'r').readlines()
    except IOError:
        print('[!] Unable to open CSV file: {}'.format(csv_filename))
        quit()

    print('[+] Starting RegEx queries')            
    # Parse through the dictionary of regex's at top of file:
    for regex in searches.iterkeys():
        output_file =  searches[regex]
        results = regex_string(regex, shim_entries)
        if results:
            results = shimalizer_output_cleanup(results)
            WriteListToFile(args.output, results, output_file)

    # The following are negative searches
    regex_temp = "(\\temp\\.)"  # Python RegEx cannot end with literal backslash
    results_temp = regex_string(regex_temp, shim_entries)
    results_temp = regex_string(r'(\{|\_|\-|\~|\()', results_temp, True)
    if results_temp:
        results_temp = shimalizer_output_cleanup(results_temp)
        WriteListToFile(args.output, results_temp, 'tempfolder.txt')

    regex_temp = "\\tmp\\."  # Python RegEx cannot end with literal backslash
    results_temp = regex_string(regex_temp, shim_entries)
    results_temp = regex_string(r'\{|\_|\-|\~|\(', results_temp, True)
    if results_temp:
        results_temp = shimalizer_output_cleanup(results_temp)
        WriteListToFile(args.output, results_temp, 'tempfolder.txt')

    regex_temp = "\.exe,|\.dll,|\.tmp,"  # Python RegEx cannot end with literal backslash
    results_temp = regex_string(regex_temp, shim_entries, True)
    results_temp = regex_string(r'Recycle\.Bin', results_temp, True)
    if results_temp:
        results_temp = shimalizer_output_cleanup(results_temp)
        WriteListToFile(args.output, results_temp, 'suspectExtension.txt')
        
    # The following are searches against text files keywords
    if file_exists('ioc-terms.txt'):
        for keyword in open('ioc-terms.txt', 'r').readlines():
            keyword = keyword.strip()
            results_temp = regex_string(keyword, shim_entries)
            if results_temp:
                print('[*] Found {} of IOC keyword: {}'.format(len(results_temp), keyword))
                WriteListToFile(args.output, results_temp, 'IOC-Results.txt')
                
    if file_exists('ioc-dates.txt'):
        for keyword in open('ioc-dates.txt', 'r').readlines():
            keyword = keyword.strip()
            results_temp = regex_string(keyword, shim_entries)
            if results_temp:
                WriteListToFile(args.output, results_temp, 'IOC-dates-Results.txt')


if __name__ == '__main__':
    main()