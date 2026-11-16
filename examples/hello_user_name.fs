include lib.fs

create name 64 cells allot

: main
  ." What is your name?" cr
  name read-pstr
  ." Hello, " name pstr-type [char] ! emit cr ;

main
bye
