include lib.fs

create msg s" Hello, World!" pstr,

: main ( -- ) msg pstr-type cr ;

main
bye
