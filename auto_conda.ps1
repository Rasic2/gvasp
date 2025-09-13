# Directory constant
$CondaDir = "conda"
$RootDir = Get-Location
$Exclued = @("bld.bat", "build.sh", "meta.yaml")

# delete files first
Set-Location $CondaDir
Get-ChildItem -Path "." -Exclude $Exclued | Remove-Item -Force -Recurse
Set-Location $RootDir

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
conda activate gvasp_build
conda-build purge
conda-build . -c conda-forge
conda activate

# delete all files
Get-ChildItem -Path "." -Exclude $Exclued | Remove-Item -Force -Recurse

# back to RootDir
Set-Location $RootDir
