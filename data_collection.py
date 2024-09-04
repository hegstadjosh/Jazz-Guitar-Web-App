import os
import pprint
import requests
from bs4 import BeautifulSoup
from music_objects import Chord, ChordShape, Scale
from urllib.parse import urljoin
import json
import music_data as md

'''
Archive of funcitons I made to collect and/or format data from different sources. The 
formatted data is now in the music_data.py file or jsons. 
'''

def create_chord_dictionary_from_file(file_path):
    chord_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            if ',' in line:  # Processing a line with chord data
                parts = line.strip().split(', ')
                if len(parts) == 3:
                    # Extracting the name and integer spelling
                    name = parts[0]
                    integer_spelling = set(map(int, parts[2].split()))
                    chord_dict[name] = integer_spelling
    return chord_dict

def create_chords_from_file(chord_spellings):
    with open(chord_spellings, 'r') as file:
        chord_data = file.readlines()
    
    chords = []
    for line in chord_data:
        if ',' not in line:  # This ensures we're processing a line with chord data
            chord_type = line.strip()
        else:
            parts = line.strip().split(', ')
            name = parts[0]
            standard_spelling = set(parts[1].split(' '))
            integer_spelling  = set(parts[2].split(' '))
            chord = Chord(chord_type, name, standard_spelling, integer_spelling)
            chords.append(chord)
            
    return chords

def process_scale_lines(lines):
    scale_dict = {}
    
    for line in lines:
        line = line[:23] + ';' + line[23:]  # Insert ';' at the 24th column
        parts = line.split(';')
        if len(parts) == 3:  # Adjust the condition to match the number of columns in your file
            scale_num, binary_notes, scale_name = parts  # Adjust the indices based on your file structure
            integer_spelling = decimal_to_scale_tones(scale_num.strip())
            scale_dict[scale_name.strip()] = integer_spelling
    return scale_dict   

def decimal_to_scale_tones(decimal_number):
    decimal_number = int(decimal_number)
    # Convert the decimal number to binary. The binary representation is right-aligned
    # and padded with zeros to ensure it always has 12 digits.
    binary_representation = format(decimal_number, '012b')

    # Calculate the scale tones. If a bit is '1', the corresponding note (index + 1) is included.
    scale_tones = [i + 1 for i, bit in enumerate(binary_representation) if bit == '1']

    return tuple(scale_tones)

