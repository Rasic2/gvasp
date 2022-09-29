# Directory constant
$CondaDir = "conda"
$RootDir = Get-Location

# copy source files
Copy-Item -r extension $CondaDir
Copy-Item -r gvasp $CondaDir
Copy-Item LICENSE, pytest.ini, README.md, requirements.txt, setup.py $CondaDir

# delete the lib files
Remove-Item $CondaDir/extension/dos_cython.cpp
Remove-Item $CondaDir/extension/path_cython.c
Remove-Item $CondaDir/gvasp/lib/*.so
Remove-Item $CondaDir/gvasp/lib/*.pyd

# start make package
Set-Location $CondaDir
conda activate gvasp_build_conda
conda-build purge
conda-build .
conda activate

# delete all files
$Exclued = @("bld.bat", "build.sh", "meta.yaml")
Get-ChildItem -Path "." -Exclude $Exclued | Remove-Item -Force -Recurse

# back to RootDir
Set-Location $RootDir