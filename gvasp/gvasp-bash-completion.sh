#!/usr/bin/bash

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
    local cur c=2 opts command 

    while [ $c -lt $COMP_CWORD ]
    do 
        i="${COMP_WORDS[c]}"
        command=$i
        c=$((++c))
    done

    if [ -z "$command" ];then
        COMPREPLY=()
        cur=${COMP_WORDS[COMP_CWORD]}
        opts="opt con-TS chg wf dos freq md stm neb dimer -h --help"
        COMPREPLY=( $( compgen -W "$opts" -- $cur ) ) 
    else
        case "$command" in
        opt) _gvasp_submit_opt ;;
        esac
    fi
}

_gvasp_config() {
    local cur opts
 
    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="-h --help -f --file"
    COMPREPLY=( $( compgen -W "$opts" -- $cur ) )
}

_gvasp() {
    local i cur opts c=1 command
    
    while [ $c -lt $COMP_CWORD ]
    do 
        i="${COMP_WORDS[c]}"
        command=$i
        c=$((++c))
    done

    if [ $COMP_CWORD -gt 2 ]; then
        slice=${COMP_WORDS[@]:1:2}
        new_slice=(${slice[0]})
        command=$(IFS=-; echo "${new_slice[*]}")
    fi

    if [ -z "$command" ];then
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
        esac 
    fi
}

complete  -F _gvasp gvasp