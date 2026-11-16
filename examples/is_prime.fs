include lib.fs

: prime?
  2
  begin
    2dup dup * <
    0=
  while
    2dup mod 0= if 2drop 0 exit then
    1+
  repeat
  2drop -1 ;

: main
  read-int
  dup 1 < if drop ." -1" cr exit then
  dup 1 = if drop 0 print-num cr exit then
  prime? if 1 else 0 then print-num cr ;

main
bye
