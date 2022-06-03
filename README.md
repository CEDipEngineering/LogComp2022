# LogComp2022

![git status](http://3.129.230.99/svg/CEDipEngineering/LogComp2022/)

![SintaticDiagram](SyntaticDiagram.svg)

Source for function assembly:

https://aaronbloomfield.github.io/pdr/book/x86-32bit-ccc-chapter.pdf

## EBNF:

PROGRAM = { FUNCDEC };

FUNCDEC = TYPE, IDENT, "(", λ | ( (TYPE, IDENT) , {"," TYPE, IDENT} ), ")", BLOCK ;

BLOCK = "{", { STATEMENT }, "}" ;

STATEMENT = ( λ | ASSIGNMENT | PRINT | DECLARATION | RETURN | CALL ), ";" 
            | ( WHILE | IF | BLOCK ) ;

DECALARTION = TYPE, IDENT, {",", IDENT};

RETURN = "return", "(", RELEXPRESSION ")" 
        | "return";

CALL = IDENT, "(", λ | ( (RELEXPRESSION) , {"," RELEXPRESSION} ), ")";

WHILE = "while", "(", RELEXPRESSION, ")", STATEMENT ;

IF = "if", "(", RELEXPRESSION, ")", STATEMENT, ( λ | ("else", STATEMENT) );

ASSIGNMENT = IDENTIFIER, "=", RELEXPRESSION ;

PRINT = "printf", "(", RELEXPRESSION, ")" ;

RELEXPRESSION = EXPRESSION, { ("==" | ">" | "<" ), EXPRESSION }

EXPRESSION = TERM, { ("+" | "-" | "||" | "." ), TERM } ;

TERM = FACTOR, { ("*" | "/" | "&&" ), FACTOR } ;

FACTOR = (("+" | "-" | "!" ), FACTOR) 
        | NUMBER 
        | STRING
        | IDENTIFIER 
        | CALL
        | "(", RELEXPRESSION, ")" 
        | SCANF, "(", ")", ;
        ;

IDENTIFIER = LETTER, { LETTER | DIGIT | "_" } ;

NUMBER = DIGIT, { DIGIT } ;

STRING = '"', LETTER, {LETTER}, '"';

LETTER = ( a | ... | z | A | ... | Z ) ;

DIGIT = ( 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 ) ;



