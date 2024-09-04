import os
import json
import pprint
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text

import music_methods as mm
import music_objects as mo
import music_data as md

DATABASE_USERNAME = ""
DATABASE_PASSWRD = ""
DATABASE_HOST = ""
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/"

engine = create_engine(DATABASEURI)

conn = engine.connect()

def add_diagrams(): 
    fret_range = [0, 5]
    # Raw SQL query
    query = text("SELECT chord_id as id, chord_name as name FROM chord;")
    result = conn.execute(query)
    rows = result.fetchall()

    i = 0 
    for row in rows:
        #get diagram for chord name
        chord_name = md.transpose_chord(row[1], 0)
        note = md.get_note_from_chord(chord_name)
        generic_name = md.get_generic_chord_name(chord_name)
        spelling = mm.find_spelling_from_name(generic_name)
        coords = mm.find_coords_from_spelling(spelling)
        
        # no diagram 
        if coords is None: 
            query = text("UPDATE chord SET diagram = NULL WHERE chord_id = :chord_id")
            conn.execute(query, chord_id=row[0])
            return 0

        k = 0 
        while True:
            shape_obj = mo.ChordShape(coords, note) 
            if shape_obj.diagram.min_fret >= fret_range[0] and shape_obj.diagram.max_fret <= fret_range[1]:
                diagram = shape_obj.diagram.diagram
                print(chord_name, generic_name)
                pprint.pprint(diagram)
                insert_diagram(row[0], diagram)
                break 
            elif k > 15: 
                diagram = shape_obj.diagram.diagram
                print(chord_name, generic_name)
                pprint.pprint(diagram)
                insert_diagram(row[0], diagram)
                break
            coords = mm.find_coords_from_spelling(spelling)
            k += 1

        if i > 5: break
        i += 1

def add_notes():
    # Raw SQL query
    query = text("SELECT chord_id as id, chord_name as name FROM chord order by chord_id;")
    result = conn.execute(query)
    rows = result.fetchall()

    i = 0
    for row in rows:
        notes = mm.chord_to_notes(row[1])
        insert_notes(row[0], notes)

        i += 1

def insert_diagram(chord_id, diagram): 
    query = text("UPDATE chord SET diagram = :diagram WHERE chord_id = :chord_id")
    conn.execute(query, chord_id=chord_id, diagram=diagram)

def insert_notes(chord_id, notes): 
    print("insert", chord_id, notes)
    query = text("UPDATE chord SET notes = :notes WHERE chord_id = :chord_id;" )
    conn.execute(query,{"notes": notes, "chord_id": chord_id})
    conn.commit()

def add_descriptions(): 
    with open("C:\\Users\\socce\\Desktop\\Personal GPT\\responses.txt", "r", encoding="utf-8") as f: 
        responses = f.readlines()
        for response in responses: 

            response = response.replace("'", "''")
            title = response.split("\"")[1]
            
            query = text("select song_id from song where title = :title;")
            result = conn.execute(query, {"title": title})
            row = result.fetchone()
            pprint.pprint(row)
            if row is None: 
                print(title)
                print(f"update song set description = '{response}' where song_id = ;")
            
            else: 
                query = text("update song set description = :description where song_id = :song_id;")
                #print(f"update song set description = '{response}' where title = '{title}';")
                
                conn.execute(query, {"description": response, "song_id" : row[0]})
                conn.commit()

