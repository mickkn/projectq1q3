#include "q3tex2wad.hpp"

using namespace std;

void find_and_replace(string* line, const string search, const string replace) {

    string tempLine = *line;

    while(true) {
        size_t subStringPos = tempLine.find(search);    // Find first word in line
        if(subStringPos != string::npos) {              // If word is found
            tempLine.replace(subStringPos, search.size(), replace); // Replace in line string
        } else {
            break;  // Exit while loop
        }
    }

    *line = tempLine;

}

void find_and_replace_from_config(string config_file, string* input_line) {

    ifstream configFile;
    configFile.open(config_file);

    // Copy string to temp string
    string tempLine = *input_line;

    // Declare some variables
    string configLine, search, replace;
    int lineCounter = 0;

    // Do the cha cha cha
    while(!configFile.eof()) {
    
        lineCounter++;
        getline(configFile, configLine);                // Read config file line
        istringstream iss_semi(configLine);             // Parse line to iss
        getline(iss_semi, search, ';');                 // Get first cell (search string in csv with semicolon)
        if(iss_semi.eof()) {                            // No semicolon found
            istringstream iss_comma(configLine);        // Parse line to iss
            getline(iss_comma, search, ',');            // Get first cell (search string in csv with comma)
            if(iss_comma.eof()) {                       // No comma found
                cout << "*********************\n";
                cout << "Error in config file (" << config_file << ") - line: " << lineCounter << "\n";
                cout << "Missing comma or semicolon separation\n";
                cout << "*********************\n";
                break;                                  // Break out of while loop
            } else {
                iss_comma >> replace;                   // Get second cell (replace string)
            }
        } else {
            iss_semi >> replace;                        // Get second cell (replace string)
        }

        find_and_replace(&tempLine, search, replace);   // Replace the words in the line
    }
    
    // Place new replaced string in line
    *input_line = tempLine;

    // Close file before exit
    configFile.close();
}