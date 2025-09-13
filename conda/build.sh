export CFLAGS="${CFLAGS} -isysroot ${CONDA_BUILD_SYSROOT}"
export CXXFLAGS="${CXXFLAGS} -isysroot ${CONDA_BUILD_SYSROOT}"
$PYTHON -m pip install . --no-deps -vv
