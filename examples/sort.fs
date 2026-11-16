include lib.fs

create arr 100 cells allot
variable n
variable tmp

: arr@ cells arr + @ ;
: arr! cells arr + ! ;

: read-array
  read-num n !
  n @ 0 ?do read-num i arr! loop ;

: arr-swap
  over arr@ tmp !
  dup arr@ rot arr!
  tmp @ swap arr! ;

: sort
  n @ 2 < if exit then
  n @ 1 ?do
    n @ i - 0 ?do
      i arr@ i 1+ arr@ > if i i 1+ arr-swap then
    loop
  loop ;

: print-array
  n @ 0 ?do i arr@ print-num space loop cr ;

: main read-array sort print-array ;

main
bye
