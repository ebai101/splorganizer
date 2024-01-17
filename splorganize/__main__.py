import os
import re
import shutil
import json
from pathlib import Path
import sqlite3
import pandas as pd

splice_dir = 'C:/Users/carol/Documents/Splice/Samples/'
sorted_dir  = 'C:/Users/carol/Documents/Splice/Splorganized/'

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# open databases
sounds_db = sqlite3.connect('sounds.db')
with open ('hierarchy.json', 'r') as f:
    hierarchy = json.loads(f.read())
with open ('db_info.json', 'r') as f:
    db_info = json.loads(f.read())

# sqlite regex function
def regexp(expr, item):
    try:
        reg = re.compile(expr)
        return reg.search(item) is not None
    except Exception as e:
        print(e)
sounds_db.create_function("REGEXP", 2, regexp)

def reset_filetree():
    for dirname in os.scandir (sorted_dir):
        shutil.rmtree (dirname.path)
    for dirname in hierarchy['sample_dirs'].keys():
        os.mkdir (sorted_dir + '/' + dirname)
    os.mkdir (sorted_dir + '/' + hierarchy['catchall']['dirname'])

def get_samples (cat, custom_query=None):
    if 'query' in cat:
        query = cat['query']
    else:
        query = """
        select * from samples 
        where tags regexp '{tag_regex}'
        and filename regexp '{file_regex}'
        {loop_filter}
        and local_path not null;""".format (
            tag_regex = cat['tag_regex'],
            file_regex = cat['file_regex'],
            loop_filter = "and sample_type = 'oneshot'" if not cat['include_loops'] else ""
        ) if not custom_query else custom_query
    
    with sounds_db:
        return sounds_db.execute(query).fetchall()

def samples_to_dataframe (samples):
    return pd.DataFrame(samples,
             columns=db_info['db_cols'])\
            .set_index ('id')\
            .drop(['local_path', 'attr_hash', 'file_hash', 'sas_id', 'genre', 'pack_uuid', 'purchased_at', 'last_modified_at', 'waveform_url'], axis=1)

# create link directory
def generate_links (dirname, samples):
    for row in samples:
        sample_path = row[1]
        filename = row[10]
        # For blackbox prepend key and bpm to filename if not null
        key = row[4]
        bpm = row[5]
        sample_type = row[13] # loop OR oneshot
        key = key.upper() if key != None else None
        bpm = None if bpm == 0 else str(bpm)
        original_list = [key, bpm, filename]
        filtered_list = [item for item in original_list if item is not None]
        filename = "-".join(filtered_list)

        # Add oneshot or loop to the directory
        dir = '{}/{}'.format(dirname, sample_type)

        # Add key to the directory after sample_type
        if dirname == 'tonal' and key is not None:
            dir = '{}/{}'.format(dir, key)

        link_dir = '{}/{}'.format(sorted_dir, dir)
        link_path = '{}/{}'.format(link_dir, filename)
        if not os.path.exists(link_path):
            # TODO symlink is funky on windows with perms
            # os.symlink(sample_path, link_path)
            os.makedirs(link_dir, exist_ok=True)
            shutil.copy(sample_path, link_path)

# main program
reset_filetree()

sorted_samps = {}
catchall = ''

# process samples
for i in hierarchy['sample_dirs'].keys():
    sorted_samps[i] = get_samples (hierarchy['sample_dirs'][i])
    generate_links (i, sorted_samps[i])
    
# catchall (percussion)
catchall_samps = get_samples (hierarchy['catchall'])
for i in sorted_samps.keys():
    for samp in sorted_samps[i]:
        if samp in catchall_samps:
            catchall_samps.remove(samp)
generate_links (hierarchy['catchall']['dirname'], catchall_samps)