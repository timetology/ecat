import binascii
import sys
import time
import traceback
import urllib2, urllib
import csv
import re
import json
from optparse import OptionParser


# Encode Unicode strings safely - Should reduce skipped sessions and improve stdout output
# Fix provided by Matt, further tuned by me
def safe_str(obj):
    try:
        if (obj is None):
             return ''
        else:
             return str(obj)
    except UnicodeEncodeError:
        return unicode(obj).encode('unicode_escape')
    except UnicodeDecodeError:
        return unicode(obj).encode('latin-1')

def quote_str(obj):
    #place " around values with spaces, commas and other special characters and escape any possible " already there
    if (re.search('[\s+,=/|]', obj)):
       return '"' + obj.replace('"','""') + '"'
    else:
       return obj

def vt_api_call(vt_opener,vt_url,parameters,method):
     sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + " API Request: " + vt_url + "?" + str(urllib.urlencode(parameters)) + "\n")
     try:
         if (method == 'GET'): 
             response = vt_opener.open('%s?%s' % (vt_url, urllib.urlencode(parameters)))
         else:
             data = urllib.urlencode(parameters)
             req = urllib2.Request(vt_url, data) 
             response = vt_opener.open(req)
         # VT API Returned exceed the public API request rate limit a 204 HTTP status code     
         if (response.getcode() == 204):
             sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + " " + "Sleeping for a minute due to VT limitations. 204 Returned by HTTP call.\n")
             time.sleep(60)
             # Call itself again for a result
             json_string = vt_api_call(vt_opener,vt_url,parameters,method)
         else:    
             json_string = response.read()
             #sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + " API Response: " + str(response.getcode()) + ":" + str(response.info()) +"\n" + json_string + "\n")
     except urllib2.URLError, e:
             data = {}
             data['response_code'] = 1024
             data['reason'] = str(e.reason)
             json_string = json.dumps(data)
             c = sys.exc_info()[0]
             e = sys.exc_info()[1]
             #Error 
             sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + ' - ERROR: Reason="' + str(e) + '" Class="' + str(c) + '"\n')
             sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + ' ' + traceback.format_exc())
             pass
     return json_string

