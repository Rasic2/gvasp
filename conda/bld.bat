call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
"%PYTHON%" -m pip install . --no-deps -vv
if errorlevel 1 exit 1
