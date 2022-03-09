from ast import Raise
import string
import sys
import re

class Token():
    def __init__(self, type, value):
        self.type: str = type
        self.value: int = value

    def __str__(self):
        return f"({self.value},{self.type})"

class Prepro():
    def process(string: str) -> str:
        string = re.sub("/\*.*?\*/", "",string)
        if "/*" in string or "*/" in string:
            raise Exception("CommentError")
        return string

class Tokenizer():
    def __init__(self, origin):
        self.origin: str = origin
        self.position: int = 0
        self.actual: Token = self.selectNext()
    
    def selectNext(self) -> Token:
        self.actual = self._advance()
        return self.actual

    def _advance(self):
        ## Find next token and update self.actual
        token: Token = None
        if self.position == len(self.origin):
            return Token("EOF", "EOF")
        elif self.origin[self.position] == "+":
            token = Token("PLUS", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == "-":
            token = Token("MINUS", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == "*":
            token = Token("MULT", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == "/":
            token = Token("DIV", self.origin[self.position])
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
            token = Token("INT", int(acum))
        else:
            raise Exception(f"LexiconError: Invalid character '{self.origin[self.position]}'")
        return token

class Parser():
    tokens: Tokenizer

    def parseExpression():
        ## Consume tokens, and calculate result
        if Parser.tokens.actual.type != "INT":
            raise SyntaxError
        result = Parser.parseTerm(Parser.tokens.actual.value())
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

    def parseTerm(result):
        curr_token = Parser.tokens.selectNext()
        while curr_token.type == "MULT" or curr_token.type == "DIV":
            Parser.tokens.selectNext() #Avança pro próximo numero
            if Parser.tokens.actual.type != "INT":
                raise SyntaxError
            if curr_token.type == "MULT":
                result *= Parser.tokens.actual.value
            if curr_token.type == "DIV":
                result //= Parser.tokens.actual.value
            
        return result

    def run(source: str):
        ## Inicializa Tokenizer, roda Parser, retorna parseExpression()
        Parser.tokens = Tokenizer(source)
        return Parser.parseExpression()

def main(argv: list, argc: int):
    if argc < 2:
        print("Send more args plz")
        return 1
    _ = Parser()
    _ = Prepro()
    print(Parser.run(Prepro.process(argv[1])))
    return 0

if __name__ == "__main__":
    exit(main(sys.argv, len(sys.argv)))