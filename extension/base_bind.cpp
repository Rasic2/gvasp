using namespace std;

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;

py::array_t<int> search_image(py::array_t<double> atom_i_frac_coord, py::array_t<double> atom_j_frac_coord)
{
    py::buffer_info buf_i = atom_i_frac_coord.request();
    py::buffer_info buf_j = atom_j_frac_coord.request();
    double *ptr_i = (double *)buf_i.ptr;
    double *ptr_j = (double *)buf_j.ptr;

    py::array_t<int> image = py::array_t<int>(3);
    py::buffer_info buf_image = image.request();
    int *ptr_image = (int *)buf_image.ptr;

    for (size_t i = 0; i < buf_i.shape[0]; i++)
    {
        if (ptr_j[i] - ptr_i[i] > 0.5)
        {
            ptr_image[i] = -1;
        }
        else if (ptr_j[i] - ptr_i[i] < -0.5)
        {
            ptr_image[i] = 1;
        }
        else
        {
            ptr_image[i] = 0;
        }
    }

    for (size_t i=0; i<buf_image.shape[0];i++)
    {
        if (ptr_j[i]+ptr_image[i]-ptr_i[i]>0.5 || ptr_j[i]+ptr_image[i]-ptr_i[i]<-0.5)
        {
            throw runtime_error("Transform Error, exit!");
        }
    }
    return image;
}

PYBIND11_MODULE(base_bind, m)
{
    m.doc() = "pybind11 <base> module";
    m.def("search_image", &search_image, "A C++ function to search image for PBC");
}
