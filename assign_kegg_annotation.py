#************************************************************************************#
# 1. This script assigns KEGG annotation of reads or read pairs based on their       #
#    similarities to the EukZoo database.                                            #
# 2. First search your reads against EukZoo database. We recommend using DIAMOND. If #
#    you have fewer sequences, BLAST can also be used. Please make sure output is in #
#    tabular format (default for DIAMOND, --outfmt 6 for BLASTX)                     #
# 3. Hits with score < score_cutoff * top score were discarded. (default 95%)        #
# 4. Consensus calculation for multiple hits: all hits with KEGG annotations have to #
#    agree.                                                                          #
# 6. Consensus calculation for paired reads: read with higher best score wins        #
#************************************************************************************#

import sys
import getopt
from collections import defaultdict

usage = '''
python assign_kegg_annotation.py [OPTIONS] ... [READ ALIGNMENTS]
OPTIONS: -a [database KEGG annotation] (required)
         -c [cutoff] (optional, default c=0.95)
Paired end reads must have same name.
Output to STDOUT.
'''

#define global settings
score_cutoff = 0.95

def prepare_kegg_table(kegg_table_file):
    """
    Read in the database KEGG annotation
    """
    kegg_table = dict()
    with open(kegg_table_file, 'r') as f:
        for line in f:
            fields = line.strip().split("\t")
            if len(fields)>1:
                kegg_table[fields[0]] = fields[1]
    return kegg_table

def process_blast(read_file, kegg_assign, best_score, kegg_table):
    """
    Process blast reads and return kegg annotation and best score
    """
    global score_cutoff
    query_tracker = '' #define a query tracker to track which query is being processed
    kegg_collection = set()
    query_best_score = 0
    with open(read_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            query, subject = fields[0:2]
            score = float(fields[-1])
            if query != query_tracker: #if a new query, finish processing the last query
                if len(kegg_collection):
                    if query_best_score > best_score[query_tracker]: #only change the assignment if score is better
                        best_score[query_tracker] = query_best_score #update the best score
                        if len(kegg_collection) == 1: #if all hits agree
                            kegg_assign[query_tracker] = kegg_collection.pop()
                        else: #if conflicts exist
                            kegg_assign[query_tracker] = "conflicted"
                query_tracker = query #(re)initialize everything
                kegg_collection = set()
                query_best_score = score
            if score < score_cutoff * max(query_best_score, best_score[query]): #skip if score is below cutoff of best score
                continue
            #add the KEGG annotation of the subject if it exists
            if subject in kegg_table:
                kegg_collection.add(kegg_table[subject])
        if len(kegg_collection): #process the last query
            if query_best_score > best_score[query_tracker]:
                best_score[query_tracker] = query_best_score
                if len(kegg_collection) == 1: #if all hits agree
                    kegg_assign[query_tracker] = kegg_collection.pop()
                else: #if conflicts exist
                    kegg_assign[query_tracker] = "confilcted"
    return (kegg_assign, best_score)

#Define global settings
score_cutoff = 0.95
kegg_table_file = ""

#Read options
try:
    opts, args = getopt.getopt(sys.argv[1:], "a:c:")
except getopt.GetoptError as err:
    print(err)
    print(usage)
    sys.exit()
for o, a in opts:
    if o == "-a":
        kegg_table_file = a
    elif o == "-c":
        score_cutoff = a
if kegg_table_file=="" or len(args)<1:
    print(usage)
    sys.exit()

#Prepare KEGG annotation table
kegg_table = prepare_kegg_table(kegg_table_file)

#initialize two result dictionaries
kegg_assignment = defaultdict(str)
best_score = defaultdict(float)

#process blast results of both reads
for read_file in args:
    kegg_assignment, best_score = process_blast(read_file, kegg_assignment, best_score, kegg_table)

#output results
for key, value in kegg_assignment.items():
    if value != "conflicted":
        print (key+"\t"+value)
