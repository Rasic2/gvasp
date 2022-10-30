#!/usr/bin/env bash

# Directory constant
CondaDir=conda
RootDir=$(pwd)

# copy source files
cp -r extension $CondaDir
cp -r gvasp $CondaDir
cp LICENSE pytest.ini README.md requirements.txt setup.py $CondaDir

# delete the lib files
rm -rf $CondaDir/extension/dos_cython.cpp
rm -rf $CondaDir/extension/path_cython.c
rm -rf $CondaDir/gvasp/lib/*.so
rm -rf $CondaDir/gvasp/lib/*.pyd

# start make package
cd $CondaDir || exit

conda activate gvasp-build
conda-build purge
conda-build . -c conda-forge
conda activate

# delete all files
for file in *; do
  if [ "$file" != "bld.bat" ] && [ "$file" != "build.sh" ] && [ "$file" != "meta.yaml" ]; then
    rm -rf $file
  fi
done

# back to RootDir
cd "$RootDir" || exit
