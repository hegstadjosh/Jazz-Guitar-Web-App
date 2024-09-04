import itertools
import pprint
import music_data as md 
import music_objects as mo
import json

@staticmethod
def find_spelling_from_name(chord_name): 
    if chord_name is None: 
        return None
    spelling = None
    for entry in md.names_to_spellings['chords']: 
        if chord_name in entry['names']: 
            spelling = entry['spelling']
            break

    # try removing 1, then 2 chars from name (ie A7b9#5 -> A7b9 or Cmaj7 -> Cmaj) if no spelling found
    if spelling is None and len(chord_name) > 2: 
        tone = None
        for i in range(1,3): 
            
            new_spelling = find_spelling_from_name(chord_name[:-i])
            if new_spelling is not None: 
                return new_spelling
            
            #spelling = short_spelling + [md.tones_to_integer[tones[i]]]        
                
    
    return spelling

# @staticmethod
# # return 7-digit list of coordinates for a chord spelling
# def find_coords_from_spelling(spelling): 
#     for entry in md.generic_shapes['shapes']:
#         shape = mo.ChordShape(entry['coords']) 
#         if shape.spelling == set(spelling): 
#             return entry['coords']
    
#     return None
import random

@staticmethod
def find_coords_from_spelling(spelling, options = 0): 
    if spelling is None: 
        return None
    shapes = md.generic_shapes['shapes']
    
    if options == 1: 
        coords = [] 
        for entry in shapes:
            shape = mo.ChordShape(entry['coords']) 
            if shape.spelling == set(spelling):  
                coords.append(entry['coords'])
        
        if len(coords) > 1:
            coords = [list(item) for item in set(tuple(md.reduced_coords(row)) for row in coords)]
            return coords
    else:
        random.shuffle(shapes)
        for entry in shapes:
            shape = mo.ChordShape(entry['coords']) 
            if shape.spelling == set(spelling): 
                return entry['coords']
    return None

def chord_to_tones(chord_name): 
    note = md.get_note_from_chord(chord_name)
    generic_name = md.get_generic_chord_name(chord_name)
    spelling = find_spelling_from_name(generic_name)

    if spelling is None: 
        return None
    
    note_val = None
    # find note value for root note
    for i, notes in enumerate(md.note_values): 
        if note in notes: 
            note_val = i

    if note_val is None:
        return None

    int_notes = sorted([(x + note_val) for x in spelling])
        #0, 4, 7, 10...
    return int_notes


def tones_to_notes(note, int_notes):
    notes = []
    is_flat = note in md.flat_keys
    for i in range(len(int_notes)):
            if is_flat:
                note = md.note_values[int_notes[i] % 12][1] #will be None if not a sharp/flat note
            if not note or not is_flat: 
                note = md.note_values[int_notes[i] % 12][0] 
            notes.append(note)

    return notes

def chord_to_notes(chord_name): 
    note = md.get_note_from_chord(chord_name)
    int_notes = chord_to_tones(chord_name)
    if int_notes is None: 
        return None
    return tones_to_notes(note, int_notes)

@staticmethod
def display_chord(chord_name, transpose = 0, options = 0, fret_range = None, iter = 0): 
    if iter > 15: 
        print("No chord found for", chord_name)
        return 0
    
    if fret_range is None or not isinstance(fret_range, list) or len(fret_range) != 2:
        fret_range = [-1, 1000]

    chord_name = md.transpose_chord(chord_name, transpose)
    note = md.get_note_from_chord(chord_name)
    generic_name = md.get_generic_chord_name(chord_name)
    spelling = find_spelling_from_name(generic_name)
    coords = find_coords_from_spelling(spelling, options)
    
    if coords is None: 
        print("No chord found for", generic_name)
        return 0
    

    if coords and isinstance(coords[0], list):
        used_coords = []
        for row in coords:
            if md.reduced_coords(row) in used_coords: 
                continue
            used_coords.append(md.reduced_coords(row))

            shape_obj = mo.ChordShape(row, note) 
            if shape_obj.diagram.min_fret >= fret_range[0] and shape_obj.diagram.max_fret <= fret_range[1]:
                print(shape_obj)
                shape_obj.print_diagram(2)
        return 0
    
    else:
        shape_obj = mo.ChordShape(coords, note) 
        if shape_obj.diagram.min_fret >= fret_range[0] and shape_obj.diagram.max_fret <= fret_range[1]:
            print(shape_obj)
            shape_obj.print_diagram()
            return 0 
        else: 
            if isinstance(fret_range, list):
                fret_range = "-".join(map(str, fret_range))
            display_chord(chord_name, options, fret_range, iter= iter + 1)
            return 0 

@staticmethod
def display_chord_loop(): 
    while True: 
        args = input("Enter a chord name: ").split(" ")
        
        if len(args) > 4 or len(args) == 0:
            print("Usage: chord_name [-a] [lowfret-highfret]")
            continue 
        
        chord_name = args[0]
        transpose = args[1] if len(args) > 1 else 0
        options = args[2] if len(args) > 2 else None
        fret_range = args[3] if len(args) > 3 else None

        if chord_name == "q": 
            break
        
        if transpose and not transpose.isdigit():
            transpose = 0 

        if options:
            if options == "-a": 
                options = 1
            else: 
                options = 0
                continue 
        
        if fret_range and "-" in fret_range:
            fret_range = fret_range.split("-")
            if not (len(fret_range) == 2 and fret_range[0].isdigit() and fret_range[1].isdigit()):
                print("Invalid fret_range format")
                continue
            fret_range = [int(fret_range[0]), int(fret_range[1])]
        else: 
            fret_range = None

        print("Chord:", chord_name, "Transpose:", transpose, "Options:", options, "Fret Range:", fret_range)
        display_chord(chord_name, transpose, options, fret_range)

def get_chord_diagrams(chords, fret_range): 
    chord_diagrams = []
    chords = list(dict.fromkeys(chords))
    if fret_range and "-" in fret_range:
        fret_range = fret_range.split("-")
        fret_range = [int(fret_range[0]), int(fret_range[1])]

    for chord in chords: 
        chord_name = md.get_generic_chord_name(chord)
        spelling = find_spelling_from_name(chord_name)
        range_good = False

        while not range_good:
            coords = find_coords_from_spelling(spelling)
            if coords is None: 
                chord_diagrams.append([chord, "No chord found"])
                range_good = False
                break 

            diagram_obj = mo.ChordShape(coords, chord).diagram
            if diagram_obj.min_fret >= fret_range[0] and diagram_obj.max_fret <= fret_range[1]: 
                range_good = True
                break
        if not range_good: #means no chord found
            continue

        diagram = diagram_obj.diagram
        string_diagram = [chord]
        for i in range(len(diagram) ):
            row = diagram[i]
            row_num = str(i + diagram_obj.min_fret - 1) if i + diagram_obj.min_fret - 1 in diagram_obj.fret_numbers else ""
            string_diagram.append("  ".join(str(element).ljust(diagram_obj.max_width) for element in row) + " " + row_num)

        chord_diagrams.append(string_diagram)

    
    return chord_diagrams

pprint.pprint(get_chord_diagrams(["Cm7b5", "F7b9"], "0-5"))