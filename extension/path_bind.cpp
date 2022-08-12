#include <cmath>
#include <vector>

using namespace std;

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;

struct PyNumpy
{
    vector<py::array_t<double>> funcs;
    vector<py::array_t<double>> funcs_prime;
};

PyNumpy _get_funcs_and_forces(py::array_t<double> x,
                              py::array_t<double> trans,
                              py::array_t<double> weights,
                              py::array_t<double> target_dists)
{
    py::buffer_info buf_x = x.request();                       // (images+2, atoms_num, 3)
    py::buffer_info buf_trans = trans.request();               // (images, atoms_num, atoms_num, 3)
    py::buffer_info buf_weights = weights.request();           // (images, atoms_num, atoms_num)
    py::buffer_info buf_target_dists = target_dists.request(); // (images, atoms_num, atoms_num)

    double *ptr_x = (double *)buf_x.ptr;
    double *ptr_trans = (double *)buf_trans.ptr;
    double *ptr_weights = (double *)buf_weights.ptr;
    double *ptr_target_dists = (double *)buf_target_dists.ptr;

    PyNumpy ReturnValue;

    int images = buf_x.shape[0] - 2;
    int atoms_num = buf_x.shape[1];
    double func = 0.;
    vector<vector<vector<double>>> vec;
    vector<vector<double>> trial_dist;
    vector<vector<double>> aux;
    vector<vector<double>> grad;

    double sum_k = 0.;
    double sqrt_k = 0.;
    double temp_value = 0.;
    vector<double> temp_vector;
    vector<vector<double>> temp_matrix;
    vector<vector<double>> unit_matrix;
    vector<vector<vector<double>>> temp_tensor;

    // np.eye(atoms_num, dtype=np.float64)
    unit_matrix.clear();
    for (size_t i = 0; i < atoms_num; i++)
    {
        temp_vector.clear();
        for (size_t j = 0; j < atoms_num; j++)
        {
            if (i == j)
            {
                temp_vector.push_back(1.);
            }
            else
            {
                temp_vector.push_back(0.);
            }
        }
        unit_matrix.push_back(temp_vector);
    }

    for (size_t ni = 0; ni < images; ni++)
    {
        // vec = [x[ni + 1, i] - x[ni + 1] - trans[ni, i] for i in range(atoms_num)]
        temp_tensor.clear();
        for (size_t i = 0; i < atoms_num; i++)
        {
            temp_matrix.clear();
            for (size_t j = 0; j < atoms_num; j++)
            {
                temp_vector.clear();
                for (size_t k = 0; k < 3; k++)
                {
                    temp_value = ptr_x[(ni + 1) * atoms_num * 3 + i * 3 + k] - ptr_x[(ni + 1) * atoms_num * 3 + j * 3 + k] - ptr_trans[ni * atoms_num * atoms_num * 3 + i * atoms_num * 3 + j * 3 + k];
                    temp_vector.push_back(temp_value);
                } // temp_vector: (3,)
                temp_matrix.push_back(temp_vector);
            } // temp_matrix: (atoms_num, 3)
            temp_tensor.push_back(temp_matrix);
        }                                                   // temp_matrix: (atoms_num, atoms_num, 3)
        vec.assign(temp_tensor.begin(), temp_tensor.end()); // (atoms_num, atoms_num, 3)

        // trial_dist = np.linalg.norm(vec, axis=2)
        temp_matrix.clear();
        for (size_t i = 0; i < atoms_num; i++)
        {
            temp_vector.clear();
            for (size_t j = 0; j < atoms_num; j++)
            {
                sum_k = 0.;
                for (size_t k = 0; k < 3; k++)
                {
                    sum_k += vec[i][j][k] * vec[i][j][k];
                }
                sqrt_k = sqrt(sum_k);
                temp_vector.push_back(sqrt_k);
            }
            temp_matrix.push_back(temp_vector);
        }
        trial_dist.assign(temp_matrix.begin(), temp_matrix.end()); // (atoms_num, atoms_num)

        // aux = (trial_dist - target_dists[ni]) * weights[ni] / (trial_dist + np.eye(atoms_num, dtype=np.float64))
        temp_matrix.clear();
        for (size_t i = 0; i < atoms_num; i++)
        {
            temp_vector.clear();
            for (size_t j = 0; j < atoms_num; j++)
            {
                temp_value = (trial_dist[i][j] - ptr_target_dists[ni * atoms_num * atoms_num + i * atoms_num + j]) * ptr_weights[ni * atoms_num * atoms_num + i * atoms_num + j] / (trial_dist[i][j] + unit_matrix[i][j]);
                temp_vector.push_back(temp_value);
            }
            temp_matrix.push_back(temp_vector);
        }
        aux.assign(temp_matrix.begin(), temp_matrix.end()); // (atoms_num, atoms_num)

        // func = np.sum((trial_dist - target_dists[ni]) ** 2 * weights[ni])
        for (size_t i = 0; i < atoms_num; i++)
        {
            for (size_t j = 0; j < atoms_num; j++)
            {
                func += pow((trial_dist[i][j] - ptr_target_dists[ni * atoms_num * atoms_num + i * atoms_num + j]), 2) * ptr_weights[ni * atoms_num * atoms_num + i * atoms_num + j];
            }
        }

        // grad = np.sum(aux[:, :, None] * vec, axis=1)
        temp_matrix.clear();
        for (size_t i = 0; i < atoms_num; i++)
        {
            temp_vector.clear();
            for (size_t k = 0; k < 3; k++)
            {
                sum_k = 0.;
                for (size_t j = 0; j < atoms_num; j++)
                {
                    sum_k += aux[i][j] * vec[i][j][k];
                }
                temp_vector.push_back(sum_k);
            }
            temp_matrix.push_back(temp_vector);
        }
        grad.assign(temp_matrix.begin(), temp_matrix.end()); // (atoms_num, 3)
        
        // funcs.append(func)
        py::array_t<double> func_np = py::array_t<double>(1);
        py::buffer_info buf_func_np = func_np.request();
        double *ptr_func_np = (double *)buf_func_np.ptr;
        ptr_func_np[0] = func;
        ReturnValue.funcs.push_back(func_np);
        
        // funcs_prime.append(grad)
        py::array_t<double> grad_np = py::array_t<double>(grad.size() * 3);
        py::buffer_info buf_grad_np = grad_np.request();
        double *ptr_grad_np = (double *)buf_grad_np.ptr;
        for (size_t i = 0; i < atoms_num; i++)
        {
            for (size_t k = 0; k < 3; k++)
            {
                ptr_grad_np[i * 3 + k] = grad[i][k];
            }
        }
        grad_np.resize({atoms_num, 3});
        ReturnValue.funcs_prime.push_back(grad_np);
    }
    return ReturnValue;
}

PYBIND11_MODULE(path_bind, m)
{
    m.doc() = "pybind11 <path> module";

    py::class_<PyNumpy>(m, "PyNumpy")
        .def_readwrite("funcs", &PyNumpy::funcs)
        .def_readwrite("funcs_prime", &PyNumpy::funcs_prime);

    m.def("_get_funcs_and_forces", &_get_funcs_and_forces, "A C++ function to get_funcs_and_forces for idpp");
}