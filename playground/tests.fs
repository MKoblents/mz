: hello ." hello " ;
: cat ( -- )  begin key emit again ;

create user-name 64 allot


: pstr, ( c-addr u -- )
  dup c,
  0 ?do dup i + c@ c, loop
  drop ;

create ask-msg   s" What is your name?" pstr,
create hello-msg s" Hello, " pstr,

: pstr-type ( addr -- )
  dup c@ 0 ?do dup 1+ i + c@ emit loop
  drop ;

: read-name ( -- )
  0
  begin key dup 10 <> while
    over user-name 1+ + c!
    1+
  repeat
  drop user-name c! ;

: main ( -- )
  ask-msg pstr-type cr
  read-name
  hello-msg pstr-type
  user-name pstr-type
  [char] ! emit cr ;

main 
