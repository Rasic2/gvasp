#include <cstring>
#include <fstream>
#include <cmath>

using namespace std;

#include "c_doscar_load.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;

struct Soft_Array // 变长数组
{
	int len;
	char str[];
};

vector<string> string_split(const string &s, const char *delimiter)
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

void dimension_cal(Dimensions &dresult, const string filename)
{
	int line_num = 0;
	string s;
	ifstream dosfile;
	vector<string> v;

	dosfile.open(filename, ios::in);
	if (!dosfile.is_open())
	{
		cout << "打开DOSCAR文件失败";
	}

	while (getline(dosfile, s))
	{
		line_num += 1;
		v = string_split(s, " ");
		if (line_num == 1)
		{
			dresult.atoms_num = atoi(v[0].c_str());
		}
		else if (line_num == 6)
		{
			dresult.NEDOS = atoi(v[2].c_str());
		}
		else if (line_num > 6 && line_num == dresult.NEDOS + 8)
		{
			dresult.orbitals_num = v.size() - 1;
			break;
		}
	}
	dosfile.close();
}

ParseResult* doscar_load(string filename)
{
	int line_num = 0, orbitals_num = 0;
	int NEDOS = 1000, count = 0, index = 0;
	double E_Fermi;
	string s;
	ifstream posfile;
	vector<string> v;
	vector<double> energy_list, Total_up, Total_down, atom_oneE_dos;
	vector<vector<double>> atom_dos;
	vector<vector<vector<double>>> atom_total_dos;

	posfile.open(filename, ios::in);
	if (!posfile.is_open())
	{
		cout << "打开文件失败";
	}
	while (getline(posfile, s))
	{
		line_num += 1;
		if (line_num == 6) // 获取NEDOS和E_Fermi能级的值
		{
			v = string_split(s, " ");	// 分割string到vector
			NEDOS = atoi(v[2].c_str()); // 将string先转化为C字符串然后转化为整数
			E_Fermi = atof(v[3].c_str());
		}
		else if (line_num > 6 && line_num <= 6 + NEDOS) // 处理Total_DOS
		{
			v = string_split(s, " ");
			energy_list.push_back(atof(v[0].c_str()) - E_Fermi);
			Total_up.push_back(atof(v[1].c_str()));
			Total_down.push_back(-atof(v[2].c_str()));
		}
		else if (line_num > 6 + NEDOS && (line_num - 6) % (NEDOS + 1) != 0) // 处理原子Projected_DOS
		{
			count += 1;
			v = string_split(s, " ");
			orbitals_num = v.size() - 1;
			for (int i = 1; i != v.size(); i++) // 处理一个原子的一个能级
			{
				atom_oneE_dos.push_back(atof(v[i].c_str()) * pow(-1, (i - 1)));
			}
			atom_dos.push_back(atom_oneE_dos); // 一个原子所有能级的DOS
			atom_oneE_dos.clear();
			if (count == NEDOS)
			{
				count = 0;
				atom_total_dos.push_back(atom_dos); // 所有原子的DOS
				atom_dos.clear();
			}
		}
	}
	posfile.close(); // close the DOSCAR file

	ParseResult *result = new ParseResult();
	result->energy_list.swap(energy_list);
	result->Total_up.swap(Total_up);
	result->Total_down.swap(Total_down);
	result->atom_total_dos.swap(atom_total_dos);
	result->orbitals_num = orbitals_num;
	return result;
}

PYBIND11_MODULE(c_doscar_load, m)
{
	m.doc() = "pybind11 doscar_load plugin"; // optional module docstring
	
	py::class_<ParseResult>(m, "ParseResult")
		.def_readwrite("energy_list", &ParseResult::energy_list)
		.def_readwrite("Total_up", &ParseResult::Total_up)
		.def_readwrite("Total_down", &ParseResult::Total_down)
		.def_readwrite("atom_total_dos", &ParseResult::atom_total_dos)
		.def_readwrite("orbitals_num", &ParseResult::orbitals_num);
	
	m.def("doscar_load", &doscar_load, py::return_value_policy::reference, "A C++ Wrapper to load the DOSCAR file");
}
