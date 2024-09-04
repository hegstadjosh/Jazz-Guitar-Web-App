import pprint
import sys
import random
import music_data
from collections import deque
import sqlite3

"""
File Name: music_objects.py
Description: This file contains classes and functions for representing musical scales and chords, 
             and generating diagrams for them on a guitar fretboard.
Author: Joshua Hegstad
Date: 01/18/2024
Version: 1.2.1
"""                                                                                                    

base_notes =  [7, 12, 17, 22, 26, 31] #Standard tuning EADGBE in integer notation (A = 0, G# = 11)


# Define the Chord class and a function to create instances for each chord from the file
class Chord:
    """
    Represents a musical chord with standard and integer spellings.

    Attributes:
        name (str): The name of the chord.
        standard_spelling (str): The standard notation of the chord.
        integer_spelling (set of int): The integer representation of the chord.
    """

    def __init__(self, name = None, standard_spelling = None, integer_spelling = None):
        """
        Initializes a Chord instance.

        Parameters:
            name (str): The name of the chord.
            standard_spelling (str): The standard notation of the chord.
            integer_spelling (set of int): The integer representation of the chord.
        """
        self.name = name
        self.integer_spelling = integer_spelling
        self.standard_spelling = standard_spelling
        self.shape = None
        if not standard_spelling and integer_spelling:
            # Convert from integer to standard
            if isinstance(integer_spelling, str):
                integer_spelling = tuple(sorted(map(int, integer_spelling.split())))
            else:
                integer_spelling = tuple(sorted(integer_spelling))
                
            self.standard_spelling = music_data.convert_spelling(integer_spelling, 1)
            self.integer_spelling = integer_spelling
        elif not integer_spelling and standard_spelling:
            # Convert from standard to integer
            self.integer_spelling = music_data.convert_spelling(standard_spelling, 0)
            self.standard_spelling = standard_spelling
        elif name and name in music_data.chord_map:
            self.standard_spelling = music_data.chord_map[name][0]
            self.integer_spelling = music_data.chord_map[name][1]
        
        if not self.integer_spelling:
            raise ValueError("At least one of standard_spelling or integer_spelling must be provided")
        
        # print(music_data.chord_map_invert[])
        if not self.name and self.integer_spelling in music_data.chord_map_invert:
            self.name = music_data.chord_map_invert[self.integer_spelling][0]
        
    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_standard_spelling(self):
        return self.standard_spelling

    def set_standard_spelling(self, standard_spelling):
        self.standard_spelling = standard_spelling

    def get_integer_spelling(self):
        return self.integer_spelling

    def set_integer_spelling(self, integer_spelling):
        self.integer_spelling = integer_spelling

    def __repr__(self):
        return f"Chord(name='{self.name}', standard_spelling='{self.standard_spelling}', integer_spelling='{self.integer_spelling}')"

