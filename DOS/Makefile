CC = g++

#main-test: main-test.cpp c_doscar_load.so
#	$(CC) -o main-test main-test.cpp c_doscar_load.so

c_doscar_load.so: c_doscar_load.cpp
	$(CC) -O3 -std=gnu++17 -fPIC -shared -o c_doscar_load.so c_doscar_load.cpp -I /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/pybind11/include -I /Library/Frameworks/Python.framework/Versions/3.8/include/python3.8 -L /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/config-3.8-darwin/ -lpython3.8

.PHONY: clean
clean:
	rm -rf *.so main-test

