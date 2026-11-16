include lib.fs

: say-a ." a" ;
: say-b ." b" ;
: pick-word if ['] say-a else ['] say-b then ;
: demo pick-word execute cr ;

true demo
false demo
bye