class ChordShape(Chord):
    empty_chord = [0, 0, 0, 0, 0, 0, 0]
    """
    Represents the shape of a chord on a guitar fretboard.

    Attributes:
        coords (list of int): Coordinates on the fretboard.
        root (int): The root note position.
        diagram (list): Visual representation of the chord shape.
        myStrings (list): String representation for the chord diagram.
        chord (Chord): Associated Chord object.

    Methods:
        __init__: Initializes a ChordShape instance.
        find_notes: Finds the absolute notes of the shape.
        find_spelling: Determines the spelling of the chord.
        coords_to_2D: Converts coordinates to a 2D matrix.
        match_chord: Matches the chord shape to a chord from the chord list.
        print_diagram: Prints the diagram of the chord shape.

    """

    def __init__(self, coords, note = None):
        """
        Initializes a ChordShape instance.

        Parameters:
            coords (list of int): Coordinates representing the chord shape on the fretboard.
        """
        if coords == self.empty_chord or coords == self.empty_chord[1:]:
            return
        
        self.is_valid = True
        self.fret = "O"
        self.r_fret = "0"

        coords = ChordShape.process_coords(coords, note)
        self.coords = coords[1:]
        self.root = coords[0]

        self.notes = None
        self.spelling = None
        self.chord = None
        self.coords_matrix = None
        self.find_notes()
        self.find_spelling()
        if self.is_valid == False:
            return
        self.coords_to_2D()
        self.diagram = Diagram(self.coords_matrix, self.root)


           #Find th  e chord in list of chords with same spelling as this shape, assign to chord

    def __repr__(self):
        return f"ChordShape(name='{self.chord.name}', standard_spelling='{self.chord.standard_spelling}', integer_spelling='{self.chord.integer_spelling}', root='{self.root}', coords='{self.coords}')" if self.coords is not None else "" 

    def getCoords(self):
        return self.coords

    def getName(self):
        return self.myName

    def setName(self, name):
        self.myName = name

    def getRoot(self):
        return self.root
    
    def process_coords(coords, note = None):
        """
        Returns correctly formatted guitar fret coordinates in the following format: 
        [root string # (1-6), String 1 fret # (1- ), String 2, 3, 4, 5, 6]
        0 represents an unplayed string. 

        This method takes a list of coordinates or a string or integer representation of coordinates,
        validates the input, and returns a list of coordinates with the root note added if not given.
        If a note (integer value between 0 and 11) is provided, the method finds the root based on the given note.

        Parameters:
        coords (list or str or int): The input coordinates.
        note (int, optional): The note to find the root based on. Defaults to None.

        Returns:
        list: The processed coordinates.
        """
        
        #Convert to list if not already
        if type(coords) is not list:
            if type(coords) is str and coords.isdigit():
                coords = [int(digit) for digit in coords]
            elif type(coords) is int:
                coords = [int(digit) for digit in str(coords)]
            else:
                return ChordShape.empty_chord
            
        #Check if valid input
        if(7 < len(coords) < 6 or (len(coords) == 7 and 6 < coords[0] < 1)):
            return ChordShape.empty_chord

        #Add 0 for root note if not given
        if len(coords) == 6:
            coords = [0] + coords

        #convert note (str) to int 
        if(note is not None and type(note) is str):
            note_values = music_data.note_values
            note = next((i for i, row in enumerate(note_values) if note in row), None)
        #find root note based on given note
        # or transpose the shape to the given note if both root and note are given
        if(note is not None and type(note) is int and 0 <= note < 12):
            if coords[0] != 0:  
                
                curr_root_note = (coords[coords[0]] + base_notes[coords[0] - 1] - 1) % 12
                # if note = 4 & curr_root_note = 9, dist = 7, so curr_root_note + dist % 12 = 4
                dist = (note - curr_root_note - 1) % 12
                for i in range(1, len(coords)):
                    if coords[i] != 0:
                        coords[i] += dist
            else: 
                for i in range(1, len(coords)):
                    if coords[i] != 0 and (coords[i] + base_notes[i - 1] - 1) % 12 == note:
                        coords[0] = i
                        break
                
            if coords[0] == 0:
                return ChordShape.empty_chord
        #if no root or note given, find the root based on the first non-zero coordinate TODO
        if coords[0] == 0:
            coords[0] = next((i for i, coord in enumerate(coords) if coord != 0), None)
        #standard input: 7 digits long list, 1st digit is root string, rest are fret numbers
        return coords

    def find_notes(self):
        #Find the absolute notes of the shape
        self.notes = [(base_note + coord - 1) % 12 if coord != 0 else None for base_note, coord in zip(base_notes, self.coords)]

    def find_spelling(self): #TODO
        spelling = set()
        if self.root == 0:
            self.spelling = spelling
            self.is_valid = False
            return
        
        root_note = self.notes[self.root - 1] % 12
        for note in self.notes:
            if note is not None:
                spelling.add((note - root_note) % 12)
        self.spelling = spelling
        self.match_chord()
    
    def coords_to_2D(self):
        min_fret = min(coord - 1 for coord in self.coords if coord != 0)
        max_fret = max(coord - 1 for coord in self.coords if coord != 0)
        self.coords_matrix = [[None for _ in range(6)] for _ in range(max_fret  + 2)] #- min_fret
        for i in range(len(self.coords)):
            if self.coords[i] != 0:  
                self.coords_matrix[self.coords[i] ][i] = self.notes[i] #- min_fret
                #self.coords[i] = self.coords[i] - min_fret
        
    def match_chord(self):
        if self.chord is None:
            for chord in all_chords:
                if set(chord.integer_spelling) == self.spelling:
                    self.chord = chord
                    return
            
        self.chord = Chord("None", music_data.convert_spelling(self.spelling, 1), self.spelling) #TODO how to name chord?

    def print_diagram(self, type = 0):
        self.diagram.print_diagram(type)

