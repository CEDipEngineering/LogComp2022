from plistlib import InvalidFileException
import string
import sys
import re
from typing import List

from pyparsing import ParseExpression

class SymbolTable():
    def __init__(self):
        self._table = {}
        self._reservedWords = ['printf']

    def isReserved(self, word):
        return word in self._reservedWords

    def assign(self, name, value):
        self._table[name] = value

    def retrieve(self, name):
        try:
            return self._table[name]
        except Exception:
            raise NameError("Variable '{0}' referenced before assignment".format(name))

ST = SymbolTable()

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
        elif self.origin[self.position] == '=':
            token = Token("ASSIGN", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == "{":
            token = Token("OCB", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == "}":
            token = Token("CCB", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == ";":
            token = Token("SEMICOL", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position].isalpha():
            ident = self.origin[self.position]
            self.position+=1
            while self.origin[self.position].isalpha() or self.origin[self.position].isdigit() or self.origin[self.position] == '_':
                ident+=self.origin[self.position]
                self.position+=1
            if ST.isReserved(ident):
                token = Token("PRINTF", ident)
            else:
                token = Token("IDENT", ident)
        elif (re.match("[0-9]|\s|\n", self.origin[self.position]) != None):
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

class Node:
    def __init__(self, value, children: List['Node']):
        self.value = value
        self.children = children

    def evaluate(self):
        pass

    def __str__(self):
        return f'Node({self.value})=>[{" ".join([str(n) for n in self.children])}]'

    def __repr__(self):
        return self.__str__()

class BinOp(Node):
    def evaluate(self):
        if self.value == '+':
            return self.children[0].evaluate() + self.children[1].evaluate()
        elif self.value == '*':
            return self.children[0].evaluate() * self.children[1].evaluate()
        elif self.value == '-':
            return self.children[0].evaluate() - self.children[1].evaluate()
        elif self.value == '/':
            return self.children[0].evaluate() // self.children[1].evaluate()

class UnOp(Node):
    def evaluate(self):
        if self.value == '+':
            return self.children[0].evaluate()
        elif self.value == '-':
            return -self.children[0].evaluate()

class IntVal(Node):
    def evaluate(self):
        return self.value

class Block(Node):
    def evaluate(self):
        [f.evaluate() for f in self.children]

class Assignment(Node):
    def evaluate(self):
        ST.assign(self.children[0].value, self.children[1].evaluate())

class Printf(Node):
    def evaluate(self):
        print(self.children[0].evaluate())

class Identifier(Node):
    def evaluate(self):
        return ST.retrieve(self.value)

class NoOp(Node):
    def evaluate(self):
        pass

class Parser():
    tokens: Tokenizer

    def parseExpression():
        # print(Parser.tokens.actual , " EXPRESSION")
        node = Parser.parseTerm()
        operation = Parser.tokens.actual
        while operation.type == "PLUS" or operation.type == "MINUS":
            Parser.tokens.selectNext()
            if operation.type == "PLUS":
                node = BinOp(value='+', children=[node, Parser.parseTerm()])
            elif operation.type == "MINUS":
                node = BinOp(value='-', children=[node, Parser.parseTerm()])
            operation = Parser.tokens.actual
            if operation.type == "INT":
                raise SyntaxError("Expected valid operation, instead got integer")
        return node

    def parseTerm():
        node = Parser.parseFactor()
        operation = Parser.tokens.actual
        if operation.type == "INT":
            raise SyntaxError("Expected valid operation, instead got integer")
        while operation.type == "MULT" or operation.type == "DIV":
            Parser.tokens.selectNext()
            if operation.type == "MULT":
                node = BinOp(value='*', children=[node, Parser.parseFactor()])
                operation = Parser.tokens.actual
            elif operation.type == "DIV":
                node = BinOp(value='/', children=[node, Parser.parseFactor()])
                operation = Parser.tokens.actual
            # operation = Parser.tokens.selectNext()
            # if operation.type == "INT":
            #     raise SyntaxError("Expected valid operation, instead got integer")
        # print(f"Term {node=}")
        return node

    def parseFactor():
        # print(Parser.tokens.actual , " FACTOR")
        operation = Parser.tokens.actual
        if operation.type == "INT":
            Parser.tokens.selectNext()
            return IntVal(value=operation.value, children=[])
        elif operation.type == "IDENT":
            Parser.tokens.selectNext()
            return Identifier(value=operation.value, children=[])
        elif operation.type == "PLUS":
            Parser.tokens.selectNext()
            return UnOp(value='+', children=[Parser.parseFactor()])
        elif operation.type == "MINUS":
            Parser.tokens.selectNext()
            return UnOp(value='-', children=[Parser.parseFactor()])
        elif operation.type == "OP":
            Parser.tokens.selectNext()
            node = Parser.parseExpression()
            if Parser.tokens.actual.type == "CP":
                Parser.tokens.selectNext()
                return node
            else:
                raise SyntaxError("Failed to close parentheses")
        else:
            raise SyntaxError("Expected INT, +, -, or parentheses")

    def parseBlock():
        if Parser.tokens.actual.type == "OCB":
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type == "CCB":
                return Block("EL BLOCO", [])
            opList = []
            while Parser.tokens.actual.type != "CCB":
                opList.append(Parser.parseStatement())
            Parser.tokens.selectNext() # Consume CCB
            return Block("EL BLOCO", opList)
        else:
            raise Exception("Missing block opener {")

    def parseStatement():
        if Parser.tokens.actual.type == "SEMICOL":
            return NoOp(None, [])
        elif Parser.tokens.actual.type == "IDENT":
            curr_token = Parser.tokens.actual
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type != 'ASSIGN':
                raise SyntaxError("Invalid solitary identifier encountered {0}".format(curr_token.value))
            Parser.tokens.selectNext()
            node = Assignment("=", [Identifier(curr_token.value,[]), Parser.parseExpression()])
        elif Parser.tokens.actual.type == "PRINTF":
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type != "OP":
                raise SyntaxError("Function call must contain arguments between paretheses")
            Parser.tokens.selectNext()
            node = Printf('Printf', [Parser.parseExpression()])
            if Parser.tokens.actual.type != "CP":
                raise SyntaxError("Function call must contain arguments between paretheses")
            Parser.tokens.selectNext()
        if Parser.tokens.actual.type != "SEMICOL":
            raise SyntaxError("Expected ; end of statement")
        Parser.tokens.selectNext()
        return node

    def run(source: str):
        ## Inicializa Tokenizer, roda Parser, retorna parseExpression()
        Parser.tokens = Tokenizer(source)
        result = Parser.parseBlock()
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
    try:
        if not argv[1].endswith('.c'):
            raise InvalidFileException("Message must be of type '.c'")
        with open(argv[1], 'r') as f:
            word = f.read()
    except FileNotFoundError:
        print("vish, nn achei esse arquivo nn :(")
        raise FileNotFoundError
    root = Parser.run(Prepro.filter(word))
    root.evaluate()
    # Parser.debug_run(Prepro.filter(word)) # Will dump all tokens for debugging
    return 0

if __name__ == "__main__":
    exit(main(sys.argv, len(sys.argv)))