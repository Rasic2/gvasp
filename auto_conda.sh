#!/usr/bin/env bash

rmfile() {
  for file in *; do
    if [ "$file" != "bld.bat" ] && [ "$file" != "build.sh" ] && [ "$file" != "meta.yaml" ]; then
      rm -rf $file
    fi
  done
}

# Directory constant
CondaDir=conda
RootDir=$(pwd)

# delete files first
cd $CondaDir || return
rmfile
cd $RootDir || return

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
rmfile

# back to RootDir
cd "$RootDir" || exit
