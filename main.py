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
        # print("AVANCEI TOKEN ", self.actual)
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
        elif self.origin[self.position] == "(":
            token = Token("OP", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == ")":
            token = Token("CP", self.origin[self.position])
            self.position += 1
        elif (re.match("[0-9]|\s", self.origin[self.position]) != None):
            # Acumulate number by concat
            acum = ""
            # If is not digit, advance 
            while not (re.match("[0-9]+", self.origin[self.position:]) != None): 
                self.position+=1
                # Recursiveness re-checks previous cases
                return self._advance()
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
        # print(Parser.tokens.actual , " EXPRESSION")
        result = Parser.parseTerm()
        operation = Parser.tokens.actual
        while operation.type == "PLUS" or operation.type == "MINUS":
            Parser.tokens.selectNext()
            if operation.type == "PLUS":
                result = result + Parser.parseTerm()
            elif operation.type == "MINUS":
                result = result - Parser.parseTerm()
            operation = Parser.tokens.actual
            if operation.type == "INT":
                raise SyntaxError("Expected valid operation, instead got integer")
        return result

    def parseTerm():
        # print(Parser.tokens.actual , " TERM")
        result = Parser.parseFactor()
        operation = Parser.tokens.actual
        if operation.type == "INT":
            raise SyntaxError("Expected valid operation, instead got integer")
        while operation.type == "MULT" or operation.type == "DIV":
            Parser.tokens.selectNext()
            if operation.type == "MULT":
                result = result * Parser.parseFactor()
                operation = Parser.tokens.actual
            elif operation.type == "DIV":
                result = result // Parser.parseFactor()
                operation = Parser.tokens.actual
            # operation = Parser.tokens.selectNext()
            # if operation.type == "INT":
            #     raise SyntaxError("Expected valid operation, instead got integer")
        # print(f"Term {result=}")
        return result

    def parseFactor():
        # print(Parser.tokens.actual , " FACTOR")
        operation = Parser.tokens.actual
        if operation.type == "INT":
            Parser.tokens.selectNext()
            return operation.value
        elif operation.type == "PLUS":
            Parser.tokens.selectNext()
            return Parser.parseFactor()
        elif operation.type == "MINUS":
            Parser.tokens.selectNext()
            return -Parser.parseFactor()
        elif operation.type == "OP":
            Parser.tokens.selectNext()
            result = Parser.parseExpression()
            if Parser.tokens.actual.type == "CP":
                Parser.tokens.selectNext()
                return result
            else:
                raise SyntaxError("Failed to close parentheses")
        else:
            raise SyntaxError("Expected INT, +, -, or parentheses")

    def run(source: str):
        ## Inicializa Tokenizer, roda Parser, retorna parseExpression()
        Parser.tokens = Tokenizer(source)
        result = Parser.parseExpression()
        if Parser.tokens.actual.type != "EOF":
            raise SyntaxError("Failed to reach EOF")
        return result
    
    def debug_run(source: str):
        Parser.tokens = Tokenizer(source)
        return Parser.tokens.dump_tokens()

def main(argv: list, argc: int):
    if argc < 2:
        print("Send more args plz")
        return 1
    _ = Parser()
    _ = Prepro()

    # Parser.debug_run(Prepro.filter(argv[1]))
    print(Parser.run(Prepro.filter(argv[1])))
    return 0

if __name__ == "__main__":
    exit(main(sys.argv, len(sys.argv)))