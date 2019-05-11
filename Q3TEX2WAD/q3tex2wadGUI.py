import os
import sys
try:
    import easygui
except ImportError:
    sys.exit("""You need easygui! run 'pip install easygui' """)


top_message = 'Project Q1Q3 - Texture Fix by Mick'
choice = 'none'
config_file = 'q3tex2wad.csv'
bsp_file = 'q3dm6.bsp'
map_file = 'elder_converted.map'

rotation_fix_name = "Rotation fix"
rotation_fix = 'no'
caps_originals_name = "CAPS originals"
caps_originals = 'no'
option_choices = [rotation_fix_name, caps_originals_name]

decompile_choices = ['QuakeLive Map', 'Quake3 Map']

find = []
replace = []


# Decompile with Q3MAP2
def decompile_bsp(file_name):
    d_choice = easygui.choicebox('Pick Map Type', top_message, decompile_choices)
    if 'QuakeLive Map' in d_choice:
        os.system('q3map2.exe -convert -game et -format map ' + file_name)
        os.system('q3map2.exe -convert -game et -format quake3 ' + file_name.replace('.map', '_converted.map'))
    elif 'Quake3 Map' in d_choice:
        os.system('q3map2.exe -convert -format map ' + file_name)


# Read config file
def read_config(file_name, original_name, new_name):
    with open(file_name) as open_file:
        for line in open_file:
            original_name.append(line.split(';')[0])      			# Add directory
            new_name.append(line.split(';')[1].rstrip('\n'))    	# Add code


def replace_textures(map_name, find_lst, replace_lst, tex_options):
    print("Fixing.....")
    with open(map_name, 'r') as input_file:
        converted_map_name = map_name.replace('.map', '_fixed.map')
        with open(converted_map_name, 'w') as output_file:
            for line in input_file:                                                  # Do something for each line
                for p in range(len(find_lst)):                                       # Check all finds until one match
                    if caps_originals_name in tex_options:
                        if find_lst[p].upper() in line:                              # Check line for find name
                            line = line.replace(find_lst[p].upper(), replace_lst[p])
                    else:
                        if find_lst[p] in line:
                            line = line.replace(find_lst[p], replace_lst[p])         # Create a new line with replaced
                output_file.write(line)                                              # Write to output file
    print("DONE!")
    input_file.close()
    output_file.close()


# MENU
chosen_options = []

read_config(config_file, find, replace)

while choice != 'Exit':

    message = 'Choose!' + \
              '\nBSP file: ' + bsp_file + \
              '\nConfig file (.csv): ' + config_file + \
              '\nMap file: ' + map_file
    options = 'Options!\n' + 'Rotation fix: ' + rotation_fix + '\nCAPS originals: ' + caps_originals
    choice = easygui.buttonbox(message+'\n\n'+options, top_message,
                               ('Decompile', 'BSP File', 'Fix', 'Map File', 'Config File', 'Options', 'Exit'))


    if choice is 'Decompile':
        print(bsp_file)
        decompile_bsp(bsp_file)
        map_file = bsp_file.replace('.bsp', '_converted.map')
    elif choice == 'BSP File':
        bsp_file = easygui.fileopenbox()
    elif choice == 'Fix':
        if '.csv' not in config_file:
            easygui.msgbox("ERROR: Config file need to be a CSV file with semicolon separation")
            choice = 'none'
        else:
            replace_textures(map_file, find, replace, chosen_options)
    elif choice == 'Map File':
        map_file = easygui.fileopenbox()
        if map_file is None:
            choice = 'none'
    elif choice == 'Config File':
        config_file = easygui.fileopenbox()
        if config_file is None:
            choice = 'none'
        else:
            read_config(config_file, find, replace)
    elif choice == 'Options':
        chosen_options = easygui.multchoicebox('Pick options', top_message, option_choices)
        if chosen_options is None:
            caps_originals = 'no'
            rotation_fix = 'no'
        else:
            if caps_originals_name in chosen_options:
                caps_originals = 'yes'
            else:
                caps_originals = 'no'

            if rotation_fix_name in chosen_options:
                rotation_fix = 'yes'
            else:
                rotation_fix = 'no'
    else:
        sys.exit()

