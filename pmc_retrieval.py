import sys
import os
import pandas

import argparse
import httplib, urllib
import xml.etree.ElementTree as ET
import dateutil
import time
from datetime import datetime

DOCS_FOR_FOLDER=1000

parser=argparse.ArgumentParser()
parser.add_argument('-o', help='Path Directory Directory')
parser.add_argument('-s', help='Search Term for the data to be downloaded')
parser.add_argument('-b', help='Flag to indicate start up, if its true all the database will be downloaded if not only the data from last month to now')
args=parser.parse_args()

if __name__ == '__main__':
    import pmc_retrieval
    start_time = time.time()
    try:
        dest=args.o
        search_terms=args.s
        start_up=args.b
    except Exception as inst:
        print( "Error: reading the parameters.")
        sys.exit(1) 
    if dest==None:
        print( "Error: complete the destination path.") 
        sys.exit(1)    
    if not os.path.exists(dest):
        print( "Error: the destination path does not exist.") 
        sys.exit(1)
    
    pmc_retrieval.Main(args)    
        
def Main(args):
    dest=args.o
    search_terms=args.s
    start_up=args.b
    result_file = dest + "/index.csv"
    if os.path.isfile(result_file):
        df = pandas.read_csv(result_file, header=0, index_col=0)
    else:
        df = pandas.DataFrame()
    #df.at[index,'date']=datetime.now().date()   
    d = datetime.now()
    
    retrieval_output = dest + "/retrieval/"
    if(start_up=="True"):
        from_date = datetime.strptime("1900-01-01", "%Y-%m-%d")
        work_dir = os.path.join(retrieval_output, str("start_up_" + str(d.date())))
    else:
        from_date = d - dateutil.relativedelta.relativedelta(months=1)
        work_dir = os.path.join(retrieval_output, str(from_date.date()))
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    if(search_terms is not None):
        params_dict = {'term': search_terms}
    else:
        params_dict = {'from': str(from_date.date())}
    download(df, from_date, work_dir, result_file, params_dict)   

def download(df, from_date, work_dir, result_file, params_dict):    
    token=''
    while (token != None):
        if(token!=''):
            params_dict = {'resumptionToken': token}
        params = urllib.urlencode(params_dict)
        conn = httplib.HTTPSConnection("www.ncbi.nlm.nih.gov")
        conn.request("POST", "/pmc/utils/oa/oa.fcgi", params)
        # Obtiene la respuesta
        r1 = conn.getresponse()
        # Verifica que la respuesta es correcta
        if not r1.status == 200:
            print "Error en la conexion: " + str(r1.status) + " " + str(r1.reason) 
            exit()
        response = r1.read()
        docs_quantity = DOCS_FOR_FOLDER
        internal_folder_q = 0 
        docXml = ET.fromstring(response)
        for f in docXml.find("records").findall("record"):
            pmc_id = f.attrib["id"]
            link = f.find("link").attrib["href"]
            update_date = f.find("link").attrib["updated"]
            update_date = datetime.strptime(update_date, '%Y-%m-%d %H:%M:%S')
            if(from_date < update_date):
                if(docs_quantity==DOCS_FOR_FOLDER):
                    internal_folder_q = internal_folder_q + 1
                    internal_folder = work_dir + "/" + str(internal_folder_q)
                    if not os.path.exists(internal_folder):
                        os.makedirs(internal_folder)
                print "PMC ID {:15} ".format(pmc_id)
                #print "LINK {:300} ".format(link)
                params = urllib.urlencode({'db':'pmc','retmode':'xml','id':pmc_id})
                conn_2 = httplib.HTTPSConnection("eutils.ncbi.nlm.nih.gov")
                conn_2.request("POST", "/entrez/eutils/efetch.fcgi", params)
                r1 = conn_2.getresponse()
                response = r1.read()
                file_path=os.path.join(internal_folder, str(pmc_id+".xml"))
                save_file2 = open(file_path, "w")
                save_file2.write(response)
                save_file2.close()
                conn_2.close()
                index = len(df.index) + 1 
                df.at[index,'name']=pmc_id
                df.at[index,'date']=str(datetime.now().date())
                df.at[index,'time']=str(datetime.now().time())
                df.at[index,'retrieval']="complete"
                df.at[index,'retrieval_path']=file_path
                df.to_csv(result_file)    
                docs_quantity = docs_quantity - 1
                if(docs_quantity==0):
                    docs_quantity=DOCS_FOR_FOLDER
        resumption = docXml.find("resumption")
        if(resumption!=None):
            token = resumption.find("link").attrib["token"]
        else:
            token=None
        conn.close()
    print "PMC download Finished"        