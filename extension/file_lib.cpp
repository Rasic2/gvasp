#include "file_lib.h"

void split_string(const string &s, const char *delimiter, vector<string> &v)
{
    char *ptr;
    size_t len = s.size();
    Soft_Array *p = (Soft_Array *)malloc(sizeof(Soft_Array) + sizeof(char) * len);

    strcpy(p->str, s.c_str()); // c_str(): transform string to char
    ptr = strtok(p->str, delimiter);
    while (ptr != NULL)
    {
        v.push_back(ptr);
        ptr = strtok(NULL, delimiter);
    }
    free(p);
    p = NULL;
}

void split_string(const string &s, const char *delimiter, vector<int> &v)
{
    char *ptr;
    size_t len = s.size();
    Soft_Array *p = (Soft_Array *)malloc(sizeof(Soft_Array) + sizeof(char) * len);

    strcpy(p->str, s.c_str());
    ptr = strtok(p->str, delimiter);
    while (ptr != NULL)
    {
        v.push_back(atoi(ptr));
        ptr = strtok(NULL, delimiter);
    }
    free(p);
    p = NULL;
}

void split_string(const string &s, const char *delimiter, vector<double> &v)
{
    char *ptr;
    size_t len = s.size();
    Soft_Array *p = (Soft_Array *)malloc(sizeof(Soft_Array) + sizeof(char) * len);

    strcpy(p->str, s.c_str());
    ptr = strtok(p->str, delimiter);
    while (ptr != NULL)
    {
        v.push_back(atof(ptr));
        ptr = strtok(NULL, delimiter);
    }
    free(p);
    p = NULL;
}