## MAIN STARTS HERE ##
REFRESH_AGE = 31*86400
TRUSTED_AV_VENDOR = [ "Symantec", "ESET-NOD32", "TrendMicro-HouseCall", "Avast", "Kaspersky", "F-Secure", "TrendMicro", "McAfee-GW-Edition", "Sophos", "F-Prot", "Microsoft", "McAfee", "Fortinet", "AVG", "Panda" ]
try:
    parser = OptionParser(description="This script will read MD5s from a CSV file and will check them against VirusTotal.")
    parser.add_option("-f", "--file", dest="filename", help="Filename to process")
    parser.add_option("-c","--es-cache-on", dest="cache_off", action="store_false", default=True, help="ElasticSearch Caching.")

    (opts, args) = parser.parse_args()


    #vt_apikey = "<place your VirusTotal API key in here>"
    # NW-IR Key
    vt_apikey = ""

    if vt_apikey == "" or vt_apikey is None:
        sys.exit("Please set a VirtusTotal API Key")

    csvfile = open(opts.filename, 'rb')
    csvreader = csv.DictReader(csvfile)
    csvheaders = csvreader.fieldnames
    
    if (not 'HashMD5' in csvheaders ):
        sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + ' - ERROR: No HashMD5 in CSV Header="' + str(','.join(csvheaders)) + '"\n')             
    else:
    
        if (not opts.cache_off):
            from elasticsearch import Elasticsearch
            #es = Elasticsearch()
            es = Elasticsearch(['https://cache:$4T2_9q_@209.249.175.10:9443/'])
            import urllib3
            urllib3.disable_warnings()

        proxy = urllib2.ProxyHandler({'ftp': ''})
        proxy_opener = urllib2.build_opener(proxy)

        #csvheaders.extend(["VTResult","VTScanDate","VTResultPositives","VTResultTotal","VTResultRatio","Symantec","Kaspersky","TrendMicro","Sophos","Microsoft","McAfee","TrustedAV","VTLink","VTAV"])
        csvheaders.extend(["Symantec","Kaspersky","TrendMicro","Sophos","Microsoft","McAfee","TrustedAV","VTLink","VTAV"])
    
        csvwriter = csv.DictWriter(sys.stdout,fieldnames=csvheaders)
        csvwriter.writeheader()

        for row in csvreader:
            md5 = row['HashMD5'][2:].lower()
            if ( not re.match('[0-9a-f]{32}',md5) ):
                sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + ' - ERROR: ' + str(md5) + ' not an MD5 Hash.\n')             
            else:    
                # remove leading 0x from MSSQL output for easy import back if needed
                row['HashMD5'] = row['HashMD5'][2:]
                hits = True
                age = 0
                doc_id = None
                if (not opts.cache_off):
                    try:
                        res = es.search(index='virustotal',doc_type='file',q='md5:' + md5)
                    except:
                        c = sys.exc_info()[0]
                        e = sys.exc_info()[1]
                        #Error 
                        sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + ' - ERROR: ES Query Failed. Reason="' + str(e) + '" Class="' + str(c) + '"\n')             
                        hits = False
                else: 
                    hits = False
       
                if ( hits and res['hits']['total'] > 0 ):
                    age = int(time.time() - res['hits']['hits'][0]['_source']['last_update'])
                    sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + ' - INFO: Hit found on ElasticSearch for File Hash:' + md5 + ' age=' + str(age) + ' seconds\n')
                    doc_id = res['hits']['hits'][0]['_id']
                else:
                    hits = False
                if ( hits and age < REFRESH_AGE ):
                    json_string = res['hits']['hits'][0]['_source']['vt_api_response']
                else:
                    if ( hits ) :
                        sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + ' - WARN: Old hit found on ElasticSearch for File Hash:' + md5 + ' age=' + str(age) + ' seconds _id=' + str(doc_id) + '\n')
                    vt_url = "https://www.virustotal.com/vtapi/v2/file/report"
                    parameters = {"resource": md5, "apikey": vt_apikey }
                    json_string = vt_api_call(proxy_opener,vt_url,parameters,'POST')
                    json_file = json.loads(json_string)
                    # For file searches also cache files not on VT, a separate script will clean these up if needed
                    if json_file["response_code"] == 1 or json_file["response_code"] == 0 :
                        # If valid result returned store it in ElasticSearch
                        record = {}
                        record['md5'] = md5
                        record['last_update'] = int(time.time())
                        record['vt_api_response'] = json_string
                        record = json.dumps(record)
                        if (not opts.cache_off):
                            try:
                                res = es.index(index="virustotal", doc_type='file', id=doc_id, refresh=True, body=record)
                                # sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + ' - INFO: ' + str(res) + '\n')
                            except:
                                c = sys.exc_info()[0]
                                e = sys.exc_info()[1]
                                #Error 
                                sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + ' - ERROR: ES Index Failed. Reason="' + str(e) + '" Class="' + str(c) + '"\n')  
                json_file = json.loads(json_string)
                if json_file["response_code"] == 0 :
                     row['VTResult'] = "Not on VT"
                #Printing Desired Information
                if ('positives' in json_file.keys()):
                     row['VTResult'] = "VT Hits Found"
                     row['VTResultPositives'] = str(json_file["positives"])
                     row['VTResultTotal'] = str(json_file["total"])
                     row['VTResultRatio'] = str(((json_file["positives"] * 100 )/ json_file["total"]))
                     #print sessionid,"[",filename,"/",row['filename'],"]",":",json_file["positives"],"/",json_file["total"]
                     av_results = ''
                     trust_av_results = ''
                     for k in json_file["scans"].keys():
                         if json_file["scans"][k]["detected"] :
                             if ( av_results == '' ):
                                 av_results += k + ":" + safe_str(json_file["scans"][k]["result"])
                             else:
                                 av_results += "|" + k + ":" + safe_str(json_file["scans"][k]["result"])
                             if ( k in TRUSTED_AV_VENDOR and trust_av_results == ''  ):
                                 trust_av_results += k + ":" + safe_str(json_file["scans"][k]["result"])
                             elif ( k in TRUSTED_AV_VENDOR ):
                                  trust_av_results += "|" + k + ":" + safe_str(json_file["scans"][k]["result"])
                             if ( k in csvheaders ):
                                  row[k] = safe_str(json_file["scans"][k]["result"])
                     row['VTAV'] = av_results
                     row['TrustedAV'] = trust_av_results
                if ('scan_date' in json_file.keys()):
                     row['VTScanDate'] = safe_str(json_file["scan_date"])
                if ('permalink' in json_file.keys()): 
                     row['VTLink'] = safe_str(json_file["permalink"])
     
                csvwriter.writerow(row)

except:
    c = sys.exc_info()[0]
    e = sys.exc_info()[1]
    #Error pulling only one session issue error message and return empty
    sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + ' - ERROR: Reason="' + str(e) + '" Class="' + str(c) + '"\n')
    sys.stderr.write(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime(time.time())) + ' ' + traceback.format_exc())


