#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import csv

from dolly.utils import *


def create_connection(db_file, db_type='sqlite3'):
    if db_type == 'sqlite3':
        try:
            return sqlite3.connect(db_file)
        except sqlite3.Error as e:
            print(e)
    else:
        raise NotImplementedError('Database unknown')


def load_into_db(filename, database, sql, parser, csvkargs, buffer=10000, **kwargs):
    data = []

    commit_flag = False

    # Create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    with conn:
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, **csvkargs)

            for counter, (is_last, row) in enumerate(isLast(reader)):
                values = parser(row, **kwargs)
                if values:
                    data.append(values)
                    commit_flag = True if (counter + 1) % buffer == 0 else False

                # Force commit (To make sure the commit is done at this point)
                if commit_flag or is_last:
                    cur.executemany(sql, data)
                    conn.commit()
                    data = []  # Reset data
                    commit_flag = False
                    print("- Commit #{}\t(total: {})".format(int((counter + 1) / buffer), counter + 1))
                    if is_last:
                        print('Finished!')


def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)

# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)