@staticmethod
def scrape_chord_shapes(url):
    print("scraping url...\t", url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    with open('chord_shapes.txt', 'w') as file:
        # Find all links to text files
        count = 0
        for link in soup.find_all('a'):
                
                    href = link.get('href')
                    if href and href.endswith('.txt'):
                        txt_url = urljoin(url, href)  # Construct the full URL
                        filename = os.path.basename(txt_url)  # Get the filename
                        filename_without_ext = os.path.splitext(filename)[0]  # Remove the .txt extension
                        print(filename_without_ext + ":\n")

                        txt_response = requests.get(txt_url)
                        # if txt_response.status_code != 200:
                        #     print(f"Failed to get {txt_url}")
                        #     continue

                        # Process the text file content into ChordShape objects
                        file.write(filename_without_ext + ":\n")
                        process_chord_shapes(txt_response.text, file)
                        
                        count += 1

def process_chord_shapes(txt_content, file):
    lines = txt_content.split('\n')

    for line in lines:
        if line and all(s.isdigit() or s == 'x' for s in line.split()):
            coords = [0 if s == 'x' else int(s) + 1 for s in line.split()]
            curr = ChordShape(coords, 0)
            coords = [curr.root] + coords
            file.write(str(coords) + "\n")             

url = 'https://www.hakwright.co.uk/guitarchords/A_chords.html'

# file = 'C:\\Users\\socce\\Desktop\\Guitar Project (Python)\\old_chord_assignments.txt'
# with open(file, 'r') as file:
#     lines = file.readlines()
#     chords = []
#     for line in lines:
#         if '[' in line:
#             parts = line.split('[')
#             parts = parts[1].split(']')
#             parts = parts[0].split(',')
#             parts = [int(part.strip()) for part in parts]

#             print("ChordShape(", parts, "),\n")



def convert_chord_json():
    json_files = ['guitar.json', 'guitar-ly.json', 'guitar-legacy.json']
    new_file = 'guitar_data.json'
    new_data = []
    for json_file in json_files:
        
        with open(json_file, 'r', encoding='utf-8') as file:
            guitar_data = json.load(file)
            for chord in guitar_data['chords']:
                if 'base' in chord:
                    frets = chord['frets']
                    base = chord['base']
                    coords = [0, 0, 0, 0, 0, 0, 0]
                    coords[1:] = [fret + base for fret in frets]
                    new_data.append({'name': chord['name'], 'coords': coords})
                else:
                    new_data.append({'name': chord['name'], 'copy': chord['copy']})
        with open(new_file, 'w', encoding='utf-8') as out_file:
            out_file.write('{"chords": [\n')
            for item in new_data:
                out_file.write(json.dumps(item, ensure_ascii=False) + ",\n")
            out_file.write(']}')

def name_spelling_json():
    map = md.chord_map
    alternates = md.alternate_chord_names

    with open('chord_data.json', 'w', encoding='utf-8') as file:
        file.write('{"chords": [\n')
        for name, spelling in map.items():
            for alt in alternates:
                if alt == name:
                    names = [name] + list(alternates[alt])
                    file.write(json.dumps({'names': names, 'spelling': sorted(spelling[1])}, ensure_ascii=False) + ",\n")
        file.write(']}')

#add new spellings to names_spellings.json
# names_coords = './names_coords_parsed.json'
# with open(names_coords, 'r', encoding='utf-8') as file1:
#     with open('names_spellings.json', 'r', encoding='utf-8') as file2:
#         data1 = json.load(file1)
#         data2 = json.load(file2)
#         i = 0 
#         for item in data1['chords']:
#             spellings = [chord['spelling'] for chord in data2['chords']]
#             if item['names'][0] == 'NC':
#                 continue
#             root_note = md.parse_chord_note(item['names'][0])
#             print(root_note, item['coords'])
#             shape = ChordShape( item['coords'], root_note)
#             curr_spelling = sorted(list(shape.chord.integer_spelling)) if shape.chord else None

#             if curr_spelling not in spellings:
#                 data2['chords'].append({'names': item['names'], 'spelling': curr_spelling})

#             i += 1
#             print(i)
#         with open('names_spellings2.json', 'w', encoding='utf-8') as out_file:
#             out_file.write('{"chords": [\n')
#             for item in data2:
#                 out_file.write(json.dumps(item, ensure_ascii=False) + ",\n")
#             out_file.write(']}')

def parse_specific_shapes(shape_file, spelling_file, new_shape_file): 
    specific_shapes = {}
    spellings = {}
    with open(shape_file, 'r', encoding='utf-8') as shape_f:
        specific_shapes = json.load(shape_f)
    with open(spelling_file, 'r', encoding='utf-8') as spell_f:
        spellings = json.load(spell_f)
        
                #each shape has a root note coord (1-6) & a 6-digit coords list 
        generic_shapes = {'shapes': []}
        i = 1 
        for shape in specific_shapes['chords']:
            root_note = md.get_note_from_chord(shape['names'][0])
            coords = shape['coords']

            shape_obj = ChordShape(coords, root_note)
            if(shape_obj.is_valid == False):
                continue

            generic_names = []
            for name in shape['names']:
                generic_names.append( md.get_generic_chord_name(name))
            
               
            coords7 = [shape_obj.root] + shape_obj.coords
            generic_shapes['shapes'].append({'names': generic_names, 'coords': coords7})

            print(str(i) + ": " + generic_names[0], shape_obj.chord.name, shape_obj.spelling, shape_obj.root)
            
            #check if current chord's spelling is already in spellings json 
            found = False
            for entry in spellings['chords']:
                spelling = entry['spelling']
                
                if set(spelling) == shape_obj.spelling:
                    found = True
                    break
            
            spellings['chords'].append({'names': generic_names, 'spelling': sorted(list(shape_obj.spelling))})

            if(i < 0 ): 
                break 
        
        # for entry in generic_shapes['shapes']:
        #     names1 = entry['names']
        #     for entry2 in generic_shapes['shapes']:
        #         names2 = entry2['names']
                    
        
        with open(spelling_file.replace(".json", "2.json"), 'w', encoding='utf-8') as out_file:
            out_file.write("{\"chords\": [" + "\n")
            for entry in spellings['chords']:
                out_file.write(json.dumps(entry, ensure_ascii=False) + ",\n")
            out_file.write("]}" + "\n")

        with open(new_shape_file, 'w', encoding='utf-8') as out_file:
            out_file.write("{\"shapes\": [" + "\n")
            for entry in generic_shapes['shapes']:
                out_file.write(json.dumps(entry, ensure_ascii=False) + ",\n")
            out_file.write("]}" + "\n")


names_coords = './names_coords_parsed.json'
names_spelling = './names_spellings.json'



# with open('generic_shapes3.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)
#     shapes = data['shapes']
#     shapes2 = []
#     for shape in shapes:
#         coords = shape['coords']
#         coords = md.reduced_coords(coords)
#         if len(shapes2) > 0 and coords not in [shape['coords'] for shape in shapes2]:
#             shapes2.append({'names': shape['names'], 'coords': coords})
#         else :
#             shapes2.append({'names': shape['names'], 'coords': coords})
    
#     with open('generic_shapes4.json', 'w', encoding='utf-8') as out_file:
#         out_file.write("{\"shapes\": [" + "\n")
#         for entry in shapes2:
#             out_file.write(json.dumps(entry, ensure_ascii=False) + ",\n")
#         out_file.write("]}" + "\n")
#     #each shape has 'names' and 'coords' keys
    