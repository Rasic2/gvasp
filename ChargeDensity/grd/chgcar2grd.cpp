#include <iostream>
#include <iomanip>
#include <string>
#include <fstream>
#include <sstream>
#include <array>
#include <vector>
#include <chrono>

#include <ctime>
#include <cstring>
#include <cmath>

#define PI 3.14159265358979323846

using namespace std;
using namespace std::chrono;

struct Soft_Array // 变长数组
{
    int len;
    char stub; // 占位作用
    char str[];
};

vector<string> split_string(const string &s, const char *delimiter)
{
    char *ptr;
    int len = s.size();
    vector<string> v;
    Soft_Array *p = (Soft_Array *)malloc(sizeof(Soft_Array) + sizeof(char) * len);

    strcpy(p->str, s.c_str()); // c_str(): 将string转化为C字符串
    ptr = strtok(p->str, delimiter);
    while (ptr != NULL)
    {
        v.push_back(ptr);
        ptr = strtok(NULL, delimiter);
    }
    free(p);
    p = NULL;

    return v;
}

inline double dot_product(array<double, 3> A, array<double, 3> B)
{
    return A[0] * B[0] + A[1] * B[1] + A[2] * B[2];
}

void myclock(time_t tNow)
{
    tNow = system_clock::to_time_t(system_clock::now());
    cout << ctime(&tNow) << endl;
}

int main()
{
    double DenCut;
    FILE *fp;
    ifstream chgfile;
    ofstream grdfile; 
    stringstream sstream;
    string sline, lstring;
    int lineno = 0;
    vector<string> svector;
    array<array<double, 3>, 3> lattice;
    array<double, 3> length = {0};
    array<double, 3> angle = {0};
    vector<double> densities;
    int sum_elements = 0;
    int NX, NY, NZ;
    time_t tNow;
    char tempcs[50];
    const int offset = 100;
    const size_t Maxlen = 100 * 1024;
    char *buffer = new char[Maxlen];

    cout << "The program is convert the CHGCAR_mag to the .grd chgfile format!" << endl;
    cout << "Please indicate the DenCut to load the charge density!" << endl;
    cout << "If you don't want to use the DenCut, set the DenCut = -1!" << endl;
    cout << "DenCut = ";
    cin >> DenCut;

    chgfile.open("CHGCAR_mag", ios::in);
    if (!chgfile.is_open())
    {
        cout << "Open the CHGCAR_mag failure!" << endl;
    }

    while (getline(chgfile, sline))
    {
        lineno += 1;
        if (lineno >= 3 && lineno <= 5)
        {
            svector = split_string(sline, " ");
            for (int j = 0; j < svector.size(); j++)
            {
                lattice[lineno - 3][j] = atof(svector[j].c_str());
                length[lineno - 3] += pow(lattice[lineno - 3][j], 2);
            }
            length[lineno - 3] = pow(length[lineno - 3], 0.5);
        }
        else if (lineno == 6)
        {
            angle[0] = acos(dot_product(lattice[1], lattice[2]) / (length[1] * length[2])) * 180 / PI;
            angle[1] = acos(dot_product(lattice[0], lattice[2]) / (length[0] * length[2])) * 180 / PI;
            angle[2] = acos(dot_product(lattice[0], lattice[1]) / (length[1] * length[0])) * 180 / PI;
        }
        else if (lineno == 7)
        {
            svector = split_string(sline, " ");
            for (vector<string>::iterator iter = svector.begin(); iter < svector.end(); iter++)
            {
                sum_elements += (atoi((*iter).c_str()));
            }
        }
        else if (lineno == sum_elements + 10)
        {
            svector = split_string(sline, " ");
            NX = atoi(svector[0].c_str());
            NY = atoi(svector[1].c_str());
            NZ = atoi(svector[2].c_str());
        }
        else if (lineno > sum_elements + 10)
        {
            svector = split_string(sline, " ");
            for (int i = 0; i < svector.size(); i++)
            {
                densities.push_back(atof(svector[i].c_str()));
            }
        }
    }
    chgfile.close();
    grdfile.open("vasp_cpp.grd", ios::out);
    if (!grdfile.is_open())
    {
        cout << "Open the .grd file failure!" << endl;
    }
    grdfile << "VASP charge density" << endl;
    grdfile << "(1p,e12.5)" << endl;
    grdfile << fixed << setprecision(3)
            << "  " << length[0] << "  " << length[1] << "  " << length[2]
            << "  " << angle[0] << "  " << angle[1] << "  " << angle[2] << endl;
    grdfile << "  " << NX - 1 << "  " << NY - 1 << "  " << NZ - 1 << endl;
    grdfile << setw(5) << 1 << setw(5) << 0 << setw(5) << NX - 1
            << setw(5) << 0 << setw(5) << NY - 1 << setw(5) << 0 << setw(5) << NZ - 1 << endl;
    grdfile.close();
    if (DenCut != -1)
    {
        for (int i = 0; i < densities.size(); i++)
        {
            if (abs(densities[i]) < DenCut - offset)
            {
                densities[i] = 0.0;
            }
        }
    }
    fp = fopen("vasp_cpp.grd", "a");
    for (int i = 0; i < densities.size(); i++)
    {
        if (abs(densities[i]) > 1e-5)
        {
            snprintf(tempcs, 13, "%12.5E", densities[i]);
        }
        else
        {
            snprintf(tempcs, sizeof(densities[i]) + 1, "%1.0f", densities[i]);
        }
        strcat(buffer, tempcs);
        strcat(buffer, "\n");
        if (i % 1000 == 0)
        {
            fwrite(buffer, strlen(buffer), 1, fp);
            strcpy(buffer, "");
        }
    }
    fwrite(buffer, strlen(buffer), 1, fp);
    fclose(fp);
    return 0;
}
