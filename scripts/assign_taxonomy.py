#************************************************************************************#
# 1. This script assigns taxonomy of reads or read pairs based on their similarities #
#    to the EukZoo database.                                                         #
# 2. First search your reads against EukZoo database. We recommend using DIAMOND. If #
#    you have fewer sequences, BLAST can also be used. Please make sure output is in #
#    tabular format (default for DIAMOND, --outfmt 6 for BLASTX                      #
# 3. Hits with score < score_cutoff * top score were discarded. (default 95%)        #
# 4. Maximal taxonomy allowed based on identity% of the best hit:                    #
#    >=95% species; >=80% genus; >=65% family; >=50% order; <=50% class;             #
# 5. Consensus calculation for multiple hits: total LCA, that is all hits have to    #
#    agree on a specific taxonomic level.                                            #
# 6. Consensus calculation for paired reads: read with higher best score wins        #
#************************************************************************************#

import sys
import getopt
import pandas as pd
from collections import defaultdict

usage = '''
python assign_taxonomy.py [OPTIONS] ... [READ ALIGNMENTS]
OPTIONS: -t [taxonomy table] (required)
         -c [cutoff] (optional, default c=0.95)
Paired end reads must have same name.
Output to STDOUT.
'''

#define global settings
score_cutoff = 0.95
max_taxonomy_cutoff = { 95:'Species', 80:'Genus', 65:'Family', 50:'Order' }

def prepare_taxonomy_table(taxonomy_table_file):
    """
    Read in the taxonomy table
    """
    taxonomy_table = pd.read_csv(taxonomy_table_file, sep = "\t")
    taxonomy_table = taxonomy_table.drop(["Strain","Notes"], axis = 1).set_index("Source_ID")
    taxonomy_table = taxonomy_table.T.to_dict() # Convert to dict to increase speed
    return taxonomy_table

def taxonomy_LCA(tax_list, best_identity, tax_table):
    """Generate consensus taxonomy using total LCA"""
    all_taxonomy = [tax_table[i] for i in tax_list] #get taxonomy of all sources in tax_list
    taxonomy_levels = ['Supergroup','Phylum','Class','Order','Family','Genus','Species']    
    global max_taxonomy_cutoff
    for key, value in max_taxonomy_cutoff.items(): #Check whether identity below cutoff
        if best_identity < key:
            taxonomy_levels.remove(value) #drop taxonomy levels below idenity cutoff
    result = ''
    for level in taxonomy_levels:
        #use set comprehension to get all unique taxons at this level
        level_consensus = {i[level] for i in all_taxonomy if i[level] != 'Uncertain'} #disregard uncertain entries
        if len(level_consensus) == 1: #if consensus agree
            result += level_consensus.pop() + ';'
        else:
            break #if disgreement, no need to continue for lower levels
    return result

def process_blast(read_file, tax_assign, best_score, tax_table):
    """
    Process blast reads and return taxonomy assignment and best score
    """
    global score_cutoff
    query_tracker = '' #define a query tracker to track which query is being processed
    taxonomy_collection = set()
    query_best_score = 0
    best_identity = 0
    with open(read_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            query, subject = fields[0:2]
            identity, score = float(fields[2]), float(fields[-1])
            if query != query_tracker: #if a new query, finish processing the last query
                if len(taxonomy_collection):
                    if query_best_score > best_score[query_tracker]: #only change the assignment if score is better
                        best_score[query_tracker] = query_best_score #update the best score
                        tax_assign[query_tracker] = taxonomy_LCA(taxonomy_collection, best_identity, tax_table) #run LCA and update taxonomy
                query_tracker = query #(re)initialize everything
                taxonomy_collection = set()
                query_best_score = score
                best_identity = identity
            if score < score_cutoff * max(query_best_score, best_score[query]): #skip if score is below cutoff of best score
                continue
            taxonomy_collection.add(subject[:10]) #add the source name to the taxonomy collection set
        if len(taxonomy_collection): #process the last query
            if query_best_score > best_score[query]:
                best_score[query] = query_best_score
                tax_assign[query_tracker] = taxonomy_LCA(taxonomy_collection, best_identity, tax_table) 
    return (tax_assign, best_score)

#Define global settings
score_cutoff = 0.95
max_taxonomy_cutoff = { 95:'Species', 80:'Genus', 65:'Family', 50:'Order' }
taxonomy_table_file = ""

#Read options
try:
    opts, args = getopt.getopt(sys.argv[1:], "t:c:")
except getopt.GetoptError as err:
    print(err)
    print(usage)
    sys.exit()
for o, a in opts:
    if o == "-t":
        taxonomy_table_file = a
    elif o == "-c":
        score_cutoff = a
if taxonomy_table_file=="" or len(args)<1:
    print(usage)
    sys.exit()

#Prepare taxonomy table
taxonomy_table = prepare_taxonomy_table(taxonomy_table_file)

#initialize two result dictionaries
taxonomy_assignment = defaultdict(str)
best_score = defaultdict(float)

#process blast results of both reads
for read_file in args:
    taxonomy_assignment, best_score = process_blast(read_file, taxonomy_assignment, best_score, taxonomy_table)

#output results
for key, value in taxonomy_assignment.items():
    if value != '':
        print (key+"\t"+value)
