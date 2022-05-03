#
# Amcache Win10 Parser - github.com/timetology
# python 3

import argparse
import datetime
import os
import sys

from Registry import Registry

def getTotalFilesStartsWith(path, file_prefix):
    counter = 0
    for filename in TraversePath(path):
        fname = os.path.split(filename)[1]
        if fname.lower().startswith(file_prefix): 
            counter += 1
    return counter

def TraversePath(directory):
    for dirpath,_,filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))

def getTotalFilesIn(match,path):
    total_files = 0
    for filename in TraversePath(path):
        fname = os.path.split(filename)[1]
        if match in fname.lower(): 
            total_files += 1
    return total_files



def Parse_Single_Amcache(amcache):
    ret = []
    try:
        registry = Registry.Registry(amcache)
    except Exception:
    	pass
    else:
        if registry.open("Root\\InventoryApplicationFile") is not None:
            amcache_win10 = True
            volumes = registry.open("Root\\InventoryApplicationFile")
        
    
        if amcache_win10:

            for subkey in volumes.subkeys():
                line = ''
                for value in subkey.values():
                    line += str(value.value()) + ','
                ret.append(line)
    return ret

def Parse_Amcache_Dir(path):
    total_files = getTotalFilesStartsWith(path, 'amcache')
    print("Amcache Hive Count: {}".format(total_files))
    print('ProgramId,FileId,LowerCaseLongPath,LongPathHash,Name,OriginalFileName,Publisher,Version,BinFileVersion,BinaryType,ProductName,ProductVersion,LinkDate,BinProductVersion,AppxPackageFullName,AppxPackageRelativeId,Size,Language,Usn')
    for filename in TraversePath(path):
        fname = os.path.split(filename)[1]

        if fname.lower().startswith('amcache'):
            #print(filename)
            parsed = Parse_Single_Amcache(filename)
            if parsed:
                for line in parsed:
                    print(fname + ',' + line)

                    
def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-d', '--directory', help='Amcache.hve Directory', required=False)
    parser.add_argument('-f', '--file', help='Amcache.hve File', required=False)
    
    args = parser.parse_args()

    if args.file:
        parsed = Parse_Single_Amcache(args.file)
        if parsed:
            print('ProgramId,FileId,LowerCaseLongPath,LongPathHash,Name,OriginalFileName,Publisher,Version,BinFileVersion,BinaryType,ProductName,ProductVersion,LinkDate,BinProductVersion,AppxPackageFullName,AppxPackageRelativeId,Size,Language,Usn')
            for line in parsed:
                print(args.file + ',' + line)
    elif args.directory:
        Parse_Amcache_Dir(args.directory)
    else:
        print('[!] Error - Nothing to do')

if __name__ == '__main__':
    main()
 
