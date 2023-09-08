# Subc

Subc is a compiler for a subset of the C language written in under 1000 lines of Python.

## Supported Features

- comments (both styles)
- types (void, char, int, pointers)
- enums, structs
- array subscripting
- functions, recursion
- c expressions
- ternary expressions
- if, while, continue, break
- sizeof

## Todo

- finish the algorithm for malloc and free
- for statements
- switch statements

## Unsupported Features

- preprocessor (includes, macros, defines)
- forward declarations
- typedef
- passing structs by value
- returning structs by value
- function pointers
- floats, unions
- checking for incomplete types
- and others...


## Quirks
- function arguments are pushed onto stack in reverse order
- no checks for correct number of function arguments