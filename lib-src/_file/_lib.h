#pragma once

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cstring>
#include <numeric>

using namespace std;

struct Soft_Array
{
    int len;
    char stub; // placehold
    char str[1];
};

void split_string(const string &s, const char *delimiter, vector<string> &v);
void split_string(const string &s, const char *delimiter, vector<int> &v);
void split_string(const string &s, const char *delimiter, vector<double> &v);