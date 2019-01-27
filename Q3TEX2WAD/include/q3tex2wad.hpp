#include <iostream>
#include <fstream>
#include <sstream>

using namespace std;

void find_and_replace(string* line, const string search, const string replace);

void find_and_replace_from_config(string config_file, string* input_line);