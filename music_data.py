# Mapping from standard to integer, including double sharps and flats
import pprint
import json 

'''
File to store music data (scales, chords, note values...).
Contains a convert_spelling method to convert between standard and integer spellings.
ChordShape data stored in the chord_coordinates.txt file, not yet used.

Data parsed using methods in the data_collection.py file.
Sources given in comments above chord_map and scale_map.
'''

names_to_spellings = {}
generic_shapes = {}
with open('./names_spellings2.json', 'r', encoding='utf-8') as file:
    names_to_spellings = json.load(file)
with open('./generic_shapes3.json', 'r', encoding='utf-8') as file:
    generic_shapes = json.load(file)

tones_to_integer = {
    '1': 0, 'b2': 1, '2': 2, '#2': 3, 'x2': 4, 'b3': 3, '3': 4, 'x3': 5, '4': 5, '#4': 6, 'x4': 7,
    'b5': 6, '5': 7, '#5': 8, 'x5': 9, 'b6': 8, '6': 9, '#6': 10, 'x6': 11, 'bb7': 9, 'b7': 10, '7': 11
}
# Inverse mapping for integer to standard
# 0: '1', 1: 'b2', 2: '2', 3: 'b3', 4: '3', 5: '4', 6: 'b5', 7: '5', 8: 'b6', 9: '6', 10: 'b7', 11: '7'
integer_to_tones = {v: k for k, v in tones_to_integer.items()}
integer_to_tones[9] = '6'

flat_keys = ["C", "F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb"]
sharp_keys = ["G", "D", "A", "E", "B", "F#", "C#"]

note_values = (
    ("A", None, "G##", "Bbb"),  # A
    ("A#", "Bb", "G###", "Cbb"),  # A#/Bb
    ("B", None, "A##", "Cb"),  # B
    ("C", None, "B#", "Dbb"),  # C
    ("C#", "Db", "B##", "Ebb"),  # C#/Db
    ("D", None, "C##", "Ebb"),  # D
    ("D#", "Eb", "Fbb", "C###"),  # D#/Eb
    ("E", None, "D##", "Fb"),  # E
    ("F", None, "E#", "Gbb"),  # F
    ("F#", "Gb", "E##", "Abb"),  # F#/Gb
    ("G", None, "F##", "Abb"),  # G
    ("G#", "Ab", "F###", "Bbbb")  # G#/Ab
)

import re

@staticmethod
def get_note_from_chord(name):
    # This regular expression matches note names
    note_pattern = r'[A-G](##?|bb?)?'

    # Search for the first note in the name string
    match = re.search(note_pattern, name)

    if match:
        # If a note was found, return it
        return match.group()
    else:
        # If no note was found, raise an error
        return None    

@staticmethod
def transpose_note(note, steps):
    if not steps or steps == 0:
        return note
    steps = int(steps)
    # Find the index of the note
    for i, values in enumerate(note_values):
        if note in values:
            note_index = i
            break
    else:
        raise ValueError(f"Note {note} not found")

    # Add the transposition value, wrapping around the length of the tuple if necessary
    transposed_index = (note_index + steps) % len(note_values)

    # Return the transposed note
    return note_values[transposed_index][0]  # We return the first spelling of the note

import re
@staticmethod
def transpose_chord(chord, steps):
    if steps == 0:
        return chord
    # This regular expression matches note names in the chord
    note_pattern = r'[A-G](##?|bb?)?'

    # This function is used to transpose each note
    def transpose_match(match):
        note = match.group(0)
        return transpose_note(note, steps)

    # Use the re.sub function to replace each note in the chord with its transposition
    transposed_chord = re.sub(note_pattern, transpose_match, chord)

    return transposed_chord

@staticmethod
# Function to calculate the distance between two notes
def note_distance(note1, note2): 
    # Find the index of each note
    for i, values in enumerate(note_values):
        if note1 in values:
            note1_index = i
        if note2 in values:
            note2_index = i

    # Calculate the distance between the notes
    distance = note2_index - note1_index

    # Return the distance, wrapping around the length of the tuple if necessary
    return distance % len(note_values)

@staticmethod 
def get_generic_chord_name(chord_name): 
    root_note = get_note_from_chord(chord_name)
    if root_note is None:  
        return None
    second_note = get_note_from_chord(chord_name.replace(root_note, '')) if len(chord_name) > 1 else None
    if second_note:
        interval = note_distance(root_note, second_note)
        second_tone = integer_to_tones[interval]
    
    new_name = chord_name.replace(root_note, '')
    if(second_note):
        new_name = new_name.replace(second_note, second_tone)

    return new_name
        
@staticmethod
def reduced_coords(coords): 
    reduced_coords = coords
    min_fret = min([c for c in coords[1:] if c != 0 ]) - 1
    for i in range(1, len(coords)):
        if coords[i] != 0:
            reduced_coords[i] = coords[i] - min_fret

    return reduced_coords

# coords = [
#     [2, 0, 2, 2, 2, 1, 0],
#     [1, 3, 3, 2, 1, 1, 1],
#     [4, 4, 4, 4, 6, 4, 6], 
#     [2, 0, 6, 6, 6, 5, 0], 
#     [2, 0, 4, 4, 4, 3, 0], 
#     [4, 5, 5, 5, 7, 5, 7]
# ]
# fret_range = [0, 5]
# used_coords = []
# note = 'C'
# for row in coords:
#     if reduced_coords(row) in used_coords: 
#         continue
#     used_coords.append(reduced_coords(row))

# pprint.pprint(used_coords)

@staticmethod
def convert_spelling(spelling, conversion_type):
    """
    Converts between standard and integer spellings of a chord.

    Parameters:
        spelling (str or set of int): The spelling to be converted.
        conversion_type (int): The type of conversion (0: standard to integer, 1: integer to standard).

    Returns:
        str or set of int: The converted spelling.
    """
    if conversion_type == 0 and type(spelling) != str:
        spelling = ' '.join(spelling)  # Convert to string
    elif conversion_type == 1 and type(spelling) != set:
        spelling = set(spelling)  # Convert to set

    # Check if spelling is a chord name in chord_map
    for chord_name, spellings in chord_map.items():
        if spellings[conversion_type] == spelling:
            return spellings[conversion_type - 1]  # Return other spelling type

    # If mapping not found, convert manually (only using flats)

    converted = []
    if conversion_type == 0:
        # Convert from standard to integer
        converted = [tones_to_integer.get(note, note) for note in spelling]
        converted = ' '.join(converted)  # Convert to string
    elif conversion_type == 1:
        # Convert from integer to standard
        converted = [integer_to_tones.get(note, note) for note in spelling]
        converted = set(converted)  # Convert to set

    return converted

