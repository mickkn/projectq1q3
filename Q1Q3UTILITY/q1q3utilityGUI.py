import os
import sys
import shutil
from PIL import Image
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
	print("READING CONFIG FILE...")
	with open(file_name) as open_file:
		for line in open_file:
			original_name.append(line.split(';')[0])	  			# Add directory
			new_name.append(line.split(';')[1].rstrip('\n'))		# Add code


# Fix the texture names
def replace_textures(map_name, find_lst, replace_lst, tex_options, founds_lst, replaced_lst):
	print("REPLACING TEXTURES IN MAP FILE...")
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
	input_file.close()
	output_file.close()
	print("TEXTURES REPLACED IN MAP FILE!")

# Write replaced texture report
def write_tex_output(map_name, founds_lst, replaced_lst):
	print("WRITING TEXTURE LOG")
	log_file_name = map_name.replace('.map', '.csv')
	with open(log_file_name, 'w') as output_file:
		for i in range(len(founds_lst)):
			output_file.write(founds_lst[i] + ';' + replaced_lst[i] + '\n')
	output_file.close()
	return 0

# Create a folder with 24bit textures
def create_24bit_folder(map_name, files_to_find, replace_names, texture_dir):
	print("COPYING TEXTURES TO FOLDER...")
	# New texture folder to save some stuff in
	texFolder = map_name.rsplit('.')[0]
	
	# Create a folder if it doesn't exist
	if not os.path.exists(texFolder):
		os.mkdir(texFolder)
	else:
		shutil.rmtree(texFolder, ignore_errors=True)
		os.mkdir(texFolder)

	# Copy files to folder from texture directory
	for root, dirs, files in os.walk(texture_dir):		# Start in texture folder
		for file in files:								# Every file in texture folder
			_file = root.rsplit(os.path.sep)[-1] + '/' + file.rsplit('.')[0] # File path to check vs founds
			if _file in files_to_find:	# If file match file to find
				index = files_to_find.index(_file)				# Get found index in list
				fileext = '.' + file.rsplit('.')[-1].upper()	# Get file extension
				shutil.copy(os.path.join(root, file), \
							os.path.join(texFolder, replace_names[index] + fileext)) # Copy and rename file	
	
	return texFolder

# Resize with ration
def resize_image(image_file, new_max):
	return 0

# Create a wad file with the used textures
def create_wad(map_name, texture_folder):
	print("CREATING WAD FILE...")
	wadFileName = map_name.rsplit(os.path.sep)[-1].rsplit('.')[0] + '.wad'

	# Create a WAD folder 
	if not os.path.exists(os.path.join(texture_folder, 'wad')):
		os.mkdir(os.path.join(texture_folder, 'wad'))
	else:
		shutil.rmtree(os.path.join(texture_folder, 'wad'), ignore_errors=True)
		os.mkdir(os.path.join(texture_folder, 'wad'))

	err_lst = []

	for root, dirs, files in os.walk(texture_folder):		# Start in texture folder
		if 'wad' not in root:		# Don't look in wad folder
			for _file in files:
				
				# Convert to BMP
				fileext = '.' + _file.rsplit('.')[-1]
				#print(os.path.join(root, _file.replace(fileext, '.BMP')))
				srcFile = os.path.join(root, _file)
				bmpFile = os.path.join(os.path.join(root, 'wad'), _file.replace(fileext, '.BMP'))
				Image.open(srcFile).save(bmpFile)
				
				# Pallette conversion
				pal = Image.open('qpalette.png')
				img = Image.open(bmpFile)
				converted = img.convert("P", palette=pal)
				converted.save(bmpFile)
				
				err = os.system("python wad.py -q " + wadFileName + " " + os.path.join(root, _file))
				if err != 0:
					err_lst.append(_file)

	return err_lst

### Program variables

# Containers to keep data
find = []			# Find string list
replace = []		# Replace string list

# TEXT VARIABLES 
headerMsg = 'PROJECT Q1Q3 UTILITY TOOL - by Mick 2020'	# MENU Name
choice = 'none'											# MENU Choice
confFile = 'q1q3tex2wad.csv'							# Default CSV file
bspFile = 'none'										# Default BSP file
#mapFile = 'none'										# Default MAP file
mapFile = r'D:\[GAMES]\Quakeworld\#MapEditor\Quake\Maps\Q1Q3UTILITY\test_map.map'									
texDir = os.path.join(os.path.abspath(__file__).rsplit(os.path.sep,1)[0], '24bit', 'textures')

rotationFixName = "ROTATION BUGFIX"
rotationFix     = 'yes'
createWadName   = "CREATE WAD"
createWad       = 'yes'
create24BitName = "CREATE 24BIT DIR"
create24Bit     = 'yes'
optionChoices   = [rotationFixName, createWadName, create24BitName]

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
c_find_tex_dir = "TEX"
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
	if os.path.sep in texDir:
		texDirDisplay = os.path.join('..', texDir.rsplit(os.path.sep)[-3], texDir.rsplit(os.path.sep)[-2], texDir.rsplit(os.path.sep)[-1])
	else:
		texDirDisplay = texDir
	
	message = '%% MAKE SOME CHOICES! %%' + \
			  '\nBSP FILE    : ' + bspFileDisplay + \
			  '\nCONFIG FILE : ' + confFile + \
			  '\nMAP FILE    : ' + mapFileDisplay + \
			  '\nTEX FOLDER  : ' + texDirDisplay
	options = 'OPTIONS!\n' + \
				rotationFixName + '\t\t: '   + rotationFix + '\n' + \
				createWadName   + '\t\t : '  + createWad   + '\n' + \
				create24BitName + '\t: '     + create24Bit
			  
	choice = easygui.buttonbox(message+'\n\n'+options, headerMsg,
							   (c_find_bsp, c_decompile, c_find_map, c_fix_map, c_find_conf, c_find_tex_dir, c_options, c_exit))

	if choice == c_decompile:
		decOpt = easygui.choicebox('Pick Map Type', headerMsg, decompileChoices)
		err = decompile_bsp(bspFile, decOpt)
		if err == "error_q2map2":
			easygui.msgbox(q3map2ErrMsg, 'ERROR')
		else:
			easygui.msgbox(bspConvOkMsg, 'SUCCESS')
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
			texFolder = create_24bit_folder(mapFile, founds, replaced, texDir)	# Fetch 24bit files in folder
			err = create_wad(mapFile, texFolder)			# Create a wad from replced textures
			if len(err) != 0:
				print(err)
				errFiles = ""
				for name in err:
					errFiles = errFiles + name + '\n'
				errMsg = "Failed to complete wad file\n" + \
						 errFiles + \
						 '\nCould be size is not dividable by 8'
				easygui.msgbox(errMsg, 'NOT SUCCEEDED')
			else:
				easygui.msgbox(fixOkMsg, 'SUCCESS')
			print('\n')
	elif choice == c_find_map:
		mapFile = easygui.fileopenbox()
		if mapFile == None:
			choice = 'none'
	elif choice == c_find_conf:
		confFile = easygui.fileopenbox()
		if confFile is None:
			choice = 'none'
	elif choice == c_find_tex_dir:
		texFolder = easygui.diropenbox()
		print(texFolder)
		if texFolder is None:
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