class Scale():
    """
    Represents a musical scale.

    Attributes:
        name (str): Name of the scale.
        integer_spelling (list of int): Integer representation of the scale.
        coords (list of lists): Coordinates of the scale on a fretboard.
        diagrams (list of Diagram): Diagrams representing the scale on a fretboard.
        notes (list): Notes in the scale.
        chords (list): Chords derived from the scale.

    Methods:
        __init__: Initializes a Scale instance.
        create_coords: Static method to create a list of 5 coordinate matrices for the 
            scale shapes on the fretboard.
        create_diagrams: Creates diagrams for the scale.
        print_diagram: Prints a specific diagram of the scale.
    """

    def __init__(self, name = None, integer_spelling = None):
        self.name = name
        self.integer_spelling = integer_spelling
        if not name and tuple(integer_spelling) in music_data.scale_map_invert:
            self.name = music_data.scale_map_invert[tuple(self.integer_spelling)]
        if not integer_spelling and name in music_data.scale_map:
            self.integer_spelling = list(music_data.scale_map[name.strip()])

        '''
        self.coords has been changed from a 3d array generated by create_coords to a
        2d array (create_coords2). Thus self.diagram instead of self.diagrams and 
        print_diagram instead of print_diagrams. 
        '''
        self.coords = self.diagram = None
        if(self.integer_spelling is not None):
            self.coords = Scale.create_coords2(self.integer_spelling)
            self.diagram = Diagram(self.coords)
        #self.diagrams = Scale.create_diagrams(self.integer_spelling)
        self.notes = []
        self.chords = []


    def __repr__(self):
        return f"Scale(name={self.name}, integer_spelling={self.integer_spelling})"
    
    @staticmethod
    def create_coords(integer_spelling):
        r_height = 1
        coords = [[[None for _ in range(6)] for _ in range(5)] for _ in range(5)]
        for root in range(5):
            root_note = (base_notes[root] + r_height) % 12
            print("root note" + str(root) + ": " + str(root_note))
            queue = deque(sorted([(n + root_note) % 12 for n in integer_spelling]))
            print("queue: ")
            pprint.pprint(queue)
            
            scale_note = None
            for string in range(6):
                first_fret = 0
                count = 0

                if string == 0: 
                    scale_note = Scale.find_first(scale_note, queue, root_note, root)

                print("String " + str(string) + " scale_note: " + str(scale_note))
                for fret in range(0, 5): 
                    fret_distance = fret - first_fret
                    fret_note = (base_notes[string] + fret) % 12
                    if fret_note == scale_note and fret_distance < 4:
                        if count == 0:
                            first_fret = fret
                        count += 1  

                        coords[root][fret][string] = (scale_note - root_note) % 12 #put the integer scale tone in the right place
                        queue.append(scale_note)
                        scale_note = queue.popleft()

        return coords
    
    @staticmethod
    def create_coords2(integer_spelling):
        num_frets = 16
        coords = [[None for _ in range(6)] for _ in range(num_frets)]
        base_notes2 = [note - 7 for note in base_notes]
        queue = deque(integer_spelling)
        curr_note = queue.popleft()
        for string in range(6):
            min_diff = min([(note - base_notes2[string]) % 12 for note in integer_spelling])
            while (curr_note - base_notes2[string]) % 12 != min_diff:
                queue.append(curr_note)
                curr_note = queue.popleft()
            for fret in range(num_frets):
                fret_note = (base_notes2[string] + fret) % 12
                if curr_note == fret_note:
                    coords[fret][string] = curr_note
                    queue.append(curr_note)
                    curr_note = queue.popleft()

        return coords


            

    def find_first(scale_note: int, queue: deque, root_note: int, root: int):
        first_note = root_note - 1 #root_height
        for i in range(root, -1):
            first_note = first_note - base_notes[i]
        first_note = first_note % 12

        print("first note: " + str(first_note))

        nearest_note = min([scale_note for scale_note in queue if scale_note >= first_note], default=None)
        print("nearest note: " + str(nearest_note))
        while scale_note != nearest_note:
            scale_note = queue.popleft()
            queue.append(scale_note)
        
        print("scale note: " + str(scale_note))
        return scale_note

    def create_diagrams(integer_spelling):
        coords = Scale.create_coords(integer_spelling)

        diagrams = []
        for i in range(0, len(coords)):
            diagrams.append(Diagram(coords[i]))
        
        return diagrams
    
    def print_diagram(self, type = 0):
        self.diagram.print_diagram(type)
        
    def print_diagrams(self, number = 0, type = 0):
        self.diagrams[number].print_diagram(type)

    def print_vertical(self, type = 0):
        for diagram in self.diagrams:
            diagram.print_diagram(type, True)
    
    def print_horizontal(self, type = 0):
        for i in range(5):
            print()

