\ ---------- ввод чисел ----------
: digit? ( c -- f ) [char] 0 - 10 u< ;

\ неотрицательное число: пропустить нецифры, собрать цифры
: read-num ( -- n )
  begin key dup digit? 0= while drop repeat
  [char] 0 -
  begin key dup digit? while [char] 0 - swap 10 * + repeat
  drop ;

\ число со знаком
variable neg
: read-int ( -- n )
  0 neg !
  begin key dup digit? over [char] - = or 0= while drop repeat
  dup [char] - = if -1 neg ! drop key then
  [char] 0 -
  begin key dup digit? while [char] 0 - swap 10 * + repeat
  drop
  neg @ if negate then ;

\ ---------- вывод чисел ----------
: print-num ( n -- )              \ n >= 0
  dup 0= if drop [char] 0 emit exit then
  0 >r
  begin dup while
    10 /mod
    r> 1+ >r
  repeat
  drop
  r> 0 ?do [char] 0 + emit loop ;

\ ---------- pstr ----------
: pstr, ( c-addr u -- )           \ дописать в память: длина, символы
  dup c,
  0 ?do dup i + c@ c, loop
  drop ;

: pstr-type ( addr -- )
  dup c@ 0 ?do dup 1+ i + c@ emit loop
  drop ;

: read-pstr ( addr -- )           \ читать до \n, сложить как pstr
  >r 0
  begin key dup 10 <> while
    over r@ 1+ + c!
    1+
  repeat
  drop r> c! ;
