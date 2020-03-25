import os
import sys
try:
	import easygui
except ImportError:
	sys.exit("""You need easygui! run 'pip install easygui' """)

# Decompile with Q3MAP2
def decompile_bsp(file_name, decode_option):
	if decode_option != None:
		if 'QuakeLive Map' in decode_option:
			err1 = os.system('q3map2.exe -convert -game et -format map ' + '\"'+file_name+'\"')
			err2 = os.system('q3map2.exe -convert -game et -format quake3 '''+'\"'+file_name.replace('.map', '_converted.map')+'\"')
			if err1 != 0 or err2 != 0:
				return "error_q2map2"
		elif 'Quake3 Map' in decode_option:
			err = os.system('q3map2.exe -convert -format map ' + '\"'+file_name+'\"')
			if err != 0:
				return "error_q2map2"
	return 0


# Read config file
def read_config(file_name, original_name, new_name):
	with open(file_name) as open_file:
		for line in open_file:
			original_name.append(line.split(';')[0])	  			# Add directory
			new_name.append(line.split(';')[1].rstrip('\n'))		# Add code


# Fix the texture names
def replace_textures(map_name, find_lst, replace_lst, tex_options, founds_lst, replaced_lst):
	print("Fixing.....")
	with open(map_name, 'r') as input_file:
		converted_map_name = map_name.replace('.map', '_fixed.map')
		with open(converted_map_name, 'w') as output_file:
			for line in input_file:																		# Do something for each line
				for p in range(len(find_lst)):															# Check all finds until one match
					if find_lst[p].upper() in line:							  							# Check line for CAPPED find name
							line = line.replace(' '+find_lst[p].upper()+' ', ' '+replace_lst[p]+' ')	# Create a new line with replaced
							if find_lst[p].upper() not in founds_lst:									# Check for presence
								founds_lst.append(find_lst[p].upper())									# Save the found texture
								replaced_lst.append(replace_lst[p])										# Save the found texture replacement
					elif find_lst[p] in line:															# Check line for unCAPPED find name
							line = line.replace(' '+find_lst[p]+' ', ' '+replace_lst[p]+' ')			# Create a new line with replaced
							if find_lst[p] not in founds_lst:											# Check for presence
								founds_lst.append(find_lst[p])											# Save the found texture
								replaced_lst.append(replace_lst[p])										# Save the found texture replacement
				output_file.write(line)																	# Write to output file
	print("DONE!")
	input_file.close()
	output_file.close()

# Write replaced texture report
def write_tex_output(map_name, founds_lst, replaced_lst):
	log_file_name = map_name.replace('.map', '.csv')
	with open(log_file_name, 'w') as output_file:
		for i in range(len(founds_lst)):
			output_file.write(founds_lst[i] + ';' + replaced_lst[i] + '\n')
	output_file.close()
	return 0

# Create a folder with 24bit textures
def create_24bit_folder(map_name, founds_lst, replaced_lst):
	return 0

# Create a wad file with the used textures
def create_wad(map_name, replaced_lst, texture_folder):
	return 0

### Program variables

# Containers to keep data
find = []			# Find string list
replace = []		# Replace string list

# TEXT VARIABLES 
headerMsg = 'PROJECT Q1Q3 UTILITY TOOL - by Mick'	# MENU Name
choice = 'none'										# MENU Choice
confFile = 'q1q3utility.csv'							# Default CSV file
bspFile = 'none'									# Default BSP file
#mapFile = 'none'
mapFile = r'D:\[GAMES]\Quakeworld\#MapEditor\Quake\Maps\Q3TEX2WAD\q3dm6_converted.map'									# Default MAP file

rotationFixName = "Rotation fix"
rotationFix = 'no'
optionChoices = [rotationFixName]

decompileChoices = ['QuakeLive Map', 'Quake3 Map']
q3map2ErrMsg = "Error occurred: \n1. Did you chose a correct .bsp file? \n2. Are Q3MAP2 installed correctly? All *.dll's in folder?"
bspConvOkMsg = "BSP converted successfully!"
fixOkMsg = "SUCCESS, write some more info here !"

#Choices
c_find_bsp = "BSP"
c_decompile = "DEC"
c_find_map = "MAP"
c_fix_map = "FIX"
c_find_conf = "CFG"
c_options = "OPT"
c_exit = "EXIT"

# Containers for texture list output
founds = []		
replaced = []

### MENU
chosen_options = []

while choice != 'Exit':

	if os.path.sep in mapFile:
		mapFileDisplay = os.path.join('..', mapFile.rsplit(os.path.sep)[-3], mapFile.rsplit(os.path.sep)[-2], mapFile.rsplit(os.path.sep)[-1])
	else:
		mapFileDisplay = mapFile
	if os.path.sep in bspFile:
		bspFileDisplay = os.path.join('..', bspFile.rsplit(os.path.sep)[-3], bspFile.rsplit(os.path.sep)[-2], bspFile.rsplit(os.path.sep)[-1])
	else:
		bspFileDisplay = bspFile
	message = '%% MAKE SOME CHOICES! %%' + \
			  '\nBSP FILE: ' + bspFileDisplay + \
			  '\nCONFIG FILE (.csv): ' + confFile + \
			  '\nMAP FILE: ' + mapFileDisplay
	options = 'OPTIONS!\n' + 'Rotation fix: ' + rotationFix
	choice = easygui.buttonbox(message+'\n\n'+options, headerMsg,
							   (c_find_bsp, c_decompile, c_find_map, c_fix_map, c_find_conf, c_options, c_exit))

	if choice == c_decompile:
		decOpt = easygui.choicebox('Pick Map Type', headerMsg, decompileChoices)
		err = decompile_bsp(bspFile, decOpt)
		if err == "error_q2map2":
			easygui.msgbox(q3map2ErrMsg, 'ERROR')
		else:
			easygui.msgbox(bspConvOkMsg, 'Success')
		mapFile = bspFile.replace('.bsp', '_converted.map')
	elif choice == c_find_bsp:
		bspFile = easygui.fileopenbox()
		print(bspFile)
	elif choice == c_fix_map:
		if '.csv' not in confFile:
			easygui.msgbox("ERROR: Config file need to be a CSV file with semicolon separation")
			choice = 'none'
		else:
			read_config(confFile, find, replace)	# Read config file
			replace_textures(mapFile, find, replace, chosen_options, founds, replaced)	# Replace textures in map file
			write_tex_output(mapFile, founds, replaced)		# Write a log
			texFolder = create_24bit_folder(mapFile, founds, replaced)	# Fetch 24bit files in folder
			create_wad(mapFile, replaced, texFolder)			# Create a wad from replced textures
			easygui.msgbox(fixOkMsg, 'Success')
	elif choice == c_find_map:
		mapFile = easygui.fileopenbox()
		if mapFile == None:
			choice = 'none'
	elif choice == c_find_conf:
		confFile = easygui.fileopenbox()
		if confFile is None:
			choice = 'none'
	elif choice == c_options:
		chosen_options = easygui.multchoicebox('Pick options', headerMsg, optionChoices)
		if chosen_options == None:
			rotationFix = 'no'
		else:
			if rotationFixName in chosen_options:
				rotationFix = 'yes'
			else:
				rotationFix = 'no'
	else:
		sys.exit()

