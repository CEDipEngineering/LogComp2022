import sys
import re
from typing import List

class SymbolTable():
    def __init__(self):
        self._table = {}
        self._reservedWords = ['printf', 'while', 'if', 'else', 'scanf', 'return']
        self.varCount = -4

    def isReserved(self, name):
        return name in self._reservedWords

    def declare(self, name, typ, offset = 0):
        if name in self._table.keys():
            raise Exception(f"Variable {name} already declared")
        FileWriter.write('PUSH DWORD 0 ; Declare {0}'.format(name))
        if offset != 0:
            self._table[name] = (None, typ, self.varCount + offset)
            # print(self._table[name])
        else:
            self._table[name] = (None, typ, self.varCount)
            self.varCount -= 4
        
    def assign(self, name, value):
        if name not in self._table.keys():
            raise Exception(f"Local variable {name} assigned before declaration")
        offset = self._table[name][2]
        # print(offset)
        if offset > 0:
            FileWriter.write('MOV [EBP+{0}], EBX ; {2} = {1}'.format(offset, "some value", name))
        else:
            FileWriter.write('MOV [EBP{0}], EBX ; {2} = {1}'.format(offset, "some value", name))
        self._table[name] = (None, int, self._table[name][2])

    def retrieve(self, name):
        try:
            var = self._table[name]
            if var[2] > 0:
                FileWriter.write('MOV EBX, [EBP+{0}] ; Retrieve variable {1} from memory'.format(var[2], name))
            else: 
                FileWriter.write('MOV EBX, [EBP{0}] ; Retrieve variable {1} from memory'.format(var[2], name))
            return var
        except Exception:
            raise NameError("Variable '{0}' referenced before assignment".format(name))
    
    def __str__(self) -> str:
        out = "Symbol Table: \n"
        for k, v in self._table.items():
            out += f"{k} : {v}\n"
        return out

    def __repr__(self):
        return str(self)

class FuncTable():
    table = {}

    def declare( name, ref, ST):
        '''
        At the start of asm_template _start: we do push ebp, mov ebp, esp
        Is this to emulate main? Yes

        The process of declaring a function in 32bit x86 assembly follows the steps:
        1. PUSH EBP ; Stores the current base pointer
        2. MOV EBP, ESP ; Moves the stack to the new base pointer (essentially creating the local scope)
        3. SUB ESP, n ; Where n is the number of bytes you must use to accomodate all the variables declared, for 5 integers, n would be 5*4, or 20
        # Not sure # 4. PUSH EBX ; Push registers the function will need to modify, one for each argument, essentially
        5. Declare to symbol table all variables used  starting at +8, going up by 4
        6. Execute function block (generate assembly)
        # Undo step 4 backwards # 7. POP EBX ; Restore values to registers
        8. MOV ESP, EBP ; Destroy local scope
        9. POP EBP ; Restore base pointer
        10. RET
        '''
        if name in FuncTable.table.keys():
            raise Exception(f"Function {name} already declared")
        FuncTable.table[name] = ref
        FileWriter.write("; {0}".format(name))
        FileWriter.write("{0}:\n".format(name))
        FileWriter.write("PUSH EBP ; Store base pointer")
        FileWriter.write("MOV EBP, ESP ; Relocate base pointer to new stack top")

        # Technically dont need to, because will do PUSH DWORD 0;
        # num_args = len(ref.children - 2)
        # if num_args > 0:
        #     FileWriter.write("SUB ESP, {0}".format(num_args*4))
        # elif num_args > 3:
        #     raise Exception("Too many arguments! Don't know how many registers I have!")

        ## TODO:
        ## Handle arguments
        args = ref.children[1:-1] # Ignore first and last
        inc = 12
        localScope = SymbolTable()
        if len(args) != 0:
            for c in args:
                c.evaluate(localScope, inc)
                inc+=4
                # print(c)
                

        ref.children[-1].evaluate(localScope) # Write block

        ## TODO:
        ## Pop registers from args

        FileWriter.write("MOV ESP, EBP ; Destroy local scope")
        FileWriter.write("POP EBP ; Restore base pointer")

        FileWriter.write("RET ; Exiting {0}\n".format(name))

    def retrieve( name):
        try:
            return FuncTable.table[name]
        except Exception:
            raise NameError("Function '{0}' referenced but never declared".format(name))

