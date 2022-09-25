#!/usr/bin/bash

RED="\033[1;31m"
RESET="\033[0m"

_files () {
    local c=0
    for file in `ls`
    do
        files[$c]=$file
        c=$((++c))
    done
    echo ${files[@]}
}

_gvasp_submit_opt() {
    local cur opts

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-h --help -P --potential -V --vdw -S --sol -C --continuous -l --low"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) )
}

_gvasp_submit_chg() {
    local cur opts

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-h --help -P --potential -V --vdw -S --sol -C --continuous -s --sequential -a --analysis"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) )
}

_gvasp_submit_wf() {
    local cur opts

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}

    if [[ "${COMP_WORDS[@]}"  =~ "-s" || "${COMP_WORDS[@]}"  =~ "--sequential" ]]; then
        opts="-h --help -P --potential -V --vdw -S --sol -C --continuous -s --sequential -l --low"
    else
        opts="-h --help -P --potential -V --vdw -S --sol -C --continuous -s --sequential"
    fi
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) )
}

_gvasp_submit_dos() {
    local cur opts

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}

    if [[ "${COMP_WORDS[@]}"  =~ "-s" || "${COMP_WORDS[@]}"  =~ "--sequential" ]]; then
        opts="-h --help -P --potential -V --vdw -S --sol -C --continuous -s --sequential -l --low -a --analysis"
    else
        opts="-h --help -P --potential -V --vdw -S --sol -C --continuous -s --sequential"
    fi
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) )
}

_gvasp_submit_neb() {
    local cur opts

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-h --help -P --potential -V --vdw -S --sol -ini --ini_poscar -fni --fni_poscar -i --images -m --method -c --cancel_check_overlap"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) )
}

_gvasp_submit_normal() {
    local cur opts

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-h --help -P --potential -V --vdw -S --sol"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) )
}

_gvasp_submit() {
    local cur opts 

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="opt con-TS chg wf dos freq md stm neb dimer -h --help"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) ) 
}

_gvasp_movie() {
    local cur opts 

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="opt con-TS freq md neb dimer -h --help"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) ) 
}

_gvasp_movie_normal() {
    local cur opts 

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-n --name"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) ) 
}

_gvasp_movie_freq() {
    local cur opts 

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-n --name -f --freq"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) ) 
}

_gvasp_movie_neb() {
    local cur opts 

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-n --name -p --pos"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) ) 
}

_gvasp_sort() {
    local cur opts 

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-h --help -ini --ini_poscar -fni --fni_poscar"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) ) 
}

_gvasp_split() {
    local cur opts 

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-h --help"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) ) 
}

_gvasp_grd() {
    local cur opts 

    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-h --help -n --name -d --DenCut"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) ) 
}

_gvasp_output() {
    local cur opts
 
    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-h --help"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) )
}

_gvasp_config() {
    local cur opts
 
    COMPREPLY=()
    pre=${COMP_WORDS[COMP_CWORD-1]}
    cur=${COMP_WORDS[COMP_CWORD]}

    if [[ "$pre"  =~ "-f" || "$pre"  =~ "--file" ]]; then
        opts=""
        COMPREPLY=( $( compgen -o default -W "$opts" -- $cur ) )
    elif [ $COMP_CWORD -ge 4 ];then
        echo -e "\n${RED}Only support one argument!${RESET}"
    else 
        opts="-h --help -f --file"
        COMPREPLY=( $( compgen -W "$opts" -- $cur ) )
    fi
}

_gvasp() {
    local i cur opts c=1 command first_command second_command

    while [ $c -lt $COMP_CWORD ]
    do 
        i="${COMP_WORDS[c]}"
        command=$i
        c=$((++c))
    done

    first_command=${COMP_WORDS[1]}
    second_command=${COMP_WORDS[2]}

    if [[ $COMP_CWORD -gt 2 && ! $second_command =~ "-" ]]; then
        slice=${COMP_WORDS[@]:1:2}
        new_slice=(${slice[0]})
        command=$(IFS=-; echo "${new_slice[*]}")
    elif [[ $COMP_CWORD -gt 2 && $second_command =~ "-" ]]; then
        if [[ $second_command =~ "-" ]]; then
            command=$first_command
        fi
    fi

    # declare -p command
    
    if [ -z "$command" ];then # gvasp command completion
        COMPREPLY=()
        cur=${COMP_WORDS[COMP_CWORD]}
        opts="config submit output movie sort plot sum split grd -h --help -v --version -l --list "
        COMPREPLY=( $( compgen -W "$opts" -- $cur ) )
    else
        case "$command" in
        config) _gvasp_config ;;
        submit) _gvasp_submit ;;
        submit-opt) _gvasp_submit_opt ;;
        submit-chg) _gvasp_submit_chg ;;
        submit-wf) _gvasp_submit_wf ;;
        submit-dos) _gvasp_submit_dos ;;
        submit-neb) _gvasp_submit_neb ;;
        submit-*) _gvasp_submit_normal ;;
        output) _gvasp_output ;;
        movie) _gvasp_movie ;;
        movie-freq) _gvasp_movie_freq ;;
        movie-neb) _gvasp_movie_neb ;;
        movie-*) _gvasp_movie_normal ;;
        sort) _gvasp_sort ;;
        sum | split) _gvasp_split ;;
        grd) _gvasp_grd ;;
        esac 
    fi
}

complete -o nospace -F _gvasp gvasp