import string
import sys
import re

class Token():
    def __init__(self, type, value):
        self.type: str = type
        self.value: int = value

    def __str__(self):
        return f"({self.value},{self.type})"
    
    def __repr__(self):
        return self.__str__()

class Prepro():
    def filter(string: str) -> str:
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
        # print(self.actual)
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

    def dump_tokens(self):
        curr_token = self.actual
        while curr_token.type != "EOF":
            print(curr_token)
            curr_token = self._advance()


class Parser():
    tokens: Tokenizer

    def parseExpression():
        if Parser.tokens.actual.type != "INT":
            raise SyntaxError("Must begin sequence with integer")
        result = Parser.parseTerm()
        operation = Parser.tokens.actual
        while operation.type == "PLUS" or operation.type == "MINUS":
            next_token = Parser.tokens.selectNext()
            if next_token.type != "INT":
                raise SyntaxError("Expected integer")
            if operation.type == "PLUS":
                result = result + Parser.parseTerm()
            elif operation.type == "MINUS":
                result = result - Parser.parseTerm()
            operation = Parser.tokens.actual
            if operation.type == "INT":
                raise SyntaxError("Expected valid operation, instead got integer")
        return result

    def parseTerm():
        if Parser.tokens.actual.type != "INT":
            raise SyntaxError("Expected integer")
        result = Parser.tokens.actual.value
        print(f"Parse term {result=}")
        operation = Parser.tokens.selectNext()
        while operation.type == "MULT" or operation.type == "DIV":
            next_token = Parser.tokens.selectNext()
            if next_token.type != "INT":
                raise SyntaxError("Expected integer")
            if operation.type == "MULT":
                result = result * next_token.value
            elif operation.type == "DIV":
                result = result // next_token.value
            operation = Parser.tokens.selectNext()
            if operation.type == "INT":
                raise SyntaxError("Expected valid operation, instead got integer")
        return result

    def run(source: str):
        ## Inicializa Tokenizer, roda Parser, retorna parseExpression()
        Parser.tokens = Tokenizer(source)
        return Parser.parseExpression()
    
    def debug_run(source: str):
        Parser.tokens = Tokenizer(source)
        return Parser.tokens.dump_tokens()

def main(argv: list, argc: int):
    if argc < 2:
        print("Send more args plz")
        return 1
    _ = Parser()
    _ = Prepro()

    Parser.debug_run(Prepro.filter(argv[1]))
    print(Parser.run(Prepro.filter(argv[1])))
    return 0

if __name__ == "__main__":
    exit(main(sys.argv, len(sys.argv)))