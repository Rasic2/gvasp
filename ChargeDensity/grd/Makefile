FF = gfortran

target = chgcar2grd

$(target): $(target).f90
	$(FF) -o $@ $<

.PHONY: clean
clean:
	rm -rf $(target)
