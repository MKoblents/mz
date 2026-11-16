: digit? [char] 0 - 10 u< ;

: read-num
  begin key dup digit? 0= while drop repeat
  [char] 0 -
  begin key dup digit? while [char] 0 - swap 10 * + repeat
  drop ;

variable neg

: read-int
  0 neg !
  begin key dup digit? over [char] - = or 0= while drop repeat
  dup [char] - = if -1 neg ! drop key then
  [char] 0 -
  begin key dup digit? while [char] 0 - swap 10 * + repeat
  drop
  neg @ if negate then ;

: print-num
  dup 10 u< if [char] 0 + emit exit then
  dup 10 / recurse
  10 mod [char] 0 + emit ;

: pstr-type
  dup @ 0 ?do dup i 1+ cells + @ emit loop drop ;

: read-pstr
  0
  begin
    key dup 10 = 0=
  while
    >r over over 1+ cells + r> swap !
    1+
  repeat
  drop swap ! ;