class Diagram: #TODO
    """
    Represents a diagram of a scale or chord shape on a guitar fretboard.

    Attributes:
        root (int): Root note position.
        coords (list of lists): Coordinates on the fretboard.
        num_frets (int): Number of frets in the diagram.
        diagram (list of lists): Visual representation of the diagram.
        ordered_notes (deque): Ordered notes in the diagram.

    Methods:
        __init__: Initializes a Diagram instance.
        find_ordered_notes: Finds the ordered notes in the diagram.
        print_diagram: Prints the diagram.
        convert_fret: Converts a fret number to a specific representation.
    """

    def __init__(self, coords, root = 0):
        self.fret_numbers = (0, 3, 5, 7, 9, 12, 15, 17, 19, 21, 24)
        self.root = root
        self.coords = coords
        self.ordered_notes = None
        self.root_note = None
        self.find_ordered_notes()

        self.min_fret = self.max_fret = self.max_width = None
        self.num_frets = len(coords)
        self.diagram = None
        self.set_diagram( 0 )


    def find_ordered_notes(self):
        notes = deque()
        for i in range(0, len(self.coords)):
            for j in range(0, len(self.coords[i])):
                if self.coords[i][j] is not None:
                    notes.append(self.coords[i][j])
                    if self.root != 0 and j + 1 == self.root:
                        self.root_note = self.coords[i][j]
        self.ordered_notes = notes
        
    def set_diagram(self, type = 0, top_fret = None):
        self.diagram = [["|" for _ in range(6)] for _ in range(self.num_frets + 2)]
        for i in range(0, len(self.coords[0])):
            column = [row[i] for row in self.coords]
            if all(coord is None for coord in column):
                self.diagram[0][i] = 'x'
        for i in range(len(self.coords)):
            for j in range(0, len(self.coords[i])):
                if self.coords[i][j] is not None:
                    self.diagram[i + 1][j] = self.convert_fret(self.coords[i][j], type)
                    if type == 0 and self.coords[i][j] == self.root_note:
                        self.diagram[i + 1][j] = '0'

        if top_fret is not None:
            self.diagram = self.diagram[1:]

        self.max_width = max(len(str(element)) for row in self.diagram for element in row)

        #determine min_frret
        for i in range(0, len(self.diagram[0])):
            column = [row[i] for row in self.diagram]
            for j in range(1, len(column)):
                if column[j] != "|" and column[j] is not None:
                    self.min_fret = min(j - 1, self.min_fret) if self.min_fret is not None else j - 1
                    break
        
        
        self.diagram = [self.diagram[0]] + self.diagram[self.min_fret + 1:]
        self.max_fret = self.min_fret + len(self.diagram) - 3

    def print_diagram(self, type = 0, top_fret = None):
        self.set_diagram(type, top_fret)
        fret_numbers = (0, 3, 5, 7, 9, 12, 15, 17, 19, 21, 24)

        for i in range(len(self.diagram) ):
            row = self.diagram[i]
            row_num = str(i + self.min_fret - 1) if i + self.min_fret - 1 in fret_numbers else ""
            print(" ".join(str(element).ljust(self.max_width) for element in row) + " " + row_num)

        #find the minimum j for which diagram[i][j] is not None and assign it to min_fret

    def convert_fret(self, note, type):
        note = (note - self.root_note) % 12
        if type == 1:
            return note
        if type == 2:
            return music_data.integer_to_tones[note]
        if any(type in row for row in music_data.note_values): #type in music_data.note_values
            index = next((i for i, row in enumerate(music_data.note_values) if type in row), None)            
            return music_data.note_values[(index + note) % 12][0]
        return 'O'


all_chords = []
for chord_name, chord_data in music_data.chord_map.items():
    chord = Chord(chord_name, chord_data[0], chord_data[1])
    all_chords.append(chord)

chord_shapes = []
for coords in music_data.chord_shapes:
    shape = ChordShape(coords)
    chord_shapes.append(shape)

