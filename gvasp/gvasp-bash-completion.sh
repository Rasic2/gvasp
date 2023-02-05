#!/usr/bin/bash

RED="\033[1;31m"
RESET="\033[0m"

_gvasp_submit_opt() {
  local cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  ppre=${COMP_WORDS[COMP_CWORD - 2]}
  cur=${COMP_WORDS[COMP_CWORD]}

  allopts_short=(-P -V -S -C -l -G -N)
  allopts_long=(--potential --vdw --sol --continuous --low --gamma --nelect)
  allopts="-P --potential -V --vdw -S --sol -C --continuous -l --low -G --gamma -H --hse -SP --static -N --nelect"

  for ((i = 0; i < ${#allopts_short[@]}; i++)); do
    if [[ "${COMP_WORDS[*]}" =~ ${allopts_short[i]} || "${COMP_WORDS[*]}" =~ ${allopts_long[i]} ]]; then
      allopts=${allopts/${allopts_short[i]}/}
      allopts=${allopts/${allopts_long[i]}/}
    fi
  done

  if [[ "$pre" =~ "-h" || "$pre" =~ "--help" || "$pre" =~ "-N" || "$pre" =~ "--nelect" ]]; then
    opts=""
  elif [[ "$pre" =~ "-P" || "$pre" =~ "--potential" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91"
  elif [[ "$pre" =~ "PAW" || "$pre" =~ "USPP" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91 $allopts"
  elif [[ "$pre" =~ "-" || "$ppre" =~ "-" ]]; then
    opts="$allopts"
  else
    opts="-h --help -P --potential -V --vdw -S --sol -C --continuous -l --low -G --gamma -H --hse -SP --static -N --nelect"
  fi

  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_submit_chg() {
  local cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  ppre=${COMP_WORDS[COMP_CWORD - 2]}
  cur=${COMP_WORDS[COMP_CWORD]}

  if [[ "${COMP_WORDS[*]}" =~ "-s" || "${COMP_WORDS[*]}" =~ "--sequential" ]]; then
    allopts_short=(-P -s -V -S -C -a -l -G -N)
    allopts_long=(--potential --sequential --vdw --sol --continuous --analysis --low --gamma --nelect)
    allopts="-P --potential -s --sequential -V --vdw -S --sol -G --gamma -H --hse -SP --static -N --nelect -C --continuous -a --analysis -l --low"
  else
    allopts_short=(-P -s -V -S -C -a -G -N)
    allopts_long=(--potential --sequential --vdw --sol --continuous --analysis --gamma --nelect)
    allopts="-P --potential -s --sequential -V --vdw -S --sol -G --gamma -H --hse -SP --static -N --nelect -C --continuous -a --analysis"
  fi

  for ((i = 0; i < ${#allopts_short[@]}; i++)); do
    if [[ "${COMP_WORDS[*]}" =~ ${allopts_short[i]} || "${COMP_WORDS[*]}" =~ ${allopts_long[i]} ]]; then
      allopts=${allopts/${allopts_short[i]}/}
      allopts=${allopts/${allopts_long[i]}/}
    fi
  done

  if [[ "$pre" =~ "-h" || "$pre" =~ "--help" || "$pre" =~ "-N" || "$pre" =~ "--nelect" ]]; then
    opts=""
  elif [[ "$pre" =~ "-P" || "$pre" =~ "--potential" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91"
  elif [[ "$pre" =~ "PAW" || "$pre" =~ "USPP" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91 $allopts"
  elif [[ "$pre" =~ "-" || "$ppre" =~ "-" ]]; then
    opts="$allopts"
  else
    opts="-h --help -P --potential -V --vdw -S --sol -C --continuous -s --sequential -a --analysis -G --gamma -H --hse -SP --static -N --nelect"
  fi
  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_submit_wf() {
  local cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  ppre=${COMP_WORDS[COMP_CWORD - 2]}
  cur=${COMP_WORDS[COMP_CWORD]}

  if [[ "${COMP_WORDS[*]}" =~ "-s" || "${COMP_WORDS[*]}" =~ "--sequential" ]]; then
    allopts_short=(-P -s -V -S -C -l -G -N)
    allopts_long=(--potential --sequential --vdw --sol --continuous --low --gamma --nelect)
    allopts="-P --potential -s --sequential -V --vdw -S --sol -G --gamma -N --nelect -C --continuous -l --low"
  else
    allopts_short=(-P -s -V -S -C -G -N)
    allopts_long=(--potential --sequential --vdw --sol --continuous --gamma --nelect)
    allopts="-P --potential -s --sequential -V --vdw -S --sol -G --gamma -N --nelect -C --continuous"
  fi

  for ((i = 0; i < ${#allopts_short[@]}; i++)); do
    if [[ "${COMP_WORDS[*]}" =~ ${allopts_short[i]} || "${COMP_WORDS[*]}" =~ ${allopts_long[i]} ]]; then
      allopts=${allopts/${allopts_short[i]}/}
      allopts=${allopts/${allopts_long[i]}/}
    fi
  done

  if [[ "$pre" =~ "-h" || "$pre" =~ "--help" || "$pre" =~ "-N" || "$pre" =~ "--nelect" ]]; then
    opts=""
  elif [[ "$pre" =~ "-P" || "$pre" =~ "--potential" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91"
  elif [[ "$pre" =~ "PAW" || "$pre" =~ "USPP" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91 $allopts"
  elif [[ "$pre" =~ "-" || "$ppre" =~ "-" ]]; then
    opts="$allopts"
  else
    opts="-h --help -P --potential -V --vdw -S --sol -C --continuous -s --sequential -G --gamma -N --nelect"
  fi
  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_submit_dos() {
  local cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  ppre=${COMP_WORDS[COMP_CWORD - 2]}
  cur=${COMP_WORDS[COMP_CWORD]}

  if [[ "${COMP_WORDS[*]}" =~ "-s" || "${COMP_WORDS[*]}" =~ "--sequential" ]]; then
    allopts_short=(-P -s -V -S -C -l -a -G -N)
    allopts_long=(--potential --sequential --vdw --sol --continuous --low --analysis --gamma --nelect)
    allopts="-P --potential -s --sequential -V --vdw -S --sol -C --continuous -l --low -a --analysis -G --gamma -N --nelect"
  else
    allopts_short=(-P -s -V -S -C -G -N)
    allopts_long=(--potential --sequential --vdw --sol --continuous --gamma --nelect)
    allopts="-P --potential -s --sequential -V --vdw -S --sol -C --continuous -G --gamma -N --nelect"
  fi

  for ((i = 0; i < ${#allopts_short[@]}; i++)); do
    if [[ "${COMP_WORDS[*]}" =~ ${allopts_short[i]} || "${COMP_WORDS[*]}" =~ ${allopts_long[i]} ]]; then
      allopts=${allopts/${allopts_short[i]}/}
      allopts=${allopts/${allopts_long[i]}/}
    fi
  done

  if [[ "$pre" =~ "-h" || "$pre" =~ "--help" || "$pre" =~ "-N" || "$pre" =~ "--nelect" ]]; then
    opts=""
  elif [[ "$pre" =~ "-P" || "$pre" =~ "--potential" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91"
  elif [[ "$pre" =~ "PAW" || "$pre" =~ "USPP" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91 $allopts"
  elif [[ "$pre" =~ "-" || "$ppre" =~ "-" ]]; then
    opts="$allopts"
  else
    opts="-h --help -P --potential -V --vdw -S --sol -C --continuous -s --sequential -G --gamma -N --nelect"
  fi
  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_submit_neb() {
  local cur opts fileshow=""

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  ppre=${COMP_WORDS[COMP_CWORD - 2]}
  cur=${COMP_WORDS[COMP_CWORD]}

  allopts_short=(-P -V -S -ini -fni -i -m -c -G -N)
  allopts_long=(--potential --vdw --sol --ini_poscar --fni_poscar --images --method --cancel_check_overlap --gamma --nelect)
  allopts="-P --potential -V --vdw -S --sol -ini --ini_poscar -fni --fni_poscar -i --images -m --method -c --cancel_check_overlap -G --gamma -N --nelect"

  for ((i = 0; i < ${#allopts_short[@]}; i++)); do
    if [[ "${COMP_WORDS[*]}" =~ ${allopts_short[i]} || "${COMP_WORDS[*]}" =~ ${allopts_long[i]} ]]; then
      allopts=${allopts/${allopts_short[i]}/}
      allopts=${allopts/${allopts_long[i]}/}
    fi
  done

  if [[ "$pre" =~ "-h" || "$pre" =~ "--help" || "$pre" =~ "-i" || "$pre" =~ "--images" || "$pre" =~ "-N" || "$pre" =~ "--nelect" ]]; then
    opts=""
  elif [[ "$pre" =~ "-P" || "$pre" =~ "--potential" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91"
  elif [[ "$pre" =~ "PAW" || "$pre" =~ "USPP" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91 $allopts"
  elif [[ "$pre" =~ "-ini" || "$pre" =~ "-fni" || "$pre" =~ "--ini_poscar" || "$pre" =~ "--fni_poscar" ]]; then
    opts=""
    fileshow="-o default"
  elif [[ "$pre" =~ "-m" || "$pre" =~ "--method" ]]; then
    opts="linear idpp"
  elif [[ "$ppre" =~ "-ini" || "$ppre" =~ "--ini_poscar" ]]; then
    opts="-fni --fni_poscar"
  elif [[ "$pre" =~ "-" || "$ppre" =~ "-" ]]; then
    opts="$allopts"
  else
    opts="-h --help -P --potential -V --vdw -S --sol -ini --ini_poscar -fni --fni_poscar -i --images -m --method -c --cancel_check_overlap -G --gamma -N --nelect"
  fi
  COMPREPLY=($(compgen $fileshow -W "$opts" -- $cur))
}

_gvasp_submit_normal() {
  local cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  ppre=${COMP_WORDS[COMP_CWORD - 2]}
  cur=${COMP_WORDS[COMP_CWORD]}

  allopts_short=(-P -V -S -G -N)
  allopts_long=(--potential --vdw --sol --gamma --nelect)
  allopts="-P --potential -V --vdw -S --sol -G --gamma -N --nelect"

  for ((i = 0; i < ${#allopts_short[@]}; i++)); do
    if [[ "${COMP_WORDS[*]}" =~ ${allopts_short[i]} || "${COMP_WORDS[*]}" =~ ${allopts_long[i]} ]]; then
      allopts=${allopts/${allopts_short[i]}/}
      allopts=${allopts/${allopts_long[i]}/}
    fi
  done

  if [[ "$pre" =~ "-h" || "$pre" =~ "--help" || "$pre" =~ "-N" || "$pre" =~ "--nelect" ]]; then
    opts=""
  elif [[ "$pre" =~ "-P" || "$pre" =~ "--potential" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91"
  elif [[ "$pre" =~ "PAW" || "$pre" =~ "USPP" ]]; then
    opts="PAW_LDA PAW_PBE PAW_PW91 USPP_LDA USPP_PW91 $allopts"
  elif [[ "$pre" =~ "-" || "$ppre" =~ "-" ]]; then
    opts="$allopts"
  else
    opts="-h --help -P --potential -V --vdw -S --sol -G --gamma -N --nelect"
  fi

  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_submit() {
  local cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  cur=${COMP_WORDS[COMP_CWORD]}
  if [[ "$pre" =~ "-" ]]; then
    opts=""
  else
    opts="opt con-TS chg wf dos freq md stm neb dimer -h --help"
  fi
  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_movie() {
  local pre cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  cur=${COMP_WORDS[COMP_CWORD]}
  if [[ "$pre" =~ "-" ]]; then
    opts=""
  else
    opts="opt con-TS freq md neb dimer -h --help"
  fi
  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_movie_normal() { # gvasp movie [opt con-TS md dimer] completion
  local pre cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  cur=${COMP_WORDS[COMP_CWORD]}
  if [ $COMP_CWORD -ge 5 ]; then
    echo -e "\n${RED}One arguments maximum!${RESET}"
  elif [[ "$pre" =~ "-" ]]; then
    opts=""
  else
    opts="-n --name"
  fi
  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_movie_freq() { # gvasp movie freq completion
  local pre cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  ppre=${COMP_WORDS[COMP_CWORD - 2]}
  cur=${COMP_WORDS[COMP_CWORD]}

  if [ $COMP_CWORD -ge 7 ]; then
    echo -e "\n${RED}Two arguments maximum!${RESET}"
  elif [[ "$pre" =~ "-" ]]; then
    opts=""
  elif [[ "$ppre" =~ "-f" || "$ppre" =~ "--freq" ]]; then
    opts="-n --name"
  elif [[ "$ppre" =~ "-n" || "$ppre" =~ "--name" ]]; then
    opts="-f --freq"
  else
    opts="-n --name -f --freq"
  fi
  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_movie_neb() { # gvasp movie neb completion
  local pre cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  ppre=${COMP_WORDS[COMP_CWORD - 2]}
  cur=${COMP_WORDS[COMP_CWORD]}

  if [ $COMP_CWORD -ge 7 ]; then
    echo -e "\n${RED}Two arguments maximum!${RESET}"
  elif [[ "$pre" =~ "-p" || "$pre" =~ "--pos" ]]; then
    opts="POSCAR CONTCAR"
  elif [[ "$pre" =~ "-" ]]; then
    opts=""
  elif [[ "$ppre" =~ "-p" || "$ppre" =~ "--pos" ]]; then
    opts="-n --name"
  elif [[ "$ppre" =~ "-n" || "$ppre" =~ "--name" ]]; then
    opts="-p --pos"
  else
    opts="-n --name -p --pos"
  fi
  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_plot() {
  local pre cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  cur=${COMP_WORDS[COMP_CWORD]}
  if [[ "$pre" =~ "-" ]]; then
    opts=""
  else
    opts="-h --help opt band ep dos PES neb"
  fi
  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_plot_normal() { # gvasp plot [opt, band, op, dos, PES, neb]
  local pre cur opts fileshow=""

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  ppre=${COMP_WORDS[COMP_CWORD - 2]}
  cur=${COMP_WORDS[COMP_CWORD]}

  if [[ "$pre" =~ "-j" || "$pre" =~ "--json" ]]; then
    opts=""
    fileshow="-o default"
  elif [[ "$pre" =~ "-" ]]; then
    opts=""
  elif [[ "$ppre" =~ "-j" || "$ppre" =~ "--json" ]]; then
    opts="--save --show"
  else
    opts="-h --help -j --json --show --save"
  fi
  COMPREPLY=($(compgen $fileshow -W "$opts" -- $cur))
}

_gvasp_sort() {
  local pre cur opts fileshow=""

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  ppre=${COMP_WORDS[COMP_CWORD - 2]}
  cur=${COMP_WORDS[COMP_CWORD]}

  if [[ $COMP_CWORD -ge 6 ]]; then
    echo -e "\n${RED}Two arguments maximum!${RESET}"
  elif [[ "$pre" =~ "-ini" || "$pre" =~ "-fni" || "$pre" =~ "--ini_poscar" || "$pre" =~ "--fni_poscar" ]]; then
    opts=""
    fileshow="-o default"
  elif [[ "$pre" =~ "-" ]]; then
    opts=""
  elif [[ "$ppre" =~ "-ini" || "$ppre" =~ "--ini_poscar" ]]; then
    opts="-fni --fni_poscar"
  else
    opts="-h --help -ini --ini_poscar -fni --fni_poscar"
  fi
  COMPREPLY=($(compgen $fileshow -W "$opts" -- $cur))
}

_gvasp_split() {
  local cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  cur=${COMP_WORDS[COMP_CWORD]}
  if [[ "$pre" =~ "-" ]]; then
    opts=""
  else
    opts="-h --help"
  fi
  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_grd() { # gvasp grd completion
  local pre cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  ppre=${COMP_WORDS[COMP_CWORD - 2]}
  cur=${COMP_WORDS[COMP_CWORD]}

  if [[ $COMP_CWORD -ge 6 ]]; then
    echo -e "\n${RED}Two arguments maximum!${RESET}"
  elif [[ "$pre" =~ "-" ]]; then
    opts=""
  elif [[ "$ppre" =~ "-d" || "$ppre" =~ "--DenCut" ]]; then
    opts="-n --name"
  elif [[ "$ppre" =~ "-n" || "$ppre" =~ "--name" ]]; then
    opts="-d --DenCut"
  else
    opts="-h --help -n --name -d --DenCut"
  fi

  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_output() {
  local pre cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  cur=${COMP_WORDS[COMP_CWORD]}

  if [[ $COMP_CWORD -ge 3 ]]; then
    echo -e "\n${RED}One arguments maximum!${RESET}"
  elif [[ "$pre" =~ "-" ]]; then
    opts=""
  else
    opts="-h --help"
  fi
  COMPREPLY=($(compgen -W "$opts" -- $cur))
}

_gvasp_config() { # gvasp config completion
  local cur opts

  COMPREPLY=()
  pre=${COMP_WORDS[COMP_CWORD - 1]}
  cur=${COMP_WORDS[COMP_CWORD]}

  if [[ "$pre" =~ "-f" || "$pre" =~ "--file" ]]; then
    opts=""
    COMPREPLY=($(compgen -o default -W "$opts" -- $cur))
  elif [ $COMP_CWORD -ge 4 ]; then
    echo -e "\n${RED}One argument maximum!${RESET}"
  else
    opts="-h --help -f --file"
    COMPREPLY=($(compgen -W "$opts" -- $cur))
  fi
}

_gvasp() {
  local i cur opts c=1 command first_command second_command

  while [ $c -lt $COMP_CWORD ]; do
    i="${COMP_WORDS[c]}"
    command=$i
    c=$((++c))
  done

  first_command=${COMP_WORDS[1]}
  second_command=${COMP_WORDS[2]}

  if [[ $COMP_CWORD -gt 2 && ! $second_command =~ "-" ]]; then
    slice=${COMP_WORDS[*]:1:2}
    new_slice=(${slice[0]})
    command=$(
      IFS=-
      echo "${new_slice[*]}"
    )
  elif [[ $COMP_CWORD -gt 2 && $second_command =~ "-" ]]; then
    if [[ $second_command =~ "-" ]]; then
      command=$first_command
    fi
  fi

  if [ -z "$command" ]; then # gvasp command completion
    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    opts="config submit output movie sort plot sum split grd -h --help -v --version -l --list -d"
    COMPREPLY=($(compgen -W "$opts" -- $cur))
  else
    case "$command" in # gvasp subcommand completion
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
    plot) _gvasp_plot ;;
    plot-*) _gvasp_plot_normal ;;
    esac
  fi
}

complete -o nospace -F _gvasp gvasp
