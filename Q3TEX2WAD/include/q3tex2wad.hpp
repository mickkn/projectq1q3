#include <iostream>
#include <fstream>
#include <sstream>
#include <string>

using namespace std;

class Config {
    private:
    public:
        string * search;
        string * replace;
        Config();
        Config(int size);
        ~Config();
};