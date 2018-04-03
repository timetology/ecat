import sys
import struct
from Registry import Registry
from jinja2 import Template, Environment, PackageLoader
import codecs
import time
from datetime import datetime, timedelta

class PluginClass(object):

    def __init__(self, hives=None, search=None, format=None, format_file=None):
        self.hives = hives
        self.search = search
        self.format = format
        self.format_file = format_file

    def ProcessPlugin(self):

        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))

        for hive in self.hives:

            for entry in self.getUserAssist(hive):
                last_write = entry[0]
                sub_key = entry[1]
                runcount = entry[2]
                windate = entry[3]
                data = entry[4]            
            
                if self.format is not None:
                    template = Environment().from_string(self.format[0])
                    sys.stdout.write(template.render(last_write=last_write, \
                                                     sub_key=sub_key, \
                                                     runcount=runcount, \
                                                     windate=windate, \
                                                     data=data) + "\n")
            
                elif self.format_file is not None:
                    with open(self.format_file[0], "rb") as f:
                        template = env.from_string(f.read())            
                        sys.stdout.write(template.render(last_write=last_write, \
                                                         sub_key=sub_key, \
                                                         runcount=runcount, \
                                                         windate=windate, \
                                                         data=data) + "\n")

    def convert_wintime(self, windate):
        # http://stackoverflow.com/questions/4869769/convert-64-bit-windows-date-time-in-python
        us = int(windate) / 10
        first_run = datetime(1601,1,1) + timedelta(microseconds=us)
        return first_run    

    def getUserAssist(self, hive):
        userassist = "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\UserAssist"

        #Giuds for the various Operating Systems
        guids = ["{CEBFF5CD-ACE2-4F4F-9178-9926F41749EA}",
                 "{F4E57C4B-2036-45F0-A9AB-443BCFE33D9F}",
                 "{5E6AB780-7743-11CF-A12B-00AA004AE837}",
                 "{75048700-EF1F-11D0-9888-006097DEACF9}"
                 ]
        userassist_entries = []
        
        #Reference: registrydecoder.googlecode.com/svn/trunk/templates/template_files/user_assist.py
        for g in guids:
            try:
                for sks in Registry.Registry(hive).open(userassist).subkey(g).subkey("Count").values():
                    #Windows 7
                    if len(sks.value()) > 16:# 68:
                        runcount = struct.unpack("I", sks.value()[4:8])[0]
                        date = struct.unpack("Q", sks.value()[60:68])[0]
                        last_write = Registry.Registry(hive).open(userassist).subkey(g).subkey("Count").timestamp()
                        key = Registry.Registry(hive).open(userassist).subkey(g).name()
                        skey = Registry.Registry(hive).open(userassist).subkey(g).subkey("Count").name()
                        sub_key = key + skey
                        windate = self.convert_wintime(date)
                        data = codecs.decode(sks.name(), 'rot_13')
                        
                        userassist_entries.append((last_write, sub_key, runcount, windate, data))
                    
                    #Windows XP
                    elif len(sks.value()) == 16:
                        last_write = Registry.Registry(hive).open(userassist).subkey(g).subkey("Count").timestamp()
                        key = Registry.Registry(hive).open(userassist).subkey(g).name()
                        skey = Registry.Registry(hive).open(userassist).subkey(g).subkey("Count").name()
                        sub_key = key + skey                        
                        session, runcount, date = struct.unpack("IIQ", sks.value())
                        runcount -= 5
                        windate = self.convert_wintime(date)
                        data = codecs.decode(sks.name(), 'rot_13')
                        
                        #print last_write, sub_key, runcount, windate, data
                        userassist_entries.append((last_write, sub_key, runcount, windate, data))
        
            except Registry.RegistryKeyNotFoundException as e:
                continue
            
        return(userassist_entries)