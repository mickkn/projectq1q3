#include "q3tex2wad.hpp"

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>

using namespace std;

int main(int argc, char *argv[]) {

    if(argc < 2 || argc > 3) {
        cout << "Usage: " << argv[0] << " configfile mapfile\n\n";
        return 0;
    }

    char texfixChar;
    bool texfix = false;
    cout << "\n[OPTIONAL] Fix the rotation bug from q3map2? (Y/N) [N]:";
    cin >> texfixChar;
    if(texfixChar == 'Y' || texfixChar == 'y') {
        texfix = true;
        cout << "\nROTATION BUGFIX [ENABLED]\n";
    } else {
        cout << "\nROTATION BUGFIX [DISABLED]\n\n";
    }

    string fileToParse = string(argv[2]);

    ifstream mapFile;                           // Declare input file stream
    ofstream outputMapFile;                     // Declare output file stream
    
    string fileToWrite = "fixed_"+fileToParse;  // New map filename

    mapFile.open(fileToParse);                  // Open map file
    outputMapFile.open(fileToWrite);            // Open new map file

    string line;                                // Line variable

    // Progress bar
    cout << "Running.";
    int progressCnt = 0;

    while(getline(mapFile, line)) {             // Get line in mapFile

        find_and_replace_from_config(string(argv[1]), &line);   // Replace the line with data from config file

        // Fix the rotation bug
        if(texfix == true) {
            find_and_replace(&line, " 0.5 0.5 ", " 0 0 ");
        }

        outputMapFile << line << '\n';              // Place new replace line in new file

        progressCnt++;
        if(progressCnt > 500) {
            cout << ".";
            progressCnt = 0;
        }

    }

    cout << "\n";

    outputMapFile.close();
    mapFile.close();

    return 0;
}