CC = g++
STATIC = 
CCFLAG = -g -O3 $(STATIC)

target = chgcar2grd
$(target): $(target).cpp
	$(CC) $(CCFLAG) -o $@ $<
	rm -rf *.dSYM

.PHONY: clean
clean:
	rm -rf $(target)
	