# Dictionary of alternate chord names
alternate_chord_names = {
    'major 7th': ('maj7', 'M7', 'Δ7'),
    'dominant 7th': ('dom7', '7'),
    'minor 7th': ('min7', 'm7', '-7'),
    'half-diminished 7th': ('min7b5', 'm7b5', 'ø', 'm7(♭5)'),
    'diminished 7th': ('dim7', '°7'),
    'minor major 7th': ('minmaj7', 'mM7', 'mMaj7', '-Δ7', 'min/M7'),
    'augmented major 7th': ('augmaj7', '+M7', 'M7+5', 'maj7#5', 'maj7+5'),
    'augmented 7th': ('aug7', '+7', '7#5', '7+5'),
    'major 6 (add b5)': ('maj6b5', '6add♭5', 'maj6(♭5)', '6/♭5'),
    'dominant 6 (add b5)': ('dom6b5','7b5(no 3rd)','7♭5(no3)'),
    'major 6th': ('maj6', '6', 'M6'),
    'minor 6th': ('min6', 'm6', '-6'),
    'dominant 9th': ('dom9', '9'),
    'dominant 11th': ('dom11', '11'),
    'dominant 13th': ('dom13', '13'),
    'major 9th': ('maj9', 'M9', 'Δ9'),
    'major 11th': ('maj11', 'M11', 'Δ11'),
    'major 13th': ('maj13', 'M13', 'Δ13'),
    'minor 9th': ('min9', 'm9', '-9'),
    'minor 11th': ('min11', 'm11', '-11'),
    'minor 13th': ('min13', 'm13', '-13'),
    'minor major 9': ('minmaj9', 'mM9', 'mMaj9', '-Δ9', 'min/M9'),
    'major 7 (#11)': ('maj7#11', 'Δ7(#11)', 'M7#11'),
    'major 13 (#11)': ('maj13#11', 'M13#11', 'Δ13#11'),
    'dominant 13 (#11)': ('dom13#11', '13#11'),
    'dominant 7 (b9)': ('dom7b9', '7b9'),
    'dominant 7 (#9)': ('dom7#9', '7#9'),
    'dominant 13 (b9)': ('dom13b9', '13b9'),
    'dominant 7 (sus4, b9)': ('dom7sus4b9', '7sus4b9'),
    'dominant 13 (sus4)': ('dom13sus4', '13sus4'),
    'major (no5)': ('maj(no5)', 'maj(no3rd)'),
    'minor (no5)': ('min(no5)', 'm(no5)', 'm(no3rd)'),
    '7 (no5)': ('7(no5)', '7(no3rd)'),
    'm7 (no5)': ('min7(no5)', 'm7(no5)', 'm7(no3rd)'),
    'power chord': ('5', 'no3'),
    '7 (omit 3)': ('7(omit3)'),
    'add9': ('(add9)', 'add2'),
    'madd9': ('min(add9)', 'm(add9)', 'min(add2)', 'm(add2)'),
    'add11': ('(add11)', 'add4'),
    'madd11': ('min(add11)', 'm(add11)', 'min(add4)', 'm(add4)'),
    '6/9': ('69'),
    'm6/9': ('m69', 'min6/9', '-6/9'),
    'm7 add11': ('min7add11', 'm7add11', 'm7add4'),
    'major': ('maj', 'M'),
    'minor': ('min', 'm', '-')
}

@staticmethod
def get_chord_by_name(name):
    # Convert the name to lowercase

    # If the name is an alternate name, map it to the original name
    for original_name, alternate_names in alternate_chord_names.items():
        if name in alternate_names:
            return original_name

    # If the name is an original name, return it as is
    if name in chord_map:
        return name
    else:
        return None
    

#Dictionary of chord names and their spellings in standard and integer notation.
#Source: https://www.brendanpauljacobs.com/spelling.htm
#       ,ChatGPT
chord_map = {
    'major 7th': ('1 3 5 7', (0, 4, 7, 11)),
    'dominant 7th': ('1 3 5 b7', (0, 4, 7, 10)),
    'minor 7th': ('1 b3 5 b7', (0, 3, 7, 10)),
    'half-diminished 7th': ('1 b3 b5 b7', (0, 3, 6, 10)),
    'diminished 7th': ('1 b3 b5 bb7', (0, 3, 6, 9)),
    'minor major 7th': ('1 b3 5 7', (0, 3, 7, 11)),
    'augmented major 7th': ('1 3 #5 7', (0, 4, 8, 11)),
    'augmented 7th': ('1 3 #5 b7', (0, 4, 8, 10)),
    'major 6 (add b5)': ('1 3 b5 6', (0, 4, 6, 9)),
    'dominant 6 (add b5)': ('1 3 b5 b7', (0, 4, 6, 10)),
    'major 6th': ('1 3 5 6', (0, 4, 7, 9)),
    'minor 6th': ('1 b3 5 6', (0, 3, 7, 9)),
    'dominant 9th': ('1 3 5 b7 9', (0, 4, 7, 10, 2)),
    'dominant 11th': ('1 3 5 b7 9 11', (0, 4, 7, 10, 2, 5)),
    'dominant 13th': ('1 3 5 b7 9 11 13', (0, 4, 7, 10, 2, 5, 9)),
    'major 9th': ('1 3 5 7 9', (0, 4, 7, 11, 2)),
    'major 11th': ('1 3 5 7 9 11', (0, 4, 7, 11, 2, 5)),
    'major 13th': ('1 3 5 7 9 11 13', (0, 4, 7, 11, 2, 5, 9)),
    'minor 9th': ('1 b3 5 b7 9', (0, 3, 7, 10, 2)),
    'minor 11th': ('1 b3 5 b7 9 11', (0, 3, 7, 10, 2, 5)),
    'minor 13th': ('1 b3 5 b7 9 11 13', (0, 3, 7, 10, 2, 5, 9)),
    'minor major 9': ('1 b3 5 7 9', (0, 3, 7, 11, 2)),
    'major 7 (#11)': ('1 3 5 7 #11', (0, 4, 7, 11, 6)),
    'major 13 (#11)': ('1 3 5 7 9 #11 13', (0, 4, 7, 11, 2, 6, 9)),
    'dominant 13 (#11)': ('1 3 5 b7 9 #11 13', (0, 4, 7, 10, 2, 6, 9)),
    'dominant 7 (b9)': ('1 3 5 b7 b9', (0, 4, 7, 10, 1)),
    'dominant 7 (#9)': ('1 3 5 b7 #9', (0, 4, 7, 10, 3)),
    'dominant 13 (b9)': ('1 3 5 b7 9 b13', (0, 4, 7, 10, 2, 8)),
    'dominant 7 (sus4, b9)': ('1 4 5 b7 b9', (0, 5, 7, 10, 1)),
    'dominant 13 (sus4)': ('1 4 5 b7 9 13', (0, 5, 7, 10, 2, 9)),
    'major (no5)': ('1 3', (0, 4)),
    'minor (no5)': ('1 b3', (0, 3)),
    '7 (no5)': ('1 3 b7', (0, 4, 10)),
    'm7 (no5)': ('1 b3 b7', (0, 3, 10)),
    'power chord': ('1 5', (0, 7)),
    '7 (omit 3)': ('1 5 b7', (0, 7, 10)),
    'add9': ('1 3 5 9', (0, 4, 7, 2)),
    'madd9': ('1 b3 5 9', (0, 3, 7, 2)),
    'add11': ('1 3 5 11', (0, 4, 7, 5)),
    'madd11': ('1 b3 5 11', (0, 3, 7, 5)),
    '6/9': ('1 3 5 6 9', (0, 4, 7, 9, 2)),
    'm6/9': ('1 b3 5 6 9', (0, 3, 7, 9, 2)),
    'm7 add11': ('1 b3 5 b7 11', (0, 3, 7, 10, 5)),
    'major': (('1 3 5'), (0, 4, 7)),
    'minor': (('1 b3 5'), (0, 3, 7))}


