include lib.fs

create xs 200 cells allot
variable n

: x@ dup 0< if drop 0 else cells xs + @ then ;
: x! cells xs + ! ;

: main
  read-num n !
  n @ 0 ?do read-num i x! loop
  n @ 0 ?do
    i x@ 3 * i 1- x@ 2 * + i 2 - x@ +
    print-num space
  loop cr ;

main
bye
