#!/usr/bin/env python

import os
import re
import json
import shutil
import sqlite3
from pathlib import Path
from splorganizer_config import sounds_db_paths, sorted_dir


# sqlite regex function
def regexp(expr, item):
    try:
        reg = re.compile(expr)
        return reg.search(item) is not None
    except Exception as e:
        print(e)


# resets the filetree of the sorted directory per the hierarchy schema
def reset_filetree(hierarchy):
    for file in os.scandir(sorted_dir):
        if os.path.isdir(file.path):
            shutil.rmtree(file.path)
        else:
            os.remove(file.path)
    for file in hierarchy["sample_dirs"].keys():
        os.mkdir(sorted_dir + "/" + file)
    os.mkdir(sorted_dir + "/" + hierarchy["catchall"]["dirname"])


# queries the database for a list of samples
def get_samples(db, cat, custom_query=None):
    if "query" in cat:
        query = cat["query"]
    else:
        query = (
            """
        select * from samples
        where tags regexp '{tag_regex}'
        and filename regexp '{file_regex}'
        {loop_filter}
        and local_path not null;""".format(
                tag_regex=cat["tag_regex"],
                file_regex=cat["file_regex"],
                loop_filter="and sample_type = 'oneshot'"
                if not cat["include_loops"]
                else "",
            )
            if not custom_query
            else custom_query
        )

    with db:
        return db.execute(query).fetchall()


# create link directory
def generate_links(dirname, samples):
    for row in samples:
        sample_path = row[1]
        filename = row[10]
        link_path = "{}/{}/{}".format(sorted_dir, dirname, filename)

        if not os.path.exists(link_path):
            os.symlink(sample_path, link_path)


if __name__ == "__main__":
    # open databases
    with open("hierarchy.json", "r") as f:
        hierarchy = json.loads(f.read())
    with open("db_info.json", "r") as f:
        db_info = json.loads(f.read())

    reset_filetree(hierarchy)
    sounds_db_list = []
    for db_path in sounds_db_paths:
        db = sqlite3.connect(db_path)
        db.create_function("REGEXP", 2, regexp)
        sounds_db_list.append(db)

    sorted_samps = {}
    catchall = ""

    for db in sounds_db_list:
        # process samples
        for i in hierarchy["sample_dirs"].keys():
            sorted_samps[i] = get_samples(db, hierarchy["sample_dirs"][i])
            generate_links(i, sorted_samps[i])

        # catchall (percussion)
        catchall_samps = get_samples(db, hierarchy["catchall"])
        for i in sorted_samps.keys():
            for samp in sorted_samps[i]:
                if samp in catchall_samps:
                    catchall_samps.remove(samp)
        generate_links(hierarchy["catchall"]["dirname"], catchall_samps)