chord_map_invert = {v[1]: (k, v[0]) for k, v in chord_map.items()}

#Dictionary of scale names and their spellings in integer notation. 
#Source: https://www.daqarta.com/dw_ss0a.htm
scale_map = {'Aeolian': (0, 2, 3, 5, 7, 8, 10),
 'Aeolian Flat 0': (0, 3, 4, 6, 8, 9, 11),
 'Algerian': (0, 2, 3, 5, 6, 7, 8, 11),
 'Altered Pentatonic': (0, 1, 5, 7, 9),
 'Alternate TetraMirror': (0, 1, 3, 4),
 'Arabian 0': (0, 2, 3, 5, 6, 8, 9, 11),
 'Arabian 1': (0, 2, 4, 5, 6, 8, 10),
 'Arabian Zirafkend': (0, 2, 3, 5, 7, 8, 9, 11),
 'Augmented': (0, 3, 4, 6, 8, 11),
 'Augmented Chord': (0, 4, 8),
 'Balinese': (0, 1, 3, 7, 8),
 'Balinese Pentatonic': (0, 1, 4, 6, 7),
 'Bebop Chromatic': (0, 1, 2, 4, 5, 7, 9, 10, 11),
 'Bebop Dominant': (0, 2, 4, 5, 7, 9, 10, 11),
 'Bebop Half-Diminished': (0, 1, 3, 5, 6, 7, 8, 11),
 'Bebop Major': (0, 2, 4, 5, 7, 8, 9, 11),
 'Bebop Major Heptatonic': (0, 2, 4, 5, 7, 8, 9),
 'Bebop Major Hexatonic': (0, 2, 4, 7, 8, 9),
 'Bebop Minor': (0, 2, 3, 4, 5, 7, 9, 10),
 'Bebop Minor Heptatonic': (0, 2, 3, 4, 7, 9, 10),
 'Bhairubahar Thaat': (0, 1, 4, 5, 7, 9, 11),
 'Blues Diminished': (0, 1, 3, 4, 6, 7, 9, 10),
 'Blues Dorian Hexatonic': (0, 1, 3, 4, 7, 9),
 'Blues Enneatonic': (0, 2, 3, 4, 5, 6, 7, 9, 10),
 'Blues Heptatonic': (0, 3, 5, 6, 7, 9, 10),
 'Blues Leading Tone': (0, 3, 5, 6, 7, 10, 11),
 'Blues Major': (0, 2, 3, 4, 7, 9),
 'Blues Minor': (0, 3, 5, 6, 7, 10),
 'Blues Minor Maj7': (0, 3, 5, 6, 7, 11),
 'Blues Modified': (0, 2, 3, 5, 6, 7, 10),
 'Blues Octatonic': (0, 2, 3, 5, 6, 7, 9, 10),
 'Blues Pentacluster': (0, 1, 2, 3, 6),
 'Blues Phrygian': (0, 1, 3, 5, 6, 7, 10),
 'Blues V': (0, 3, 5, 6, 11),
 'Byzantine': (0, 1, 4, 5, 7, 8, 11),
 'Centered PentaMirror': (0, 3, 4, 5, 8),
 'Chaio': (0, 2, 5, 8, 10),
 'Chinese': (0, 4, 6, 7, 11),
 'Chinese Bi Yu': (0, 3, 7, 10),
 'Chinese Mongolian': (0, 2, 4, 7, 9),
 'Chinese Youlan': (0, 1, 2, 4, 5, 6, 7, 9, 10),
 'Chord -4 (b5)': (0, 4, 6),
 'Chord 1': (0, 2, 4, 7),
 'Chord 5th (power)': (0, 7),
 'Chord 6+4': (0, 4, 8, 10),
 'Chord 6-4': (0, 4, 6, 10),
 'Chord 6/5': (0, 4, 7, 9, 10),
 'Chord 7sus4': (0, 5, 7, 10),
 'Chord 7th': (0, 4, 7, 10),
 'Chord M6': (0, 4, 7, 9),
 'Chord M7': (0, 4, 7, 11),
 'Chord M7+4': (0, 4, 8, 11),
 'Chord Major': (0, 4, 7),
 'Chord aug (+4)': (0, 4, 9),
 'Chord dim': (0, 3, 6),
 'Chord dim7': (0, 3, 6, 9),
 'Chord m6': (0, 3, 7, 9),
 'Chord m7': (0, 3, 7, 10),
 'Chord m7-4': (0, 3, 6, 10),
 'Chord mM7': (0, 3, 7, 11),
 'Chord minor': (0, 3, 7),
 'Chord sus2': (0, 2, 6),
 'Chord sus4': (0, 5, 7),
 'Chrom. Hypodorian Inv.': (0, 3, 4, 5, 8, 9, 10),
 'Chrom. Hypolydian Inv.': (0, 1, 4, 5, 6, 8, 11),
 'Chromatic': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
 'Chromatic DecaMirror': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
 'Chromatic HeptaMirror': (0, 1, 2, 3, 4, 5, 6),
 'Chromatic HexaMirror': (0, 1, 2, 3, 4, 5),
 'Chromatic Hypodorian': (0, 2, 3, 4, 7, 8, 9),
 'Chromatic Hypolydian': (0, 1, 4, 6, 7, 8, 11),
 'Chromatic NonaMirror': (0, 1, 2, 3, 4, 5, 6, 7, 8),
 'Chromatic OctaMirror': (0, 1, 2, 3, 4, 5, 6, 7),
 'Chromatic PentaMirror': (0, 1, 2, 3, 4),
 'Chromatic TetraMirror': (0, 1, 2, 3),
 'Chromatic TriMirror': (0, 1, 2),
 'Chromatic UndecaMirror': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
 'Diatonic': (0, 2, 4, 7, 9),
 'Diatonic Dorian Chrom.': (0, 1, 2, 3, 5, 7, 8, 9, 10),
 'Diatonic Dorian Perm.': (0, 1, 2, 4, 5, 7, 8, 9, 11),
 'Diminished': (0, 2, 3, 5, 6, 8, 9, 11),
 'Diminished 7th Chord': (0, 3, 6, 9),
 'Diminished Chord': (0, 3, 6),
 'Diminished Whole Tone': (0, 1, 3, 4, 6, 8, 10),
 'Dominant 7th': (0, 2, 4, 5, 7, 9, 10),
 'Dominant Pentatonic': (0, 2, 4, 7, 10),
 'Dorian': (0, 2, 3, 5, 7, 9, 10),
 'Dorian Aeolian': (0, 2, 3, 5, 7, 8, 9, 10),
 'Dorian Chromatic': (0, 1, 2, 5, 7, 8, 9),
 'Dorian Chromatic Inv.': (0, 3, 4, 5, 7, 10, 11),
 'Dorian Pentatonic': (0, 2, 3, 7, 9),
 'Dorian Tetrachord': (0, 2, 3, 5),
 'Dorian b5': (0, 2, 3, 5, 6, 9, 10),
 'Dorico Flamenco': (0, 1, 4, 5, 7, 8, 10),
 'Double Harmonic': (0, 1, 4, 5, 7, 8, 11),
 'Egyptian': (0, 2, 5, 7, 10),
 'Enigmatic': (0, 1, 4, 5, 6, 8, 10, 11),
 'Enigmatic Ascending': (0, 1, 4, 6, 8, 10, 11),
 'Enigmatic Descending': (0, 1, 4, 5, 8, 10, 11),
 'Enigmatic Minor': (0, 1, 3, 6, 8, 10, 11),
 'Eskimo Hexatonic 0': (0, 2, 4, 6, 8, 11),
 'Eskimo Hexatonic 1': (0, 2, 4, 6, 8, 9),
 'Eskimo Tetratonic': (0, 2, 4, 7),
 'Ethiopian 0': (0, 2, 4, 5, 7, 9, 11),
 'Ethiopian 1': (0, 2, 4, 5, 7, 8, 11),
 'Ethiopian 2': (0, 2, 3, 5, 7, 8, 10),
 'Flamenco': (0, 1, 3, 4, 5, 7, 8, 10),
 'Full Minor all flats': (0, 2, 3, 5, 7, 8, 9, 10, 11),
 'Genus Chromaticum': (0, 1, 3, 4, 5, 7, 8, 9, 11),
 'Genus Primum Inverse': (0, 5, 7, 10),
 'Genus Secundum': (0, 4, 5, 7, 9, 11),
 'Gnossiennes': (0, 2, 3, 6, 7, 9, 10),
 'Greek Houseini': (0, 2, 3, 4, 5, 7, 8, 9, 10),
 'Greek Houzam': (0, 3, 4, 5, 7, 9, 11),
 'Greek Kiourdi': (0, 2, 3, 5, 6, 7, 8, 9, 10),
 'Greek Neveseri': (0, 1, 3, 6, 7, 8, 10, 11),
 'Greek Sabach': (0, 2, 3, 4, 7, 8, 10),
 'Gypsy Hexatonic 0': (0, 1, 5, 6, 8, 9, 10),
 'Gypsy Hexatonic 1': (0, 1, 4, 5, 7, 8, 9),
 'Half Diminished': (0, 1, 3, 5, 6, 8, 10),
 'Half Diminished 1': (0, 2, 3, 5, 6, 8, 10),
 'Harm. Min. Tetrachord': (0, 2, 3, 6),
 'Harm. Neapolitan Minor': (0, 1, 2, 3, 5, 7, 8, 11),
 'Harmonic Major': (0, 2, 4, 5, 7, 8, 11),
 'Harmonic Major 1': (0, 2, 4, 5, 8, 9, 11),
 'Harmonic Minor': (0, 2, 3, 5, 7, 8, 11),
 'Harmonic Minor Inv.': (0, 1, 4, 5, 7, 9, 10),
 'Hawaiian 0': (0, 2, 3, 7, 9, 11),
 'Hawaiian 1': (0, 2, 3, 5, 7, 9, 11),
 'Hindi IV & V': (0, 2, 4, 6, 8, 9, 11),
 'Hindi IV & bVII': (0, 2, 4, 6, 7, 9, 10),
 'Hindu': (0, 2, 4, 5, 7, 8, 10),
 'Honchoshi Plagal Form': (0, 1, 3, 5, 6, 10),
 'Hungarian Folk': (0, 1, 4, 5, 7, 8, 11),
 'Hungarian Gypsy': (0, 2, 3, 6, 7, 8, 10),
 'Hungarian Major': (0, 3, 4, 6, 7, 9, 10),
 'Hungarian Minor': (0, 2, 3, 6, 7, 8, 11),
 'Hungarian Minor b2': (0, 1, 2, 3, 6, 7, 8, 11),
 'Hypophrygian Inv.': (0, 1, 2, 5, 6, 7, 9),
 'Ionian': (0, 2, 4, 5, 7, 9, 11),
 'Ionian 4': (0, 2, 4, 5, 8, 9, 11),
 'Ionian Pentatonic': (0, 4, 5, 7, 11),
 'Japanese Han-Kumoi': (0, 2, 5, 7, 8),
 'Japanese Hirajoshi': (0, 2, 3, 7, 8),
 'Japanese Ichikosucho': (0, 2, 4, 5, 6, 7, 9, 11),
 'Japanese Iwato': (0, 1, 5, 6, 10),
 'Japanese Kokin-Joshi': (0, 1, 5, 7, 10),
 'Japanese Kumoi': (0, 2, 3, 7, 9),
 'Japanese Nohkan': (0, 2, 5, 6, 8, 9, 11),
 'Japanese Pentachord': (0, 1, 3, 6, 7),
 'Japanese Ritusen': (0, 2, 5, 7, 9),
 'Japanese Sakura': (0, 1, 5, 7, 8),
 'Japanese Sanagari': (0, 5, 10),
 'Japanese Taishikicho': (0, 2, 4, 5, 6, 7, 9, 10, 11),
 'Javanese': (0, 1, 3, 5, 7, 9, 10),
 'Jazz Minor Inverse': (0, 1, 3, 5, 7, 9, 10),
 'Jewish Adonai Malakh': (0, 1, 2, 3, 5, 7, 9, 10),
 'Jewish Ahaba Rabba': (0, 1, 4, 5, 7, 8, 10),
 'Kung': (0, 2, 4, 6, 9),
 'Leading Whole Tone': (0, 2, 4, 6, 8, 10, 11),
 'Locrian': (0, 1, 3, 5, 6, 8, 10),
 'Locrian 1': (0, 2, 3, 5, 6, 8, 11),
 'Locrian Natural Maj 5': (0, 1, 3, 5, 6, 9, 10),
 'Locrian PentaMirror': (0, 1, 3, 5, 6),
 'Locrian bb7': (0, 1, 3, 5, 6, 8, 9),
 'Lydian': (0, 2, 4, 6, 7, 9, 11),
 'Lydian 1': (0, 3, 4, 6, 7, 9, 11),
 'Lydian 1 Hexatonic': (0, 3, 4, 7, 9, 11),
 'Lydian Augmented': (0, 2, 4, 6, 8, 9, 11),
 'Lydian Chromatic': (0, 1, 4, 5, 6, 9, 11),
 'Lydian Chromatic Inv.': (0, 1, 3, 6, 7, 8, 11),
 'Lydian Diminished': (0, 2, 3, 6, 7, 9, 11),
 'Lydian Dominant': (0, 2, 4, 6, 7, 9, 10),
 'Lydian Hexatonic': (0, 2, 4, 7, 9, 11),
 'Lydian Minor': (0, 2, 4, 6, 7, 8, 10),
 'Lydian Mixolydian': (0, 2, 4, 5, 6, 7, 9, 10, 11),
 'Lydian Pentachord': (0, 2, 4, 6, 7),
 'Magen Abot 0': (0, 1, 3, 4, 6, 8, 10, 11),
 'Magen Abot 1': (0, 1, 3, 4, 6, 8, 9, 11),
 'Major': (0, 2, 4, 5, 7, 9, 11),
 'Major & Minor mixed': (0, 2, 3, 4, 5, 7, 8, 9, 10, 11),
 'Major Dominant b7': (0, 3, 6, 8),
 'Major Locrian': (0, 2, 4, 5, 6, 8, 10),
 'Major Lydian': (0, 2, 4, 5, 6, 7, 9, 11),
 'Major Minor': (0, 2, 4, 5, 7, 8, 10),
 'Major Pentachord': (0, 2, 4, 5, 7),
 'Major Tetrachord': (0, 2, 4, 5),
 'Major b7 Chord': (0, 3, 5, 9),
 'Major b7 Chord 1': (0, 2, 6, 9),
 'Maqam Hijaz': (0, 1, 4, 5, 7, 8, 10, 11),
 "Maqam Shadd'araban": (0, 1, 3, 4, 5, 6, 9, 10),
 'Mela Bhavapriya': (0, 1, 3, 6, 7, 8, 10),
 'Mela Chakravakam': (0, 1, 4, 5, 7, 9, 10),
 'Mela Chalanata': (0, 3, 4, 5, 7, 10, 11),
 'Mela Charukesi': (0, 2, 4, 5, 7, 8, 10),
 'Mela Citrambari': (0, 2, 4, 6, 7, 10, 11),
 'Mela Dharmavati': (0, 2, 3, 6, 7, 9, 11),
 'Mela Dhatuvardhani': (0, 3, 4, 6, 7, 8, 11),
 'Mela Dhavalambari': (0, 1, 4, 6, 7, 8, 9),
 'Mela Dhenuka': (0, 1, 3, 5, 7, 8, 11),
 'Mela Dhirasankara': (0, 2, 4, 5, 7, 9, 11),
 'Mela Divamani': (0, 1, 3, 6, 7, 10, 11),
 'Mela Gamanasrama': (0, 1, 4, 6, 7, 9, 11),
 'Mela Ganamurti': (0, 1, 2, 5, 7, 8, 11),
 'Mela Gangeyabhusani': (0, 3, 4, 5, 7, 8, 11),
 'Mela Gaurimanohari': (0, 2, 3, 5, 7, 9, 11),
 'Mela Gavambohdi': (0, 1, 3, 6, 7, 8, 9),
 'Mela Gayakapriya': (0, 1, 4, 5, 7, 8, 9),
 'Mela Hanumattodi': (0, 1, 3, 5, 7, 8, 10),
 'Mela Harikambhoji': (0, 2, 4, 5, 7, 9, 10),
 'Mela Hatakambari': (0, 1, 4, 5, 7, 10, 11),
 'Mela Hemavati': (0, 2, 3, 6, 7, 9, 10),
 'Mela Jalarnavam': (0, 1, 2, 6, 7, 8, 10),
 'Mela Jhalavarali': (0, 1, 2, 6, 7, 8, 11),
 'Mela Jhankaradhvani': (0, 2, 3, 5, 7, 8, 9),
 'Mela Jhotisvarupini': (0, 3, 4, 6, 7, 8, 10),
 'Mela Kamavardhani': (0, 1, 4, 6, 7, 8, 11),
 'Mela Kanakangi': (0, 1, 2, 5, 7, 8, 9),
 'Mela Kantamani': (0, 2, 4, 6, 7, 8, 9),
 'Mela Kharaharapriya': (0, 2, 3, 5, 7, 9, 10),
 'Mela Kiravani': (0, 2, 3, 5, 7, 8, 11),
 'Mela Kokilapriya': (0, 1, 3, 5, 7, 9, 11),
 'Mela Kosalam': (0, 3, 4, 6, 7, 9, 11),
 'Mela Latangi': (0, 2, 4, 6, 7, 8, 11),
 'Mela Manavati': (0, 1, 2, 5, 7, 9, 11),
 'Mela Mararanjani': (0, 2, 4, 5, 7, 8, 9),
 'Mela Mechakalyani': (0, 2, 4, 6, 7, 9, 11),
 'Mela Nagananadini': (0, 2, 4, 5, 7, 10, 11),
 'Mela Namanarayani': (0, 1, 4, 6, 7, 8, 10),
 'Mela Natabhairavi': (0, 2, 3, 5, 7, 8, 10),
 'Mela Natakapriya': (0, 1, 3, 5, 7, 9, 10),
 'Mela Navanitam': (0, 1, 2, 6, 7, 9, 10),
 'Mela Nitimati': (0, 2, 3, 6, 7, 10, 11),
 'Mela Pavani': (0, 1, 2, 6, 7, 9, 11),
 'Mela Ragavardhani': (0, 3, 4, 5, 7, 8, 10),
 'Mela Raghupriya': (0, 1, 2, 6, 7, 10, 11),
 'Mela Ramapriya': (0, 1, 4, 6, 7, 9, 10),
 'Mela Rasikapriya': (0, 3, 4, 6, 7, 10, 11),
 'Mela Ratnangi': (0, 1, 2, 5, 7, 8, 10),
 'Mela Risabhapriya': (0, 2, 4, 6, 7, 8, 10),
 'Mela Rupavati': (0, 1, 3, 5, 7, 10, 11),
 'Mela Sadvidhamargini': (0, 1, 3, 6, 7, 9, 10),
 'Mela Salaga': (0, 1, 2, 6, 7, 8, 9),
 'Mela Sanmukhapriya': (0, 2, 3, 6, 7, 8, 10),
 'Mela Sarasangi': (0, 2, 4, 5, 7, 8, 11),
 'Mela Senavati': (0, 1, 3, 5, 7, 8, 9),
 'Mela Simhendramadhyama': (0, 2, 3, 6, 7, 8, 11),
 'Mela Subhapantuvarali': (0, 1, 3, 6, 7, 8, 11),
 'Mela Sucharitra': (0, 3, 4, 6, 7, 8, 9),
 'Mela Sulini': (0, 3, 4, 5, 7, 9, 11),
 'Mela Suryakantam': (0, 1, 4, 5, 7, 9, 11),
 'Mela Syamalangi': (0, 2, 3, 6, 7, 8, 9),
 'Mela Tanarupi': (0, 1, 2, 5, 7, 10, 11),
 'Mela Vagadhisvari': (0, 3, 4, 5, 7, 9, 10),
 'Mela Vanaspati': (0, 1, 2, 5, 7, 9, 10),
 'Mela Varunapriya': (0, 2, 3, 5, 7, 10, 11),
 'Mela Vaschaspati': (0, 2, 4, 6, 7, 9, 10),
 'Mela Visvambhari': (0, 1, 4, 6, 7, 10, 11),
 'Mela Yagapriya': (0, 3, 4, 5, 7, 8, 9),
 'Melodic Minor (Ascend)': (0, 2, 3, 5, 7, 9, 11),
 'Messiaen 1 Brown': (0, 2, 3, 5, 6, 8, 10, 11),
 'Messiaen 1 Groves': (0, 2, 3, 5, 6, 8, 9, 11),
 'Messiaen 2nd Mode': (0, 3, 6, 9),
 'Messiaen 2 Brown': (0, 1, 3, 5, 6, 7, 9, 11),
 'Messiaen 3rd Mode': (0, 4, 8),
 'Messiaen 5th Groves': (0, 1, 2, 6, 7, 8),
 'Messiaen Mode 1-0': (0, 5, 6, 11),
 'Messiaen Mode 1-1': (0, 3, 5, 6, 9, 11),
 'Messiaen Mode 1-2': (0, 2, 5, 6, 8, 11),
 'Messiaen Mode 1-3': (0, 1, 6, 7),
 'Messiaen Mode 2': (0, 1, 2, 4, 5, 6, 8, 9, 10),
 'Messiaen Mode 2 Inv.': (0, 2, 3, 4, 6, 7, 8, 10, 11),
 'Messiaen Mode 3 Inv.': (0, 3, 4, 5, 6, 9, 10, 11),
 'Messiaen Mode 3-0': (0, 1, 2, 5, 6, 7, 8, 11),
 'Messiaen Mode 3-1': (0, 1, 2, 3, 6, 7, 8, 9),
 'Messiaen Mode 4': (0, 1, 5, 6, 7, 11),
 'Messiaen Mode 4 Inv': (0, 4, 5, 6, 10, 11),
 'Messiaen Mode 5 Inv.': (0, 2, 4, 5, 6, 8, 10, 11),
 'Messiaen Mode 5-0': (0, 2, 4, 5, 7, 9, 10, 11),
 'Messiaen Mode 5-1': (0, 1, 2, 4, 6, 7, 8, 10),
 'Messiaen Mode 6 Inv.': (0, 2, 3, 4, 5, 6, 8, 9, 10, 11),
 'Messiaen Mode 6-0': (0, 1, 2, 3, 5, 6, 7, 8, 9, 11),
 'Messiaen Mode 6-1': (0, 1, 2, 3, 4, 6, 7, 8, 9, 10),
 'Messiaen Trunc 5 Inv.': (0, 4, 6, 10),
 'Messiaen Trunc. Mode 5': (0, 2, 6, 8),
 'Messiaen Truncated': (0, 3, 6, 10),
 'Messiaen Truncated 1': (0, 1, 3, 6, 7, 9),
 'Messiaen Truncated 2': (0, 1, 4, 5, 8, 9),
 'Minor 6th Added': (0, 3, 5, 7, 9),
 'Minor Hexatonic': (0, 2, 3, 5, 7, 10),
 'Minor Locrian': (0, 2, 3, 5, 6, 8, 10),
 'Minor Pentachord': (0, 2, 3, 5, 7),
 'Minor Pentatonic Lead': (0, 2, 3, 4, 5, 6, 7, 9, 10, 11),
 'Minor Trichord': (0, 2, 3),
 'Mixolydian': (0, 2, 4, 5, 7, 9, 10),
 'Mixolydian Augmented': (0, 2, 4, 5, 8, 9, 10),
 'Mixolydian Chrom. Inv.': (0, 2, 5, 6, 7, 10, 11),
 'Mixolydian Chromatic 0': (0, 1, 2, 5, 6, 7, 10),
 'Mixolydian Chromatic 1': (0, 1, 2, 4, 6, 7, 10),
 'Mixolydian Hexatonic': (0, 2, 5, 7, 9, 10),
 'Mixolydian Pentatonic': (0, 4, 5, 7, 10),
 'Mixolydian b5': (0, 2, 4, 5, 6, 9, 10),
 'Mohammedan': (0, 2, 3, 5, 7, 8, 11),
 'Moorish Phrygian': (0, 1, 3, 4, 5, 7, 8, 10, 11),
 'Natural Minor': (0, 2, 3, 5, 7, 8, 10),
 'Neapolitan Major': (0, 1, 3, 5, 7, 9, 11),
 'Neapolitan Minor': (0, 1, 3, 5, 7, 8, 11),
 'Neapolitan Minor 1': (0, 1, 2, 4, 6, 8, 9),
 'Neopolitan Minor 1': (0, 1, 3, 5, 7, 8, 10),
 'Nine Tone': (0, 2, 3, 4, 6, 7, 8, 9, 11),
 'Octatonic JG': (0, 1, 3, 4, 5, 7, 9, 10),
 'Oriental 0': (0, 1, 4, 5, 6, 9, 10),
 'Oriental 1': (0, 1, 4, 5, 6, 9, 10, 11),
 'Oriental 2': (0, 1, 4, 5, 6, 8, 10),
 'Oriental Pentacluster': (0, 1, 2, 5, 6),
 'Overtone': (0, 2, 4, 6, 7, 9, 10),
 'Pelog': (0, 2, 4, 6, 7, 8, 11),
 'Pelog 0': (0, 1, 3, 7, 8),
 'Pelog 1': (0, 1, 3, 7, 10),
 'Pentatonic Major': (0, 2, 4, 7, 9),
 'Pentatonic Minor': (0, 3, 5, 7, 10),
 'Pentatonic Neutral': (0, 2, 5, 7, 10),
 'Persian': (0, 1, 4, 5, 6, 8, 11),
 'Phrygian': (0, 1, 3, 5, 7, 8, 10),
 'Phrygian Aeolian': (0, 1, 2, 3, 5, 7, 8, 10),
 'Phrygian Chrom. Inv.': (0, 1, 2, 4, 7, 8, 9),
 'Phrygian Chromatic': (0, 3, 4, 5, 8, 10, 11),
 'Phrygian Dominant': (0, 1, 4, 5, 7, 8, 10),
 'Phrygian Double Hex.': (0, 1, 3, 5, 6, 9),
 'Phrygian Hexatonic': (0, 3, 5, 7, 8, 10),
 'Phrygian Locrian': (0, 1, 3, 5, 6, 7, 8, 10),
 'Phrygian Major': (0, 1, 3, 4, 5, 7, 8, 10),
 'Phrygian Tetrachord': (0, 1, 3, 5),
 'Phrygian Trichord': (0, 1, 3),
 'Prokofiev': (0, 1, 3, 5, 6, 8, 10, 11),
 'Prometheus': (0, 2, 4, 6, 9, 10),
 'Prometheus Neapolitan': (0, 1, 4, 6, 9, 10),
 'Pseudo Turkish': (0, 1, 3, 5, 6, 9, 10),
 'Pyramid Hexatonic': (0, 2, 3, 5, 6, 9),
 'Raga Abhogi': (0, 2, 3, 5, 9),
 'Raga Amarasenapriya': (0, 2, 3, 6, 7, 11),
 'Raga Audva Tukhari': (0, 2, 3, 5, 8),
 'Raga Bagesri': (0, 2, 3, 5, 9, 10),
 'Raga Bauli': (0, 1, 4, 7, 8, 11),
 'Raga Bhanumanjari': (0, 3, 4, 5, 7, 10),
 'Raga Bhatiyar': (0, 1, 4, 5, 6, 7, 9, 11),
 'Raga Bhavani': (0, 1, 3, 6, 8, 10),
 'Raga Bhinna Pancama': (0, 2, 5, 7, 8, 11),
 'Raga Bhinna Shadja': (0, 4, 5, 9, 11),
 'Raga Bhupeshwari': (0, 2, 4, 7, 8),
 'Raga Bilwadala': (0, 4, 9),
 'Raga Caturangini': (0, 2, 4, 6, 7, 11),
 'Raga Chand. Kiravani': (0, 3, 5, 8, 11),
 'Raga Chandrajyoti': (0, 1, 2, 6, 7, 9),
 'Raga Chandrakauns': (0, 3, 5, 9, 11),
 'Raga Chandrakauns Kafi': (0, 3, 5, 9, 10),
 'Raga Chhaya Todi': (0, 1, 3, 6, 8),
 'Raga Chitthakarshini': (0, 1, 3, 5, 8),
 'Raga Cintamani': (0, 2, 3, 6, 7, 8, 9, 10),
 'Raga Desh': (0, 2, 5, 7, 11),
 'Raga Deshgaur': (0, 1, 7, 8, 11),
 'Raga Devaranjani': (0, 5, 7, 8, 11),
 'Raga Dhavalangam': (0, 1, 4, 6, 7, 8),
 'Raga Dhavalashri': (0, 4, 6, 7, 9),
 'Raga Dipak': (0, 2, 4, 5, 6, 7),
 'Raga Gambhiranata': (0, 4, 5, 7, 11),
 'Raga Gandharavam': (0, 1, 3, 5, 7, 10),
 'Raga Gaula': (0, 1, 4, 5, 7, 11),
 'Raga Gauri': (0, 1, 5, 7, 11),
 'Raga Ghantana': (0, 2, 3, 5, 8, 11),
 'Raga Guhamanohari': (0, 2, 5, 9, 10),
 'Raga Gujari Todi': (0, 1, 3, 6, 8, 11),
 'Raga Hamsa Vinodini': (0, 2, 4, 5, 9, 11),
 'Raga Hamsadhvani': (0, 2, 4, 7, 11),
 'Raga Hamsanandi': (0, 1, 4, 6, 9, 11),
 'Raga Harikauns': (0, 3, 6, 8, 10),
 'Raga Haripriya': (0, 2, 5, 8),
 'Raga Hejjajji': (0, 1, 4, 6, 8, 9),
 'Raga Hindol': (0, 4, 6, 9, 11),
 'Raga Indupriya': (0, 1, 4, 6, 7, 10),
 'Raga Jaganmohanam': (0, 2, 6, 7, 8, 10),
 'Raga Jayakauns': (0, 3, 5, 6, 10),
 'Raga Jivantika': (0, 1, 5, 7, 9, 11),
 'Raga Jivantini': (0, 3, 6, 7, 10, 11),
 'Raga Jyoti': (0, 4, 6, 7, 8, 10),
 'Raga Kalagada': (0, 1, 4, 7, 8, 10),
 'Raga Kalakanthi': (0, 1, 5, 7, 8, 9),
 'Raga Kalakanti': (0, 1, 5, 6, 8, 9, 10),
 'Raga Kalavati': (0, 1, 4, 5, 7, 9),
 'Raga Kamalamanohari': (0, 4, 5, 7, 8, 10),
 'Raga Kashyapi': (0, 1, 3, 7, 8, 10),
 'Raga Khamaji Durga': (0, 4, 5, 9, 10),
 'Raga Khamas': (0, 4, 5, 7, 9, 10),
 'Raga Kokil Pancham': (0, 3, 5, 7, 8),
 'Raga Kshanika': (0, 1, 5, 8, 11),
 'Raga Kuksumakaram': (0, 3, 4, 6, 7, 9, 11),
 'Raga Kumarapriya': (0, 1, 2, 8, 11),
 'Raga Kumurdaki': (0, 2, 4, 6, 11),
 'Raga Latika': (0, 2, 4, 7, 8, 11),
 'Raga Lavangi': (0, 1, 5, 8),
 'Raga Madhakauns': (0, 3, 6, 7, 9, 10),
 'Raga Madhuri': (0, 4, 5, 7, 9, 10, 11),
 'Raga Mahathi': (0, 4, 7, 10),
 'Raga Malahari': (0, 1, 4, 5, 7, 8),
 'Raga Malarani': (0, 2, 6, 7, 10, 11),
 'Raga Malashri': (0, 4, 6, 7, 11),
 'Raga Malayamarutam': (0, 1, 4, 7, 9, 10),
 'Raga Malkauns': (0, 3, 5, 8, 10),
 'Raga Mamata': (0, 4, 7, 9, 11),
 'Raga Manaranjani': (0, 1, 4, 7, 10),
 'Raga Manavi': (0, 2, 3, 7, 9, 10),
 'Raga Mand': (0, 4, 5, 7, 9),
 'Raga Mandari': (0, 1, 4, 6, 7, 11),
 'Raga Manohari': (0, 3, 5, 7, 9, 10),
 'Raga Matha Kokila': (0, 2, 7, 9, 10),
 'Raga Megh': (0, 2, 5, 7, 10, 11),
 'Raga Megharanjani': (0, 1, 4, 5, 8),
 'Raga Megharanji': (0, 1, 4, 5, 11),
 'Raga Mian Ki Malhar': (0, 2, 3, 5, 7, 9, 10, 11),
 'Raga Mohanangi': (0, 3, 4, 7, 9),
 'Raga Mrunganandana': (0, 2, 4, 6, 9, 11),
 'Raga Multani': (0, 3, 6, 7, 11),
 'Raga Nabhomani': (0, 1, 2, 6, 7),
 'Raga Nagagandhari': (0, 2, 5, 7, 9, 11),
 'Raga Nalinakanti': (0, 2, 4, 5, 7, 11),
 'Raga Nandkauns': (0, 3, 4, 5, 7, 9, 10),
 'Raga Nasamani': (0, 3, 4, 6, 7, 9, 10),
 'Raga Nata': (0, 3, 5, 7, 11),
 'Raga Nattaikurinji': (0, 2, 4, 5, 9, 10),
 'Raga Navamanohari': (0, 2, 5, 7, 8, 10),
 'Raga Neelangi': (0, 2, 3, 6, 8, 9),
 'Raga Nigamagamini': (0, 4, 6, 11),
 'Raga Nishadi': (0, 2, 6, 7, 9, 11),
 'Raga Ongkari': (0, 6, 7),
 'Raga Padi': (0, 1, 5, 7, 8, 11),
 'Raga Pahadi': (0, 2, 4, 5, 7, 8, 9, 10, 11),
 'Raga Paraju': (0, 4, 5, 7, 8, 11),
 'Raga Phenadyuti': (0, 1, 5, 7, 8, 10),
 'Raga Priyadharshini': (0, 2, 5, 8, 11),
 'Raga Puruhutika': (0, 5, 7, 9, 11),
 'Raga Putrika': (0, 1, 2, 8, 9),
 'Raga Ragesri': (0, 2, 4, 5, 9, 10, 11),
 'Raga Ramdasi Malhar': (0, 2, 3, 4, 5, 7, 9, 10, 11),
 'Raga Ramkali': (0, 1, 4, 5, 6, 7, 8, 11),
 'Raga Ranjani': (0, 2, 3, 6, 9, 11),
 'Raga Rasamanjari': (0, 3, 4, 6, 7, 11),
 'Raga Rasavali': (0, 1, 5, 7, 9, 10),
 'Raga Rasranjani': (0, 2, 5, 9, 11),
 'Raga Ratipriya': (0, 2, 4, 6, 7, 8, 10),
 'Raga Reva': (0, 1, 4, 7, 8),
 'Raga Rudra Pancama': (0, 1, 4, 5, 9, 10),
 'Raga Rukmangi': (0, 1, 3, 7, 10),
 'Raga Saildesakshi': (0, 3, 4, 5, 7, 9, 11),
 'Raga Salagavarali': (0, 1, 3, 7, 9, 10),
 'Raga Samudhra Priya': (0, 3, 6, 7, 10),
 'Raga Sarasanana': (0, 2, 4, 5, 8, 11),
 'Raga Sarasvati': (0, 2, 6, 7, 9, 10),
 'Raga Saravati': (0, 4, 5, 7, 8, 9),
 'Raga Sarvarsi': (0, 5, 7),
 'Raga Saugandhini': (0, 1, 6, 7, 8),
 'Raga Saurashtra': (0, 1, 4, 5, 7, 8, 9, 11),
 'Raga Shailaja': (0, 3, 7, 8, 10),
 'Raga Shri Kalyan': (0, 2, 6, 7, 9),
 'Raga Shubravarni': (0, 2, 6, 9, 11),
 'Raga Simantini': (0, 1, 3, 5, 7, 8),
 'Raga Simharava': (0, 2, 3, 6, 7, 10),
 'Raga Sindhura Kafi': (0, 2, 3, 5, 7, 11),
 'Raga Sindi Bhairavi': (0, 1, 2, 3, 4, 5, 7, 8, 10, 11),
 'Raga Siva Kambhoji': (0, 2, 4, 5, 7, 10),
 'Raga Sohini': (0, 1, 4, 5, 8, 11),
 'Raga Sorati': (0, 2, 5, 7, 9, 10, 11),
 'Raga Suddha Bangala': (0, 2, 3, 5, 7, 9),
 'Raga Suddha Mukhari': (0, 1, 2, 5, 8, 9),
 'Raga Sumukam': (0, 2, 6, 11),
 'Raga Syamalam': (0, 2, 3, 6, 7, 8),
 'Raga Takka': (0, 3, 5, 7, 8, 11),
 'Raga Tilang': (0, 4, 5, 7, 10, 11),
 'Raga Trimurti': (0, 2, 3, 7, 8, 10),
 'Raga Vaijayanti': (0, 2, 6, 7, 11),
 'Raga Valaji': (0, 4, 7, 9, 10),
 'Raga Vasanta': (0, 1, 4, 5, 9, 11),
 'Raga Vasantabhairavi': (0, 1, 4, 5, 8, 10),
 'Raga Vijayanagari': (0, 2, 3, 6, 7, 9),
 'Raga Vijayasri': (0, 1, 2, 6, 7, 11),
 'Raga Vijayavasanta': (0, 4, 6, 7, 10, 11),
 'Raga Viyogavarali': (0, 1, 3, 5, 8, 11),
 'Raga Vutari': (0, 4, 6, 7, 9, 10),
 'Raga Yamuna Kalyani': (0, 2, 4, 6, 7, 9),
 'Raga Zilaf': (0, 4, 5, 7, 8),
 'Ritsu': (0, 1, 3, 5, 8, 10),
 "Rock 'n Roll": (0, 3, 4, 5, 7, 9, 10),
 'Romanian Bacovia': (0, 4, 5, 8, 11),
 'Romanian Major': (0, 1, 4, 6, 7, 9, 10),
 'Roumanian Minor': (0, 2, 3, 6, 7, 9, 10),
 'Scottish Hexatonic': (0, 2, 4, 5, 7, 9),
 'Scottish Pentatonic': (0, 2, 5, 7, 9),
 'Shostakovich': (0, 1, 3, 4, 6, 7, 9, 11),
 'Six Tone Symmetrical': (0, 1, 4, 5, 8, 9),
 'Spanish 7 tone': (0, 1, 3, 4, 5, 6, 8, 10),
 'Spanish Gypsy': (0, 1, 4, 5, 7, 8, 10),
 'Spanish Heptatonic': (0, 3, 4, 5, 6, 8, 10),
 'Spanish Pentacluster': (0, 1, 3, 4, 5),
 'Super Locrian': (0, 1, 3, 4, 6, 8, 10),
 'Symmetrical Decatonic': (0, 1, 2, 4, 5, 6, 7, 8, 10, 11),
 'Symmetrical Nonatonic': (0, 1, 2, 4, 6, 7, 8, 10, 11),
 'Takemitsu Tree Line 0': (0, 2, 3, 6, 8, 11),
 'Takemitsu Tree Line 1': (0, 2, 3, 6, 8, 10),
 'Theta Asavari': (0, 2, 3, 5, 7, 8, 10),
 'Theta Bhairav': (0, 1, 4, 5, 7, 8, 11),
 'Theta Bhairavi': (0, 1, 3, 5, 7, 8, 10),
 'Theta Bilaval': (0, 2, 4, 5, 7, 9, 11),
 'Theta Kafi': (0, 2, 3, 5, 7, 9, 10),
 'Theta Kalyan': (0, 2, 4, 6, 7, 9, 11),
 'Theta Khamaj': (0, 2, 4, 5, 7, 9, 10),
 'Theta Marva': (0, 1, 4, 6, 7, 9, 11),
 'Theta Purvi': (0, 1, 4, 6, 7, 8, 11),
 'Theta Todi': (0, 1, 3, 6, 7, 8, 11),
 'Todi bVII': (0, 1, 3, 6, 7, 9, 10),
 'Ultra Locrian': (0, 1, 3, 4, 6, 8, 9),
 'Ute Tritone': (0, 3, 10),
 'Utility Minor': (0, 2, 3, 5, 7, 8, 10, 11),
 'Warao Minor Trichord': (0, 2, 3, 10),
 'Whole Tone': (0, 2, 4, 6, 8, 10),
 'Whole-Tone Tetramirror': (0, 2, 4, 6)}

scale_map_invert = {v: k for k, v in scale_map.items()}

# pprint.pprint(chord_map_invert)
# print()
# pprint.pprint(scale_map_invert)

chord_shapes = [
    [1, 1, 0, 2, 2, 1, 0],
    [2, 0, 1, 3, 2, 3, 1],
    [3, 0, 0, 1, 3, 3, 3],
    [1, 1, 0, 1, 1, 1, 0],
    [2, 0, 1, 3, 1, 2, 1],
    [3, 0, 0, 1, 3, 2, 2],
    [1, 1, 3, 1, 2, 1, 1],
    [2, 0, 1, 3, 1, 3, 1],
    [3, 0, 0, 1, 3, 2, 3],
    [1, 2, 0, 2, 2, 1, 0],
    [2, 0, 1, 2, 1, 2, 0],
    [3, 0, 0, 1, 2, 2, 2],
    [1, 2, 0, 1, 2, 1, 0],
    [2, 0, 2, 3, 1, 3, 0],
    [3, 0, 0, 1, 2, 1, 2],
]