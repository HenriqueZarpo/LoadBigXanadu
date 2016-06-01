#!/usr/bin/env python

# Copyright 2015, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line application that loads data into BigQuery via HTTP POST.
This sample is used on this page:
    https://cloud.google.com/bigquery/loading-data-into-bigquery
For more information, see the README.md under /bigquery.
"""

import argparse
import json
import time
import datetime
from unidecode import unidecode
import csv
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload
from oauth2client.client import GoogleCredentials
from oauth2client.service_account import ServiceAccountCredentials

nbJobsCompleted = 0
nbFilesSkipped = 0
nbErrors = 0

# [START make_post]
def load_data( data_path, project_id, dataset_id, table_id):
    global nbJobsCompleted
    global nbFilesSkipped
    global nbErrors
    """Loads the given data file into BigQuery.
    Args:
        schema_path: the path to a file containing a valid bigquery schema.
            see https://cloud.google.com/bigquery/docs/reference/v2/tables
        data_path: the name of the file to insert into the table.-
        project_id: The project id that the table exists under. This is also
            assumed to be the project id this request is to be made under.
        dataset_id: The dataset id of the destination table.
        table_id: The table id to load data into.
    """
    # Create a bigquery service object, using the application's default auth
    scopes = ['https://www.googleapis.com/auth/bigquery']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('ZarpoBigQuery-3bc9f2a1cfc2.json', scopes=scopes)
    bigquery = discovery.build('bigquery', 'v2', credentials=credentials)

    # Infer the data format from the name of the data file.
    source_format = 'CSV'
    if data_path[-5:].lower() == '.json':
        source_format = 'NEWLINE_DELIMITED_JSON'

    # Post to the jobs resource using the client's media upload interface. See:
    # http://developers.google.com/api-client-library/python/guide/media_upload
    insert_request = bigquery.jobs().insert(
        projectId=project_id,
        # Provide a configuration object. See:
        # https://cloud.google.com/bigquery/docs/reference/v2/jobs#resource
        body={
            'configuration': {
                'load': {
##                    'schema': {
##                        'fields': json.load(open(schema_path, 'r'))
##                    },
                    'destinationTable': {
                        'projectId': project_id,
                        'datasetId': dataset_id,
                        'tableId': table_id
                    },
                    'sourceFormat': source_format,
                }
            }
        },
        media_body=MediaFileUpload(
            data_path,
            mimetype='application/octet-stream'))
    job = insert_request.execute()

    print('Waiting for job to finish for {}...'.format(data_path))

    status_request = bigquery.jobs().get(
        projectId=job['jobReference']['projectId'],
        jobId=job['jobReference']['jobId'])

    # Poll the job until it finishes.
    while True:
        result = status_request.execute(num_retries=2)

        if result['status']['state'] == 'DONE':
            if result['status'].get('errors'):
                raise RuntimeError('\n'.join(
                    e['message'] for e in result['status']['errors']))
                nbErrors = nbErrors + 1
            print('Job complete.')
            nbJobsCompleted = nbJobsCompleted + 1
            return

        time.sleep(1)
# [END make_post]


# [START main]
def main(project_id, dataset_id, table_name, data_path):
    load_data(
        data_path,
        project_id,
        dataset_id,
        table_name)
    
    
# [END main]


def removefirstlinecsv(inf,outf):
    with open(inf,'r') as f:
        with open(outf,'wb') as f1:
            rder=csv.reader(f)
            wter=csv.writer(f1,quotechar='"',quoting=csv.QUOTE_ALL,lineterminator="\n")
            firstline=f.readline() # skip header line
            maline=firstline[0]
            #print repr(firstline)
            #print firstline
            printr = True
            for row in rder:
                changealldatesformatbutnotanythingoftheother(row,'%d-%b-%Y %H:%M:%S')
                #print repr(line)
                wter.writerow(row)
    return firstline,row

def changealldatesformatbutnotanythingoftheother(stringlist,oldf):
    for k in range(len(stringlist)):
        try:
            stringlist[k]=datetime.datetime.strptime(stringlist[k], oldf).isoformat()
        except:
            #ohwell
            anothervariablenotcredited=0
            
            
import os
import time


if __name__ == '__main__':
    
    projectid="zarpobigquery"
    datasetid="big_xanadu"
    listfiles=["sent","click","open","opt_out","skipped","bounce","launch_state"]
    lepath="./load/"
    for f in listfiles:
        mafile = "{}CED_{}.csv".format(lepath,f)
        if "CED_{}.csv".format(f) in os.listdir(lepath) and time.time()-os.path.getmtime(mafile)<10000:
            colsline=removefirstlinecsv(mafile,"{}CEDBX_{}.csv".format(lepath,f))
            #Transforms them in CloudStorage format
            
            main(
                projectid,
                datasetid,
                f.replace("_",""),
                "{}CEDBX_{}.csv".format(lepath,f))
        else:
            print  "{} is too old or not in folder. Skipped".format(f)
            nbFilesSkipped = nbFilesSkipped + 1
    email_text = open('emailtxt.txt', 'a')
    email_text.write('\n Big Xanadu:\n Number of Jobs Completed: {}\n Number of files Skipped: {}\n Number of jobs with errors: {}'.format(nbJobsCompleted, nbFilesSkipped, nbErrors))
    email_text.close()
