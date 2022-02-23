import string
import sys
import re
from turtle import position

from pyparsing import ParseExpression

class Token():
    def __init__(self, type, value):
        self.type: str = type
        self.value: int = value

    def __str__(self):
        return f"({self.value},{self.type})"

class Tokenizer():
    def __init__(self, origin):
        self.origin: str = origin
        self.position: int = 0
        self.actual: Token
    
    def selectNext(self) -> Token:
        ## Find next token and update self.actual
        if self.position == len(self.origin):
            return Token("EOF", "EOF")
        elif self.origin[self.position] == "+":
            self.actual = Token("PLUS", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == "-":
            self.actual = Token("MINUS", self.origin[self.position])
            self.position += 1
        elif (re.match("[0-9]|\s", self.origin[self.position]) != None):
            # Acumulate number by concat
            acum = ""

            # If is not digit, advance 
            while not (re.match("[0-9]+", self.origin[self.position:]) != None): 
                self.position+=1
                # Recursiveness re-checks previous cases
                return self.selectNext()
            while re.match("[0-9]+", self.origin[self.position:]) != None:
                acum += self.origin[self.position]
                self.position += 1
            self.actual = Token("INT", int(acum))
        else:
            raise Exception(f"LexiconError: Invalid character '{self.origin[self.position]}'")
        return self.actual

class Parser():
    tokens: Tokenizer

    def parseExpression():
        ## Consume tokens, and calculate result
        curr_token = Parser.tokens.selectNext()
        if curr_token.type == "INT":
            result = curr_token.value
            curr_token = Parser.tokens.selectNext()
            while curr_token.type == "PLUS" or curr_token.type == "MINUS":
                if curr_token.type == "PLUS":
                    curr_token = Parser.tokens.selectNext()
                    if curr_token.type == "INT":
                        result += curr_token.value
                    else:
                        raise SyntaxError
                elif curr_token.type == "MINUS":
                    curr_token = Parser.tokens.selectNext()
                    if curr_token.type == "INT":
                        result -= curr_token.value
                    else:
                        raise SyntaxError
                curr_token = Parser.tokens.selectNext()
            return result
        else:
            raise SyntaxError

    def run(source: str):
        ## Inicializa Tokenizer, roda Parser, retorna parseExpression()
        Parser.tokens = Tokenizer(source)
        return Parser.parseExpression()


def main(argv: list, argc: int):
    if argc < 2:
        print("Send more args plz")
        return 1
    _ = Parser()
    print(Parser.run(argv[1]))
    return 0

if __name__ == "__main__":
    exit(main(sys.argv, len(sys.argv)))