#include "_lib.h"
#define PI 3.14159265358979323846

#include <iomanip>
#include <sstream>
#include <chrono>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;

using namespace std::chrono;

struct CHGInfo
{
    int NGX;
    int NGY;
    int NGZ;
    py::array_t<double> density;
};

inline double dot_product(array<double, 3> A, array<double, 3> B)
{
    return A[0] * B[0] + A[1] * B[1] + A[2] * B[2];
}

void to_grd(const char *name, double DenCut)
{
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
    char tempcs[50];
    const int offset = 100;
    const size_t Maxlen = 100 * 1024;
    char *buffer = new char[Maxlen];

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
            split_string(sline, " ", svector);
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
            split_string(sline, " ", svector);
            for (vector<string>::iterator iter = svector.begin(); iter < svector.end(); iter++)
            {
                sum_elements += (atoi((*iter).c_str()));
            }
        }
        else if (lineno == sum_elements + 10)
        {
            split_string(sline, " ", svector);
            NX = atoi(svector[0].c_str());
            NY = atoi(svector[1].c_str());
            NZ = atoi(svector[2].c_str());
        }
        else if (lineno > sum_elements + 10)
        {
            split_string(sline, " ", svector);
            for (int i = 0; i < svector.size(); i++)
            {
                densities.push_back(atof(svector[i].c_str()));
            }
        }
    }
    chgfile.close();
    grdfile.open(name, ios::out);
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
    fp = fopen(name, "a");
    strcpy(buffer, "");
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
    delete[] buffer;
}

CHGInfo load(string name)
{
    ifstream chgfile;
    string line;
    int lineno = 0, AtomsNum = -1;
    int NGX, NGY, NGZ;
    vector<int> int_v;
    vector<double> double_v;
    vector<double> density;
    CHGInfo info;

    chgfile.open("CHGCAR_mag", ios::in);
    if (!chgfile.is_open())
    {
        throw runtime_error("file open failure");
    }

    while (getline(chgfile, line))
    {
        lineno += 1;
        if (lineno == 7)
        {
            split_string(line, " ", int_v);
            AtomsNum = accumulate(int_v.begin(), int_v.end(), 0);
        }
        else if (AtomsNum != -1 && lineno == AtomsNum + 10)
        {
            int_v.clear();
            split_string(line, " ", int_v);
            NGX = int_v[0];
            NGY = int_v[1];
            NGZ = int_v[2];
        }
        else if (AtomsNum != -1 && lineno > AtomsNum + 10)
        {
            double_v.clear();
            split_string(line, " ", double_v);
            density.insert(density.end(), double_v.begin(), double_v.end());
        }
    }
    chgfile.close();

    info.NGX = NGX;
    info.NGY = NGY;
    info.NGZ = NGZ;
    info.density = py::array_t<double>(NGX * NGY * NGZ);

    py::buffer_info buf_density = info.density.request();
    double *ptr_density = (double *)buf_density.ptr;
    for (size_t i = 0; i < density.size(); i++)
    {
        ptr_density[i] = density[i];
    }

    return info;
}

PYBIND11_MODULE(_file, m)
{
    m.doc() = "pybind11 <file> module";

    py::class_<CHGInfo>(m, "CHGInfo")
        .def_readwrite("NGX", &CHGInfo::NGX)
        .def_readwrite("NGY", &CHGInfo::NGY)
        .def_readwrite("NGZ", &CHGInfo::NGZ)
        .def_readwrite("density", &CHGInfo::density);

    m.def("to_grd", &to_grd, "A C++ function to transform CHGCAR_mag to *.grd file");
    m.def("load", &load, "A C++ function to load CHGBase file");
}