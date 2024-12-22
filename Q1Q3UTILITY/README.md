# Readme

1. Install Python 3.x (only tested with this)

2. Extract all texture folders from your .pk3 files into one texture folder in the Q1Q3UTILITY folder
	
	Should look something like this, keeping the sub folder structure
	
	..\Q1Q3UTILITY\textures\base_door
	
	..\Q1Q3UTILITY\textures\gothic_block
	
3. Install requirements for your python distro

	```bash
	pip install -r requirements.txt
	```

4. Open a commando prompt and start the application with:'

	```bash
	python q1q3utility.py -h
	```
Follow the CLI guidelines, and you should be good to go.

## Troubleshooting

If you have any issues, please open an issue on the GitHub page.

The script will create a .csv file with missing textures, this list can be used to add to the q1q3tex2wad.csv for 
running the script again. This is mostly for custom maps with new textures. Remember to extract the textures from 
your custom map (.pk3 file) to the texture folder in the Q1Q3UTILITY folder.

