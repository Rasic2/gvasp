#include "file_lib.h"
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
    array<double, 3> length;
    array<double, 3> angle;
    vector<double> density;
};

#pragma GCC visibility push(hidden)
struct PyCHGInfo
{
    int NGX;
    int NGY;
    int NGZ;
    py::array_t<double> density;
};
#pragma GCC visibility pop

inline double dot_product(array<double, 3> A, array<double, 3> B)
{
    return A[0] * B[0] + A[1] * B[1] + A[2] * B[2];
}

void read_chg(string name, CHGInfo &info)
{
    ifstream chgfile;
    string line;
    int lineno = 0;
    vector<double> double_v;
    vector<int> int_v;
    array<array<double, 3>, 3> lattice;
    array<double, 3> length = {0};
    array<double, 3> angle = {0};
    int sum_elements = 0;
    int NGX = -1, NGY = -1, NGZ = -1;
    vector<double> density;

    chgfile.open(name, ios::in);
    if (!chgfile.is_open())
    {
        throw runtime_error("file open failure");
    }

    while (getline(chgfile, line))
    {
        lineno += 1;
        if (lineno >= 3 && lineno <= 5)
        {
            double_v.clear();
            split_string(line, " ", double_v);
            for (size_t j = 0; j < double_v.size(); j++)
            {
                lattice[lineno - 3][j] = double_v[j];
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
            int_v.clear();
            split_string(line, " ", int_v);
            sum_elements = accumulate(int_v.begin(), int_v.end(), 0);
        }
        else if (lineno == sum_elements + 10)
        {
            int_v.clear();
            split_string(line, " ", int_v);
            NGX = int_v[0];
            NGY = int_v[1];
            NGZ = int_v[2];
        }
        else if (lineno > sum_elements + 10)
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
    info.length = length;
    info.angle = angle;
    info.density.assign(density.begin(), density.end());
}

void to_grd(const char *name, double DenCut)
{
    ofstream grdfile;
    vector<double> density;
    const int offset = 100;
    FILE *fp;
    const size_t Maxlen = 100 * 1024;
    char *buffer = new char[Maxlen];
    char tempcs[50];

    CHGInfo info;
    read_chg("CHGCAR_mag", info);
    density.assign(info.density.begin(), info.density.end());

    grdfile.open(name, ios::out);
    if (!grdfile.is_open())
    {
        cout << "Open the .grd file failure!" << endl;
    }
    grdfile << "VASP charge density" << endl;
    grdfile << "(1p,e12.5)" << endl;
    grdfile << fixed << setprecision(3)
            << "  " << info.length[0] << "  " << info.length[1] << "  " << info.length[2]
            << "  " << info.angle[0] << "  " << info.angle[1] << "  " << info.angle[2] << endl;
    grdfile << "  " << info.NGX - 1 << "  " << info.NGY - 1 << "  " << info.NGZ - 1 << endl;
    grdfile << setw(5) << 1 << setw(5) << 0 << setw(5) << info.NGX - 1
            << setw(5) << 0 << setw(5) << info.NGY - 1 << setw(5) << 0 << setw(5) << info.NGZ - 1 << endl;
    grdfile.close();
    if (DenCut != -1)
    {
        for (size_t i = 0; i < density.size(); i++)
        {
            if (abs(density[i]) < DenCut - offset)
            {
                density[i] = 0.0;
            }
        }
    }
    fp = fopen(name, "a");
    strcpy(buffer, "");
    for (size_t i = 0; i < density.size(); i++)
    {
        if (abs(density[i]) > 1e-5)
        {
            snprintf(tempcs, 13, "%12.5E", density[i]);
        }
        else
        {
            snprintf(tempcs, sizeof(density[i]) + 1, "%1.0f", density[i]);
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

PyCHGInfo load(string name)
{
    CHGInfo info;
    PyCHGInfo pyinfo;

    read_chg(name, info);
    pyinfo.NGX = info.NGX;
    pyinfo.NGY = info.NGY;
    pyinfo.NGZ = info.NGZ;

    pyinfo.density = py::array_t<double>(pyinfo.NGX * pyinfo.NGY * pyinfo.NGZ);
    py::buffer_info buf_density = pyinfo.density.request();
    double *ptr_density = (double *)buf_density.ptr;
    for (size_t i = 0; i < info.density.size(); i++)
    {
        ptr_density[i] = info.density[i];
    }
    return pyinfo;
}

PYBIND11_MODULE(file_bind, m)
{
    m.doc() = "pybind11 <file> module";

    py::class_<PyCHGInfo>(m, "PyCHGInfo")
        .def_readwrite("NGX", &PyCHGInfo::NGX)
        .def_readwrite("NGY", &PyCHGInfo::NGY)
        .def_readwrite("NGZ", &PyCHGInfo::NGZ)
        .def_readwrite("density", &PyCHGInfo::density);

    m.def("to_grd", &to_grd, "A C++ function to transform CHGCAR_mag to *.grd file");
    m.def("load", &load, "A C++ function to load CHGBase file");
}
