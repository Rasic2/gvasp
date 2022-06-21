#!/bin/bash
i=0
bar=''
index=0
arr=( "|" "/" "-" "\\" )
while [ $i -le 100 ]
do
    let index=index%4
    printf "[%-100s][%d%%][\e[43;46;1m%c\e[0m]\r" "$bar" "$i" "${arr[$index]}"
    let i++
    let index++
    usleep 30000
    bar+='#'
done
printf "\n"
