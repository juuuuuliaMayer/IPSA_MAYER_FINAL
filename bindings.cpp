#include <pybind11/pybind11.h>
#include "tau1.hpp"

namespace py = pybind11;

PYBIND11_MODULE(tau1_cpp, m) {
    m.doc() = "C++ module for measuring tau1 execution time";
    m.def("tau1_execution_time_ms", &tau1_execution_time_ms, py::arg("num_digits"));
    m.def("seed_rng", &seed_rng, py::arg("seed"));
}