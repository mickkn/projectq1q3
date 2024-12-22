import os
import platform
import sys
import shutil
import math
from PIL import Image
try:
	import easygui
except ImportError:
	sys.exit("""You need easygui! run 'pip install easygui' """)

Q3Map = 'QUAKE3 MAP'
QLMap = 'QUAKELIVE MAP'

# Decompile with Q3MAP2
def decompile_bsp(file_name, decode_option):
	if decode_option != None:
	
		if platform.system() == 'Windows':
			q3map2Exe = os.path.join(os.path.abspath(__file__).rsplit(os.path.sep,1)[0], 'q3map2.exe')
		elif platform.system() == 'Linux':
			q3map2Exe = os.path.join(os.path.abspath(__file__).rsplit(os.path.sep,1)[0], 'q3map2.x86')
		else:
			return "error_platform"
	
		if QLMap in decode_option:
			err1 = os.system(q3map2Exe + ' -convert -game et -format map ' + '\"'+file_name+'\"')
			err2 = os.system(q3map2Exe + ' -convert -game et -format quake3 '''+'\"'+file_name.replace('.map', '_converted.map')+'\"')
			if err1 != 0 or err2 != 0:
				return "error_q2map2"
		elif Q3Map in decode_option:
			err = os.system(q3map2Exe + ' -convert -format map ' + '\"'+file_name+'\"')
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

# Resize with ration
def resize_to_power_of_two(image_file, max_size):
	
	save = 0
	image = Image.open(image_file)
	width, height = image.size
	#print("Old size: " + str(width) + 'x' + str(height))

	hpot = math.log(height, 2)						# Get log_2(height)
	wpot = math.log(width, 2)						# Get log_2(width)

	# Check for odd sizes (fit to power of 2)
	if (wpot % 1) != 0:								# Check for power of two
		save = 1									# Save file
		if round(wpot) == 0:						# Resize with 8 as minimum
			width = 8								# New width
		else:
			width = pow(2,round(wpot))				# New width
			
	if (hpot % 1) != 0:								# Check for power of eight
		save = 1									# Save file
		if round(hpot) == 0:						# Resize with 8 as minimum
			height = 8								# New height
		else:
			height = pow(2,round(hpot))				# New height

	# Check for size above 256 px
	if width > max_size:
		ratio = (max_size/float(width))					# Create ratio from width towards 256 px
		height = int((float(height)*float(ratio)))	# Apply ratio to height
		width = max_size									# New width
		save = 1									# Save file	

	if height > max_size:
		ratio = (max_size/float(height))					# Create ratio from height towards 256 px
		width = int((float(width)*float(ratio)))	# Apply ratio to width
		height = max_size								# New height
		save = 1									# Save file	
			
	if save != 0:
		#print("New size: " + str(width) + 'x' + str(height))
		image = image.resize((width, height), Image.Resampling.LANCZOS)	# Resize accordingly
		image.save(image_file)									# Save file

# Create a folder with 24bit textures
def create_24bit_folder(map_name, files_to_find, replace_names, texture_dir):
	print("COPYING TEXTURES TO FOLDER...")
	
	if not os.path.exists(texture_dir):
		print(texture_dir + ": NOT FOUND")
		return -1
	
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
				srcFile = os.path.join(root, file)				# Source file
				distFile = os.path.join(texFolder, replace_names[index] + fileext) # Renamed distination
				shutil.copy(srcFile, distFile) 					# Copy
				resize_to_power_of_two(distFile, 256)			# Check for size and resize if needed
	
	return texFolder

# Create a wad file with the used textures
def create_wad(map_name, texture_folder):
	print("CREATING WAD FILE...")
	wadFileName = map_name.rsplit(os.path.sep)[-1].rsplit('.')[0] + '.wad'
	wadTexFolder = os.path.join(texture_folder, 'wad')

	# Create a WAD folder 
	if not os.path.exists(wadTexFolder):
		os.mkdir(wadTexFolder)
	else:
		shutil.rmtree(wadTexFolder, ignore_errors=True)
		os.mkdir(wadTexFolder)

	if os.path.exists(wadFileName):	# Delete before making new
		shutil.rm(wadFileName)

	err_lst = []

	for root, dirs, files in os.walk(texture_folder):		# Start in texture folder
		if 'wad' not in root:								# Don't look in wad folder
			for _file in files:
				
				# Convert to BMP
				fileext = '.' + _file.rsplit('.')[-1]	# File extension
				srcFile = os.path.join(root, _file)		# Source file path
				bmpFile = os.path.join(os.path.join(root, 'wad'), _file.replace(fileext, '.BMP')) # Distination file path
				Image.open(srcFile).save(bmpFile)		# Copy as BMP file
				resize_to_power_of_two(bmpFile, 128)	# Resize BMP
				
				# Pallette conversion
				pal = Image.open('qpalette.png')
				img = Image.open(bmpFile)
				converted = img.convert("P", palette=pal)
				converted.save(bmpFile)
				
				# Make the new wad file
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
confFile = os.path.join(os.path.abspath(__file__).rsplit(os.path.sep,1)[0], 'q1q3tex2wad.csv')		# Default CSV file
bspFile = 'none'										# Default BSP file
mapFile = 'none'										# Default MAP file								
texDir = os.path.join(os.path.abspath(__file__).rsplit(os.path.sep,1)[0], 'textures')

