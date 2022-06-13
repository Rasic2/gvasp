#include <iostream>
#include <string>
#include <vector>

using namespace std;

struct Dimensions // 原子数，轨道数和NEDOS值
{
    int NEDOS;
    int atoms_num;
    int orbitals_num;
};

struct ParseResult // 解析结果
{
    vector<double> energy_list;
    vector<double> Total_up;
    vector<double> Total_down;
    vector<vector<vector<double> > > atom_total_dos;
    int orbitals_num;
};

void dimension_cal(Dimensions &dresult, const string filename);
ParseResult *doscar_load(string filename);
