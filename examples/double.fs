include lib.fs

: d+ >r swap >r over + dup rot u< r> r> + swap - ;

: hex-digit dup 10 u< if [char] 0 + else 55 + then emit ;

: print-hex 8 0 do dup 28 rshift 15 and hex-digit 4 lshift loop drop ;

: print-d print-hex print-hex cr ;

: main
  $FFFFFFFF 1 1 0 d+ print-d
  $FFFFFFFF $FFFFFFFF 1 0 d+ print-d
  5 0 7 0 d+ print-d ;

main
bye
