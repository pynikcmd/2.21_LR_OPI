#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

con = sqlite3.connect('mydatabase.db')


def sql_fetch(con):
    con = sqlite3.connect('mydatabase.db')

    cursor_obj = con.cursor()
    cursor_obj.execute(
        "CREATE TABLE IF NOT EXISTS projects(id INTEGER, name TEXT)"
    )
    data = [
        (1, "Ridesharing"),
        (2, "Water Purifying"),
        (3, "Forensics"),
        (4, "Botany")
    ]
    cursor_obj.executemany("INSERT INTO projects VALUES (?, ?)", data)
    con.commit()


if __name__ == "__main__":
    sql_fetch(con)
