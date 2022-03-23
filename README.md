# LogComp2022

![git status](http://3.129.230.99/svg/CEDipEngineering/LogComp2022/)

![SintaticDiagram](SyntaticDiagram.svg)

## EBNF:

DIGIT = 0|1|2|3|4|5|6|7|8|9;
NUMBER = DIGIT, {DIGIT};
EXPRESSION = TERM, { ("+" | "-"), TERM } ;
TERM = FACTOR, { ("*" | "/"), FACTOR } ;
FACTOR = ("+" | "-") FACTOR | "(" EXPRESSION ")" | NUMBER ;

