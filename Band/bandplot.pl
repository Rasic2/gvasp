#!/usr/bin/perl 
# Usage: perl bandplot.pl OUTCAR

print "\n";
print "**************************\n";
print " Band Structure generator\n";
print "**************************\n";
print "\n";
print "...Processing data. \n";
print "\n";
system ("grep -n 'band No' OUTCAR > bandfile");
$fermi=`grep 'E-fermi' OUTCAR`;
open(IN,'OUTCAR') || die("Usage:perl bandplot.pl OUTCAR"); 
while(<IN>)
{
    if($_=~m/ISPIN\s*=\s*(\d)\s*/)
    {
        $ispin=$1;
    }
}
@fields=split (':',$fermi);
@Efermi=split(' ',$fields[1]);
open (TMP,'bandfile');
$p=0;
while (<TMP>) 
{
    @fields=split (':');
    $kpoline[$p]=$fields[0];
    $p++;
}
close (TMP);
$nbands=$kpoline[1]-$kpoline[0]-3; #能带数目
$kpoints=$p;
$count=0;
if($ispin==2)
{
    for($b=1;$b<=$nbands;$b++)
    {
        open(IN,'OUTCAR');
        open(OUT,">band_up_$b.dat") || die("Can't open file");
        while(<IN>)
        {
            if($_=~m/^\s+?(\d*?)\s+([-]?\d*?\.\d*?)\s+?\d\.\d*?\s+?\Z/)
            {
                if($1==$b)
                {
                    $energy=$2-$Efermi[0];
                    print OUT "$energy\n";
                    $count++;
                    if($count>$kpoints/2)
                    {
                        close OUT;
                        open(OUT,">band_down_$b.dat");
                        print OUT "$energy\n";
                    }
                }
            }
        }
        close OUT;
        close IN;
    }
}
`rm 'bandfile'`;
print("Done!\n");
