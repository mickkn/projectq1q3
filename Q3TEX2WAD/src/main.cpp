#include "q3tex2wad.hpp"

int main(int argc, char *argv[]) {

    if(argc < 2 || argc > 3) {
        cout << "Usage: " << argv[0] << " configfile mapfile\n\n";
        return 0;
    }

    int progressCnt = 0;                        // Progress bar counter

    string fileToParse = string(argv[2]);       // Get map filename

    ifstream mapFile;                           // Declare input file stream for map
    ifstream configFile;                        // Declare input file stream for config
    ofstream outputMapFile;                     // Declare output file stream for map
    
    string fileToWrite = "fixed_"+fileToParse;  // New map filename

    mapFile.open(fileToParse);                  // Open map file
    configFile.open(string(argv[1]));            // Open config file
    outputMapFile.open(fileToWrite);            // Open new map file

    string line;                                // Line variable

    int configSize = 0;
    while(getline(configFile, line)) {          // Count lines in config file
        configSize++;
    }

    configFile.clear();
    configFile.seekg (0, ios::beg);             // Restart from start of config file
  
    Config Config(configSize);                  // Allocate some memory for the config file

    configSize = 0;                             // Reset counter

    while(getline(configFile, line)) {          // Count lines in config file

        istringstream iss_semi(line);                           // Parse line to iss
        getline(iss_semi, Config.search[configSize], ';');      // Get first cell (search string in csv with semicolon)
        if(iss_semi.eof()) {                                    // No semicolon found
            istringstream iss_comma(line);                      // Parse line to iss
            getline(iss_comma, Config.search[configSize], ','); // Get first cell (search string in csv with comma)
            if(iss_comma.eof()) {                               // No comma found
                cout << "*********************\n";
                cout << "Error in config file (" << string(argv[1]) << ") - line: " << configSize << "\n";
                cout << "Missing comma or semicolon separation\n";
                cout << "*********************\n";
                break;                                          // Break out of while loop
            } else {
                iss_comma >> Config.replace[configSize];        // Get second cell (replace string)
                Config.replace[configSize] = (" "+Config.replace[configSize]+" ");  // Use a space in front and back
            }
        } else {
            iss_semi >> Config.replace[configSize];             // Get second cell (replace string)
            Config.replace[configSize] = (" "+Config.replace[configSize]+" ");      // Use a space in front and back
        }

        Config.search[configSize] = (" "+Config.search[configSize]+" ");            // Use a space in front and back

        configSize++;   // Count the line count up
    }

    int mapSize = 0;                        // Initialize map size
    while(getline(mapFile, line)) {         // Count lines in config file
        mapSize++;                          // Increment mapSize
    }

    string * map = new string[mapSize];     // Allocate some memory for the map file

    mapSize = 0;                            // Reset map size counter
    mapFile.clear();                        // Restart from start of map file
    mapFile.seekg (0, ios::beg);            // Restart from start of map file

    while(getline(mapFile, line)) {         // Count lines in config file
        map[mapSize] = line;                // Obtain map file in RAM
        mapSize++;                          // Count lines read
    }

    // do the replacing
    progressCnt = 0;                        // Reset progress counter
    size_t subStringPos;                    // Initialize variable
    cout << "Replace from config.";         // Progress counter prefix
    for(int mapPos = 0 ; mapPos < mapSize ; mapPos++) {

        for(int conPos = 0 ; conPos < configSize ; conPos++) {
            subStringPos = map[mapPos].find(Config.search[conPos]);             // Find first word in line (with additional spaces)
            if(subStringPos != string::npos) {                                  // If word is found
                map[mapPos].replace(subStringPos, Config.search[conPos].size(), Config.replace[conPos]); // Replace in line string
            }
        }

        // Progress counter
        if(progressCnt > 800) {
            cout << ".";
            progressCnt = 0;
        }

        progressCnt++;
    }

    progressCnt = 0;                        // Reset progress counter
    cout << "\nWriting to file.";           // Progress counter prefix
    for(int i = 0 ; i < mapSize ; i++) {
        outputMapFile << map[i] << '\n';    // Write new replaced line in new file

        // Progress counter
        if(progressCnt > 800) {
            cout << ".";
            progressCnt = 0;
        }

        progressCnt++;
    }

    outputMapFile.close();  // Close output map file
    configFile.close();     // Close config file
    mapFile.close();        // Close map file

    delete[] map;           // Delete map memory

    return 0;
}