#include "q3tex2wad.hpp"

Config::Config(int size) {
    search = new string[size];
    replace = new string[size];
}

Config::~Config() {
    delete[] search;
    delete[] replace;
}