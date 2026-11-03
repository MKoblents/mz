include lib.fs

create fmt-buf 40 allot
create vals 16 cells allot
variable fmt
variable bad
variable cnt
variable vi
variable left
variable width
variable spec-end
variable acc
variable sgn
variable nd

\ ---------- доступ к формату ----------
: fmt-len ( -- n ) fmt @ c@ ;
: fmt-at ( pos -- c ) dup fmt-len < if fmt @ 1+ + c@ else drop 0 then ;

\ ---------- вывод с выравниванием ----------
: sp-n ( n -- ) 0 max 0 ?do space loop ;

: digits ( n -- len )             \ n >= 0
  1 swap
  begin 10 / dup while swap 1+ swap repeat
  drop ;

: int-len ( n -- len )
  dup 0< if negate digits 1+ else digits then ;

: print-int ( n -- )
  dup 0< if [char] - emit negate then print-num ;

: print-padded ( n -- )
  dup int-len width @ swap -
  left @ 0= if dup sp-n then
  swap print-int
  left @ if sp-n else drop then ;

\ ---------- разбор спецификатора ----------
\ pos указывает на '%'. При успехе left, width, spec-end заполнены.
: parse-spec ( pos -- flag )
  1+
  0 left !  0 width !
  dup fmt-at [char] - = if -1 left ! 1+ then
  begin dup fmt-at digit? while
    width @ 10 * over fmt-at [char] 0 - + width !
    1+
  repeat
  dup fmt-at [char] d = if 1+ spec-end ! -1 else drop 0 then ;

: count-specs ( -- )
  0 cnt !
  0
  begin dup fmt-len < while
    dup fmt-at [char] % = if
      dup parse-spec if drop spec-end @ 1 cnt +! else 1+ then
    else 1+ then
  repeat
  drop ;

\ ---------- чтение формата (максимум 32 символа) ----------
: read-fmt ( -- )
  0
  begin key dup 10 <> while
    over 32 < if over fmt-buf 1+ + c! 1+ else drop -1 bad ! then
  repeat
  drop fmt-buf c! ;

\ ---------- строгое чтение числа: [-|+]цифры, диапазон int32 ----------
: read-int-line ( -- n )
  0 acc !  1 sgn !  0 nd !
  key
  dup [char] - = if drop -1 sgn ! key
  else dup [char] + = if drop key then then
  begin dup 10 <> while
    bad @ 0= if
      dup digit? if
        [char] 0 - acc @ 10 * + acc !
        1 nd +!
        acc @ 2147483648 > if -1 bad ! then
      else drop -1 bad ! then
    else drop then
    key
  repeat
  drop
  nd @ 0= if -1 bad ! then
  sgn @ 1 = acc @ 2147483647 > and if -1 bad ! then
  acc @ sgn @ * ;

: read-vals ( -- )
  cnt @ 0 ?do read-int-line i cells vals + ! loop ;

\ ---------- печать по формату ----------
: print-formatted ( -- )
  0 vi !
  0
  begin dup fmt-len < while
    dup fmt-at [char] % = if
      dup parse-spec if
        drop spec-end @
        vi @ cells vals + @ print-padded
        1 vi +!
      else
        [char] % emit 1+
      then
    else
      dup fmt-at emit 1+
    then
  repeat
  drop ;

: main ( -- )
  0 bad !
  fmt-buf fmt !
  read-fmt
  bad @ if ." -1" cr exit then
  count-specs
  read-vals
  bad @ if ." -1" cr exit then
  print-formatted cr ;

main
bye