class Token():
    def __init__(self, type, value):
        self.type: str = type
        self.value = value

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

    def isReserved(self, w) -> bool:
        return w in ['printf', 'while', 'if', 'else', 'scanf', 'return']

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
            if self.origin[self.position+1] == '=':
                token = Token("EQUALS", "==")
                self.position += 1
            else:
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
        elif self.origin[self.position] == ">":
            token = Token("GT", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == ".":
            token = Token("CAT", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == ",":
            token = Token("COM", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == '"':
            # String
            acum = ""
            self.position += 1
            while self.origin[self.position] != '"':
                acum += self.origin[self.position]
                self.position += 1
            self.position+=1
            token = Token("STR", acum)
        elif self.origin[self.position] == "<":
            token = Token("LT", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == "!":
            token = Token("NOT", self.origin[self.position])
            self.position += 1
        elif self.origin[self.position] == '&':
            if self.origin[self.position+1] == '&':
                token = Token("AND", "&&")
                self.position += 2
            else:
                raise Exception("LexiconError: Single & not allowed")
        elif self.origin[self.position] == '|':
            if self.origin[self.position+1] == '|':
                token = Token("OR", "||")
                self.position += 2
            else:
                raise Exception("LexiconError: Single | not allowed")
        elif self.origin[self.position].isalpha():
            ident = self.origin[self.position]
            self.position+=1
            while self.origin[self.position].isalpha() or self.origin[self.position].isdigit() or self.origin[self.position] == '_':
                ident+=self.origin[self.position]
                self.position+=1
            if self.isReserved(ident):
                token = Token(ident.upper(), ident) ## Return a token of reserved operation
            elif ident.lower() == "int":
                token = Token("TYPE", ident)
            elif ident.lower() == "str":
                token = Token("TYPE", ident)
            elif ident.lower() == "void":
                token = Token("TYPE", ident)
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
    id = 0
    def newId():
        t = Node.id
        Node.id += 1
        return t

    def __init__(self, value, children: List['Node']):
        self.value = value
        self.children = children
        self.id = Node.newId()

    def evaluate(self, ST: SymbolTable):
        pass

    def __str__(self):
        return "{0}:{1}\n{2}".format(type(self), str(self.value), ''.join(['\t'+str(c)+'\n' for c in self.children]))

    def __repr__(self):
        return self.__str__()

class BinOp(Node):
    def evaluate(self, ST: SymbolTable):
        FileWriter.write('; Evaluating BinOp {0}'.format(self.value))
        if self.value == '+':
            a = self.children[0].evaluate(ST)
            FileWriter.write('PUSH EBX')
            b = self.children[1].evaluate(ST)
            # if a[1] != int or b[1] != int:
            #     raise Exception("Operation + only defined for int and int")
            FileWriter.write('POP EAX')
            FileWriter.write('ADD EAX, EBX')
            FileWriter.write('MOV EBX, EAX')
            # print(a, b)
            # return (a[0] + b[0], int)
        elif self.value == '*':
            a = self.children[0].evaluate(ST)
            FileWriter.write('PUSH EBX')
            b = self.children[1].evaluate(ST)
            # if a[1] != int or b[1] != int:
            #     raise Exception("Operation * only defined for int and int")
            FileWriter.write('POP EAX')
            FileWriter.write('IMUL EBX')
            FileWriter.write('MOV EBX, EAX')
            # return (a[0] * b[0], int)
        elif self.value == '-':
            a = self.children[0].evaluate(ST)
            FileWriter.write('PUSH EBX')
            b = self.children[1].evaluate(ST)
            # if a[1] != int or b[1] != int:
            #     raise Exception("Operation - only defined for int and int")
            FileWriter.write('POP EAX')
            FileWriter.write('SUB EAX, EBX')
            FileWriter.write('MOV EBX, EAX')
            # return (a[0] - b[0], int)
        elif self.value == '/':
            a = self.children[0].evaluate(ST)
            FileWriter.write('PUSH EBX')
            b = self.children[1].evaluate(ST)
            # if a[1] != int or b[1] != int:
            #     raise Exception("Operation / only defined for int and int")
            FileWriter.write('POP EAX')
            FileWriter.write('IDIV EBX')
            FileWriter.write('MOV EBX, EAX')
            # return (a[0] // b[0], int)
        elif self.value == '>':
            a = self.children[0].evaluate(ST)
            FileWriter.write('PUSH EBX')
            b = self.children[1].evaluate(ST)
            # if a[1] != b[1]:
            #     raise Exception("Operation > only defined for two operands of same type")
            FileWriter.write('POP EAX')
            FileWriter.write('CMP EAX, EBX')
            FileWriter.write('CALL binop_jg')
            # FileWriter.write('MOV EBX, EAX')
            # return (a[0] > b[0], int)
        elif self.value == '<':
            a = self.children[0].evaluate(ST)
            FileWriter.write('PUSH EBX')
            b = self.children[1].evaluate(ST)
            # if a[1] != b[1]:
            #     raise Exception("Operation < only defined for two operands of same type")
            FileWriter.write('POP EAX')
            FileWriter.write('CMP EAX, EBX')
            FileWriter.write('CALL binop_jl')
            # FileWriter.write('MOV EBX, EAX')
            # return (a[0] < b[0], int)
        elif self.value == '==':
            a = self.children[0].evaluate(ST)
            FileWriter.write('PUSH EBX')
            b = self.children[1].evaluate(ST)
            # if a[1] != b[1]:
            #     raise Exception("Operation == only defined for two operands of same type")
            FileWriter.write('POP EAX')
            FileWriter.write('CMP EAX, EBX')
            FileWriter.write('CALL binop_je')
            # FileWriter.write('MOV EBX, EAX')
            # return (a[0] == b[0], int)
        elif self.value == '&&':
            a = self.children[0].evaluate(ST)
            FileWriter.write('PUSH EBX')
            b = self.children[1].evaluate(ST)
            # if a[1] != int or b[1] != int:
            #     raise Exception("Operation && only defined for types int and int")
            FileWriter.write('POP EAX')
            FileWriter.write('AND EAX, EBX')
            FileWriter.write('MOV EBX, EAX')
            # return (a[0] and b[0], int)
        elif self.value == '||':
            a = self.children[0].evaluate(ST)
            FileWriter.write('PUSH EBX')
            b = self.children[1].evaluate(ST)
            # if a[1] != int or b[1] != int:
            #     raise Exception("Operation || only defined for types int and int")
            FileWriter.write('POP EAX')
            FileWriter.write('OR EAX, EBX')
            FileWriter.write('MOV EBX, EAX')
            # return (a[0] or b[0], int)
        elif self.value == '.':
        #     a = self.children[0].evaluate(ST)
        #     FileWriter.write('PUSH EBX')
        #     b = self.children[1].evaluate(ST)
        #     FileWriter.write('POP EAX')
        #     FileWriter.write('ADD EAX, EBX')
        #     FileWriter.write('MOV EBX, EAX')
            return (str(a[0]) + str(b[0]), str)
            pass

class UnOp(Node):
    def evaluate(self, ST: SymbolTable):
        if self.value == '+':
            a = self.children[0].evaluate(ST)
            # if a[1] != int:
            #     raise Exception("Unary operator + only valid for integers")
            FileWriter.write('MOV EBX, {0} ; Eval UnOp Node op={1}'.format(a[0], self.value))
            # return (a[0], int)
        elif self.value == '-':
            a = self.children[0].evaluate(ST)
            # if a[1] != int:
            #     raise Exception("Unary operator - only valid for integers")
            FileWriter.write('MOV EBX, {0} ; Eval UnOp Node op={1}'.format(a[0], self.value))
            FileWriter.write('NEG EBX')
            # return (-a[0], int)
        elif self.value == '!':
            a = self.children[0].evaluate(ST)
            # if a[1] != int:
            #     raise Exception("Unary operator 'not' only valid for integers")
            FileWriter.write('MOV EBX, {0} ; Eval UnOp Node op={1}'.format(a[0], self.value))
            FileWriter.write('NOT EBX')
            # return (not a[0], int)
        else:
            raise Exception("Invalid UnOp {0}".format(self.value))

class IntVal(Node):
    def evaluate(self, ST: SymbolTable):
        FileWriter.write('MOV EBX, {0} ; Eval IntVal Node'.format(self.value))
        return (self.value, int)

class StrVal(Node):
    def evaluate(self, ST: SymbolTable):
        return (self.value, str)

class Block(Node):
    def evaluate(self, ST: SymbolTable):
        for f in self.children:
            f.evaluate(ST)
            
class VarDec(Node):
    def evaluate(self, ST: SymbolTable, offset=0):
        [ST.declare(name.value, self.value, offset) for name in self.children]

class Assignment(Node):
    def evaluate(self, ST: SymbolTable):
        ST.assign(self.children[0].value, self.children[1].evaluate(ST))

class Printf(Node):
    def evaluate(self, ST: SymbolTable):
        FileWriter.write('\n; begin print coroutine')
        a = self.children[0].evaluate(ST)
        FileWriter.write('PUSH EBX ; Push args to stack')
        FileWriter.write('CALL print ; Func call')
        FileWriter.write('POP EBX ; Unstack args')
        FileWriter.write('; end print coroutine\n')

class Identifier(Node):
    def evaluate(self, ST: SymbolTable):
        return ST.retrieve(self.value)

class NoOp(Node):
    def evaluate(self, ST: SymbolTable):
        pass

class Scanf(Node):
    def evaluate(self, ST: SymbolTable):
        return (int(input()), int)

class If(Node):
    def evaluate(self, ST: SymbolTable):
        id = self.id
        FileWriter.write('\n; begin if statement')
        FileWriter.write('; evaluate condition {0}'.format(self.children[0].value))
        self.children[0].evaluate(ST)
        FileWriter.write('CMP EBX, False ; if condition is false, jump to else')
        FileWriter.write('JE ELSE_{0}'.format(id))
        FileWriter.write('; if condition is true, evaluate true statement')
        self.children[1].evaluate(ST)
        FileWriter.write('; exit once true statement is done')
        FileWriter.write('JMP EXIT_IF_{0}'.format(id))
        FileWriter.write('ELSE_{0}:'.format(id))
        self.children[2].evaluate(ST)
        FileWriter.write('EXIT_IF_{0}:'.format(id))
        FileWriter.write('; end if statement\n')

class While(Node):
    def evaluate(self, ST: SymbolTable):
        id = self.id
        FileWriter.write('\n; begin while loop')
        FileWriter.write('LOOP_{0}:'.format(id))
        self.children[0].evaluate(ST)
        FileWriter.write('CMP EBX, False ; if condition is false, exit')
        FileWriter.write('JE EXIT_{0}'.format(id))
        self.children[1].evaluate(ST)
        FileWriter.write('JMP LOOP_{0}'.format(id))
        FileWriter.write('EXIT_{0}:'.format(id))

class FuncDec(Node):
    def evaluate(self, ST: SymbolTable):
        # print(FuncTable.table)
        FuncTable.declare(self.value, self, ST)

class BeginProg(Node):
    def evaluate(self, ST: SymbolTable):
        FileWriter.write("\nPUSH EBP ; Store base pointer\nMOV EBP, ESP ; Relocate base pointer to new stack top\n_start:\n\n")

class FuncCall(Node):
    def evaluate(self, ST: SymbolTable):
        function = FuncTable.retrieve(self.value)
        localScope = SymbolTable()
        varNames = []
        # print(ST)
        
        ## TODO:
        ## Handle arguments


        if len(self.children) > 0:
            for c in reversed(self.children):
                c.evaluate(ST)
                FileWriter.write("PUSH EBX ; Evaluating args in func call \n")

        # for c in function.children[1:-1]: # Skip first and last child
        #     c.evaluate(localScope)
        #     varNames.append(c.children[0].value)
        # # print("VarNames: {0}".format(varNames))
        # for exp, name in zip(self.children, varNames):
        #     localScope.assign(name, exp.evaluate(ST))
        # retVal = function.children[-1].evaluate(localScope)
        # if retVal is function.children[0].value:
            # print("Return do tipo certo")
        # if type(retVal[0]) != function.children[0].value:
        #     raise Exception("Function {0} was expected to return a {1}, but returned {2} instead".format(self.value, function.children[0].value, type(retVal)))
        
        FileWriter.write("CALL {0}".format(self.value))
        FileWriter.write("MOV EBX, EAX ; Output should be EBX, but EAX is RET default")
        
        return  # retVal

class Return(Node):
    def evaluate(self, ST: SymbolTable):
        val = self.children[0].evaluate(ST)
        FileWriter.write("MOV EAX, EBX ; Moving evaluate children return to EAX")
        return val

class Parser():
    tokens: Tokenizer

    def parseProgram():
        decs = []
        while Parser.tokens.actual.type != "EOF":
            decs.append(Parser.parseDeclaration())
        return Block("GRAN BLOCO", decs)

    def parseDeclaration():
        nodes = []
        if Parser.tokens.actual.type != "TYPE":
            raise Exception("Function declarations must begin with output type specification")
        funcType = Parser.tokens.actual.value # Save func type
        Parser.tokens.selectNext()
        if Parser.tokens.actual.type != "IDENT":
            raise Exception("Function declarations must include a valid name identifier")
        funcName = Parser.tokens.actual.value # Save func name
        Parser.tokens.selectNext()
        if Parser.tokens.actual.type != "OP":
            raise Exception("Function declarations must open parentheses after name identifier")
        Parser.tokens.selectNext()
        if funcType == 'str':
            nodes.append(VarDec(str, [Identifier(funcName, [])]))
        elif funcType == 'int':
            nodes.append(VarDec(int, [Identifier(funcName, [])]))
        elif funcType == 'void':
            nodes.append(VarDec(None, [Identifier(funcName, [])]))
        else:
            # Should never happen
            raise Exception("Unknown type used")
        # Process arguments
        if Parser.tokens.actual.type == "CP":
            Parser.tokens.selectNext()
            nodes.append(Parser.parseBlock())
        elif Parser.tokens.actual.type == "TYPE":
            tip = Parser.tokens.actual.value # Store arg type
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type != "IDENT":
                raise Exception("Type must be followed by valid identifier name in functiona argument declaration")
            name = Parser.tokens.actual.value # Store arg name
            Parser.tokens.selectNext()
            if tip == 'int':
                nodes.append(VarDec(int, [Identifier(name, [])]))
            elif tip == 'str':
                nodes.append(VarDec(str, [Identifier(name, [])]))
            else:
                raise Exception("Argument must have type string or integer")
            while Parser.tokens.actual.type != "CP":
                if Parser.tokens.actual.type != "COM":
                    raise Exception("Arguments in function declaration must be separated by comma")
                Parser.tokens.selectNext()
                if Parser.tokens.actual.type != "TYPE":
                    raise Exception("Invalid argument declaration syntax")
                tip = Parser.tokens.actual.value # Store arg type
                Parser.tokens.selectNext()
                if Parser.tokens.actual.type != "IDENT":
                    raise Exception("Type must be followed by valid identifier name in functiona argument declaration")
                name = Parser.tokens.actual.value # Store arg name
                Parser.tokens.selectNext()
                if tip == 'int':
                    nodes.append(VarDec(int, [Identifier(name, [])]))
                elif tip == 'str':
                    nodes.append(VarDec(str, [Identifier(name, [])]))
            Parser.tokens.selectNext() # Consume CP
            nodes.append(Parser.parseBlock())
        else:
            raise Exception("Invalid argument declaration syntax")  
        return FuncDec(funcName, nodes)

    def parseRelExpr():
        node = Parser.parseExpression()
        operation = Parser.tokens.actual
        while operation.type == "EQUALS" or operation.type == "LT" or operation.type == "GT":
            Parser.tokens.selectNext()
            if operation.type == "EQUALS":
                node = BinOp(value='==', children=[node, Parser.parseExpression()])
            elif operation.type == "LT":
                node = BinOp(value='<', children=[node, Parser.parseExpression()])
            elif operation.type == "GT":
                node = BinOp(value='>', children=[node, Parser.parseExpression()])
            operation = Parser.tokens.actual
            if operation.type == "INT":
                raise SyntaxError("Expected valid operation, instead got integer")
        return node

    def parseExpression():
        # print(Parser.tokens.actual , " EXPRESSION")
        node = Parser.parseTerm()
        operation = Parser.tokens.actual
        while operation.type == "PLUS" or operation.type == "MINUS" or operation.type == "OR" or operation.type == "CAT":
            Parser.tokens.selectNext()
            if operation.type == "PLUS":
                node = BinOp(value='+', children=[node, Parser.parseTerm()])
            elif operation.type == "MINUS":
                node = BinOp(value='-', children=[node, Parser.parseTerm()])
            elif operation.type == "OR":
                node = BinOp(value='||', children=[node, Parser.parseTerm()])
            elif operation.type == "CAT":
                node = BinOp(value='.', children=[node, Parser.parseTerm()])
            operation = Parser.tokens.actual
        # print(f"Expr return {node=}")
        return node

    def parseTerm():
        node = Parser.parseFactor()
        operation = Parser.tokens.actual
        if operation.type == "INT":
            raise SyntaxError("Expected valid operation, instead got integer")
        while operation.type == "MULT" or operation.type == "DIV" or operation.type == "AND":
            Parser.tokens.selectNext()
            if operation.type == "MULT":
                node = BinOp(value='*', children=[node, Parser.parseFactor()])
                operation = Parser.tokens.actual
            elif operation.type == "DIV":
                node = BinOp(value='/', children=[node, Parser.parseFactor()])
                operation = Parser.tokens.actual
            elif operation.type == "AND":
                node = BinOp(value='&&', children=[node, Parser.parseFactor()])
                operation = Parser.tokens.actual
            
            # operation = Parser.tokens.selectNext()
            # if operation.type == "INT":
            #     raise SyntaxError("Expected valid operation, instead got integer")
        # print(f"Term {node=}")
        return node

    def parseFactor():
        # print(Parser.tokens.actual , " FACTOR")
        if Parser.tokens.actual.type == "INT":
            val = Parser.tokens.actual.value
            Parser.tokens.selectNext()
            return IntVal(value=val, children=[])
        if Parser.tokens.actual.type == "STR":
            val = Parser.tokens.actual.value
            Parser.tokens.selectNext()
            return StrVal(value=val, children=[])
        if Parser.tokens.actual.type == "IDENT":
            ident_name = Parser.tokens.actual.value
            Parser.tokens.selectNext()
            # print("Factor ident token={0}".format(Parser.tokens.actual))
            if Parser.tokens.actual.type == "OP":
                Parser.tokens.selectNext()
                funcCallExprs = []
                if Parser.tokens.actual.type == "CP":
                    Parser.tokens.selectNext()
                else:
                    funcCallExprs.append(Parser.parseRelExpr())
                    while Parser.tokens.actual.type != "CP":
                        if Parser.tokens.actual.type != "COM":
                            raise Exception("Arguments in function call must be separated by comma")
                        Parser.tokens.selectNext()
                        funcCallExprs.append(Parser.parseRelExpr())
                    Parser.tokens.selectNext()
                # print(ident_name)
                return FuncCall(ident_name, funcCallExprs)
            return Identifier(value=ident_name, children=[])
        if Parser.tokens.actual.type == "SCANF":
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type != "OP":
                raise Exception("Scanf function call requires open parentheses")
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type != "CP":
                raise Exception("Scanf function call requires open and close parentheses")
            Parser.tokens.selectNext()
            return Scanf(value=Parser.tokens.actual.value, children=[])
        if Parser.tokens.actual.type == "PLUS":
            Parser.tokens.selectNext()
            return UnOp(value='+', children=[Parser.parseFactor()])
        if Parser.tokens.actual.type == "MINUS":
            Parser.tokens.selectNext()
            return UnOp(value='-', children=[Parser.parseFactor()])
        if Parser.tokens.actual.type == "NOT":
            Parser.tokens.selectNext()
            return UnOp(value='!', children=[Parser.parseFactor()])
        if Parser.tokens.actual.type == "OP":
            Parser.tokens.selectNext()
            node = Parser.parseRelExpr()
            if Parser.tokens.actual.type == "CP":
                Parser.tokens.selectNext()
                return node
            else:
                raise SyntaxError("Failed to close parentheses")
        raise SyntaxError("Factor malformed")

    def parseBlock():
        if Parser.tokens.actual.type == "OCB":
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type == "CCB":
                Parser.tokens.selectNext()
                return Block("EL BLOCO", [])
            opList = []
            while Parser.tokens.actual.type != "CCB":
                opList.append(Parser.parseStatement())
            Parser.tokens.selectNext() # Consume CCB
            return Block("EL BLOCO", opList)
        else:
            raise Exception("Missing block opener {")

    def parseStatement():
        needs_semi_col = False
        if Parser.tokens.actual.type == "SEMICOL":
            Parser.tokens.selectNext()
            return NoOp(None, [])
        elif Parser.tokens.actual.type == "IDENT":
            ident_name = Parser.tokens.actual.value
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type == "OP":
                Parser.tokens.selectNext()
                funcCallExprs = []
                needs_semi_col = True
                if Parser.tokens.actual.type == "CP":
                    Parser.tokens.selectNext()
                else:
                    funcCallExprs.append(Parser.parseRelExpr())
                    while Parser.tokens.actual.type != "CP":
                        if Parser.tokens.actual.type != "COM":
                            raise Exception("Arguments in function call must be separated by comma")
                        Parser.tokens.selectNext()
                        funcCallExprs.append(Parser.parseRelExpr())
                    Parser.tokens.selectNext()
                node = FuncCall(ident_name, funcCallExprs)
            elif Parser.tokens.actual.type == 'ASSIGN':
                Parser.tokens.selectNext()
                node = Assignment("=", [Identifier(ident_name,[]), Parser.parseRelExpr()])
                needs_semi_col = True
            else:
                raise SyntaxError("Invalid solitary identifier encountered {0}".format(ident_name))
        elif Parser.tokens.actual.type == "TYPE":
            # print(Parser.tokens.actual)
            curr_token = Parser.tokens.actual
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type != 'IDENT':
                raise SyntaxError("Type declaration must be followed by valid identifier, instead got {0}".format(curr_token.value))
            opList = [Identifier(Parser.tokens.actual.value, [])]
            Parser.tokens.selectNext()
            while Parser.tokens.actual.type != "SEMICOL":
                if Parser.tokens.actual.type != "COM":
                    raise Exception("Type declaration must be list of identifiers separated by commas")
                Parser.tokens.selectNext()
                opList.append(Identifier(Parser.tokens.actual.value, []))
                Parser.tokens.selectNext()
            if curr_token.value.lower() == 'int':
                node = VarDec(int, opList)
            elif curr_token.value.lower() == 'str':
                node = VarDec(str, opList)
            else:
                raise Exception("Undefined type declaration")
            needs_semi_col = True
        elif Parser.tokens.actual.type == "PRINTF":
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type != "OP":
                raise SyntaxError("Function call must contain arguments between paretheses")
            Parser.tokens.selectNext()
            node = Printf('Printf', [Parser.parseRelExpr()])
            if Parser.tokens.actual.type != "CP":
                raise SyntaxError("Function call must contain arguments between paretheses")
            Parser.tokens.selectNext()
            needs_semi_col = True
        elif Parser.tokens.actual.type == "RETURN":
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type == "SEMICOL":
                Parser.tokens.selectNext()
                node = Return('Return', [NoOp('nop', [])])
            else:
                if Parser.tokens.actual.type != "OP":
                    raise SyntaxError("Function call must contain arguments between paretheses")
                Parser.tokens.selectNext()
                node = Return('Return', [Parser.parseRelExpr()])
                if Parser.tokens.actual.type != "CP":
                    raise SyntaxError("Function call must contain arguments between paretheses")
                Parser.tokens.selectNext()
                needs_semi_col = True
        elif Parser.tokens.actual.type == "OCB":
            node = Parser.parseBlock()
        elif Parser.tokens.actual.type == "WHILE":
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type != "OP":
                raise SyntaxError ("while clause must be followed by parentheses")
            Parser.tokens.selectNext()
            relexp = Parser.parseRelExpr()
            if Parser.tokens.actual.type != "CP":
                raise SyntaxError ("while clause unclosed parentheses")
            Parser.tokens.selectNext()
            node = While(value="While", children=[relexp, Parser.parseStatement()])
        elif Parser.tokens.actual.type == "IF":
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type != "OP":
                raise SyntaxError ("If clause must be followed by parentheses")
            Parser.tokens.selectNext()
            relexp = Parser.parseRelExpr()
            if Parser.tokens.actual.type != "CP":
                raise SyntaxError ("If clause unclosed parentheses")
            Parser.tokens.selectNext()
            content = Parser.parseStatement()
            # print(Parser.tokens.actual)
            if Parser.tokens.actual.type == "ELSE":
                Parser.tokens.selectNext()
                elsestmt = Parser.parseStatement()
            else:
                elsestmt = NoOp(None, [])
            node = If(value="If", children=[relexp, content, elsestmt])
        # print(f"Statement node {node}")
        if needs_semi_col:
            if Parser.tokens.actual.type != "SEMICOL":
                raise SyntaxError("Expected ; end of statement")
            Parser.tokens.selectNext()
        # print(Parser.tokens.actual)
        # print(node)
        return node

    def run(source: str):
        ## Inicializa Tokenizer, roda Parser, retorna parseExpression()
        Parser.tokens = Tokenizer(source)
        result = Parser.parseProgram()
        if Parser.tokens.actual.type != "EOF":
            raise SyntaxError("Failed to reach EOF")
        return result
    
    def debug_run(source: str):
        Parser.tokens = Tokenizer(source)
        return Parser.tokens.dump_tokens()

class FileWriter():
    fn: str
    out_s: str

    def __init__(fn) -> None:
        FileWriter.fn = fn 
        with open('./asm_template.txt', 'r') as f:
            FileWriter.out_s = f.read()

    def write(line: str):
        FileWriter.out_s += line + '\n'

    def dump():
        with open(FileWriter.fn, 'w') as f:
            f.write(FileWriter.out_s + '\n\n; interrupcao de saida\nPOP EBP\nMOV EAX, 1\nINT 0x80\n')

def main(argv: list, argc: int):
    if argc < 2:
        print("Send more args plz")
        return 1

    _ = Parser()
    _ = Prepro()
    _ = FuncTable()

    try:
        if not argv[1].endswith('.c'):
            raise Exception("Provided path to file must end with '.c'")
        with open(argv[1], 'r') as f:
            word = f.read()
    except FileNotFoundError:
        print("vish, nn achei esse arquivo nn :(")
        raise FileNotFoundError

    _ = FileWriter()
    FileWriter.fn = argv[1][:-2] + '.asm'
    # Parser.debug_run(Prepro.filter(word)) # Will dump all tokens for debugging
    root = Parser.run(Prepro.filter(word))
    root.children.append(BeginProg('',[])) # Write start_ flag
    root.children.append(FuncCall('main', [])) # Add call to main
    # print(root)
    ST = SymbolTable()
    root.evaluate(ST)
    FileWriter.dump()
    return 0

if __name__ == "__main__":
    exit(main(sys.argv, len(sys.argv)))