#!/usr/bin/env perl

#功能：实现.cell文件转为POSCAR文件；
#用法：perl create_POSCAR.pl <filename.cell>;
#by 周慧
@ARGV==1||die "usage:perl <filename.cell>\n";
$constant=1;#缩放系数

open (IN,$ARGV[0]) ||die "Can't open *.cell";
open (OUT,">POSCAR");

print "Please name the system:\n";
$system=<STDIN>;
print OUT $system;
print OUT "$constant\n";

#写入晶格矢量
until ($line =~m/%ENDBLOCK LATTICE_CART/){
	$line=<IN>;
	for($i=1;$i<=3;$i++){
		$line=<IN>;
		print OUT $line;
	}
	$line=<IN>;
}
$line=<IN>;
$line=<IN>;

#写入元素和元素个数
until ($line =~m/%ENDBLOCK POSITIONS_FRAC/){
	if ($line=~m/\A(\s+)?([a-zA-Z]+)\s+/){
		if($2 ne $elements[-1]){
			push @elements,$2; #将元素添加到array尾部
			push @counts,$element_number;
			$element_number=1;
		}
		else{
			$element_number++;
		}
	}
	$line=<IN>;
}
push @counts,$element_number;

print OUT "@elements\n";
foreach (@counts){
	if(defined($_)){
		print OUT "$_  ";
		$sum+=$_;
	}
}
print OUT "\n";
print OUT "Direct\n";

#写入坐标
open (IN,$ARGV[0])||die "Can't open *.cell";
until ($line=~m/%BLOCK POSITIONS_FRAC/){
	$line=<IN>;
}
$line=<IN>;

while ($line!~m/%ENDBLOCK POSITIONS_FRAC/){
	if ($line=~m/(\s+)(-?)(\d+).+\n/){
		$coordinates.=$&;
		$total_numbers++;
	}
	$line=<IN>;
}
print OUT $coordinates;
$class_of_elements=@elements;

if ($total_numbers==$sum){
	print "\nThere are $class_of_elements kinds of elements.\n\n@elements\n\n@counts\n\ntotal_numbers=$total_numbers\n";
	print "Good job!\n";
}else{
	print "Something wrong happend! $!";
}