decompileChoices = [QLMap, Q3Map]
q3map2ErrMsg = "Error occurred: \n1. Did you chose a correct .bsp file? \n2. Are Q3MAP2 installed correctly? All *.dll's in folder?"
platformErr = "Your platform is not supported"
bspConvOkMsg = "BSP converted successfully!"
fixOkMsg = "SUCCESS, write some more info here !"
helpMsg = "\n\n%% MANUAL %%" + \
		  "\nBSP - Choose BSP file" + \
		  "\nDEC - Decompile chosen BSP" + \
		  "\nMAP - Chose MAP file (if not decompiling)" + \
		  "\nFIX - Fixing MAP and create WAD file and 24BIT folder from texture folder" + \
		  "\nCFG - Choose a different config file" + \
		  "\nTEX - Choose a different texture folder"

#Choices
c_find_bsp 		= "BSP"
c_decompile 	= "DEC"
c_find_map 		= "MAP"
c_fix_map 		= "FIX"
c_find_conf 	= "CFG"
c_find_tex_dir 	= "TEX"
c_options 		= "OPT"
c_exit 			= "EXIT"

# Containers for texture list output
founds = []		
replaced = []

### MENU
chosen_options = []

while choice != 'Exit':

	if os.path.sep in bspFile:
		bspFileDisplay = os.path.join('..', bspFile.rsplit(os.path.sep)[-3], bspFile.rsplit(os.path.sep)[-2], bspFile.rsplit(os.path.sep)[-1])
	else:
		bspFileDisplay = bspFile

	if os.path.sep in confFile:
		confFileDisplay = os.path.join('..', confFile.rsplit(os.path.sep)[-3], confFile.rsplit(os.path.sep)[-2], confFile.rsplit(os.path.sep)[-1])
	else:
		confFileDisplay = confFile

	if os.path.sep in mapFile:
		mapFileDisplay = os.path.join('..', mapFile.rsplit(os.path.sep)[-3], mapFile.rsplit(os.path.sep)[-2], mapFile.rsplit(os.path.sep)[-1])
	else:
		mapFileDisplay = mapFile

	if os.path.sep in texDir:
		texDirDisplay = os.path.join('..', texDir.rsplit(os.path.sep)[-3], texDir.rsplit(os.path.sep)[-2], texDir.rsplit(os.path.sep)[-1])
	else:
		texDirDisplay = texDir
	
	message = '%% MAKE SOME CHOICES! %%' + \
			  '\nBSP FILE    : ' + bspFileDisplay + \
			  '\nCFG FILE    : ' + confFileDisplay + \
			  '\nMAP FILE    : ' + mapFileDisplay + \
			  '\nTEX FOLDER  : ' + texDirDisplay
			  
	choice = easygui.buttonbox(message + helpMsg, headerMsg,
							   (c_find_bsp, c_decompile, c_find_map, c_fix_map, c_find_conf, c_find_tex_dir, c_exit))

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
			if texFolder != -1:
				err = create_wad(mapFile, texFolder)			# Create a wad from replced textures
				if len(err) != 0:
					print(err)
					errFiles = ""
					for name in err:
						errFiles = errFiles + '['+name+']' + '\n'
					errMsg = "FAILED TO COMPLETE WAD FILE\n" + \
							 "AFFECTED FILES:\n" + \
							 errFiles
					easygui.msgbox(errMsg, 'NOT SUCCEEDED')
				else:
					easygui.msgbox(fixOkMsg, 'SUCCESS')
			else:
				errMsg = texDir + "\n\n NOT FOUND"
				easygui.msgbox(errMsg, 'NOT SUCCEEDED')
				
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
	else:
		sys.exit()

