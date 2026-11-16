include lib.fs

create fmt-buf 40 cells allot
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
variable dgt

: fmt-len fmt @ @ ;
: fmt-at dup fmt-len < if 1+ cells fmt @ + @ else drop 0 then ;

: sp-n begin dup 0 > while space 1- repeat drop ;

: digits 1 swap begin 10 / dup while swap 1+ swap repeat drop ;

: int-len dup 0< if negate digits 1+ else digits then ;

: print-int
  dup 0< if
    [char] - emit
    dup $80000000 = if drop ." 2147483648" exit then
    negate
  then
  print-num ;

: print-padded
  dup int-len width @ swap -
  left @ 0= if dup sp-n then
  swap print-int
  left @ if sp-n else drop then ;

: parse-spec
  1+
  0 left ! 0 width !
  dup fmt-at [char] - = if -1 left ! 1+ then
  begin dup fmt-at digit? while
    width @ 10 * over fmt-at [char] 0 - + width !
    1+
  repeat
  dup fmt-at [char] d = if 1+ spec-end ! -1 else drop 0 then ;

: count-specs
  0 cnt !
  0
  begin dup fmt-len < while
    dup fmt-at [char] % = if
      dup parse-spec if drop spec-end @ cnt @ 1+ cnt ! else 1+ then
    else 1+ then
  repeat
  drop ;

: read-fmt
  0
  begin key dup 10 <> while
    over 32 < if
      over 1+ cells fmt-buf + !
      1+
    else
      drop -1 bad !
    then
  repeat
  drop fmt-buf ! ;

: overflow?
  214748364 acc @ u<
  acc @ 214748364 = dgt @ 8 > and or ;

: read-int-line
  0 acc ! 1 sgn ! 0 nd !
  key
  dup [char] - = if drop -1 sgn ! key else dup [char] + = if drop key then then
  begin dup 10 <> while
    bad @ 0= if
      dup digit? if
        [char] 0 - dgt !
        overflow? if -1 bad ! else acc @ 10 * dgt @ + acc ! then
        nd @ 1+ nd !
      else drop -1 bad ! then
    else drop then
    key
  repeat
  drop
  nd @ 0= if -1 bad ! then
  sgn @ 1 = 2147483647 acc @ u< and if -1 bad ! then
  acc @ sgn @ * ;

: read-vals
  cnt @ 0 ?do read-int-line i cells vals + ! loop ;

: print-formatted
  0 vi !
  0
  begin dup fmt-len < while
    dup fmt-at [char] % = if
      dup parse-spec if
        drop spec-end @
        vi @ cells vals + @ print-padded
        vi @ 1+ vi !
      else
        [char] % emit 1+
      then
    else
      dup fmt-at emit 1+
    then
  repeat
  drop ;

: main
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
