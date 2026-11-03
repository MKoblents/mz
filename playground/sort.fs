include lib.fs

100 constant max-n
create arr max-n cells allot
variable n
variable tmp

: arr@ ( i -- x ) cells arr + @ ;
: arr! ( x i -- ) cells arr + ! ;

: read-array ( -- )
  read-num n !
  n @ 0 ?do read-num i arr! loop ;

: arr-swap ( i j -- )
  over arr@ tmp !
  dup arr@ rot arr!
  tmp @ swap arr! ;

\ пузырёк: во внутреннем цикле i = индекс элемента
: sort ( -- )
  n @ 2 < if exit then
  n @ 1 ?do
    n @ i - 0 ?do
      i arr@ i 1+ arr@ > if i i 1+ arr-swap then
    loop
  loop ;

: print-array ( -- )
  n @ 0 ?do i arr@ print-num space loop cr ;

: main read-array sort print-array ;

main
bye
