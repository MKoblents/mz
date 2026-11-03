$FFFFFFFF constant mask32
variable alo  variable ahi  variable blo  variable bhi

: add64 ( lo1 hi1 lo2 hi2 -- lo hi )
  bhi ! blo ! ahi ! alo !
  alo @ blo @ +
  dup mask32 and
  swap 32 rshift
  ahi @ bhi @ + + mask32 and ;

: .64 ( lo hi -- ) 32 lshift or u. ;

$FFFFFFFF 0 1 0 add64 .64 cr                   \ 4294967296
$FFFFFFFF 1 $FFFFFFFF 1 add64 .64 cr           \ 17179869182
bye
