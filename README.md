# LogComp2022

![git status](http://3.129.230.99/svg/CEDipEngineering/LogComp2022/)

![SintaticDiagram](SyntaticDiagram.svg)

## EBNF:

EXPRESSION = NUMBER, {("+" | "-"), NUMBER};
TERM = NUMBER, {("*" | "/"), NUMBER};

NUMBER = DIGIT, {DIGIT};
DIGIT = 0|1|2|3|4|5|6|7|8|9;

