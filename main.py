import string
import sys
import re


class Compiler:

    def __init__(self):
        pass

    def preprocess(self, input: string)->string:
        return input

    def lexicon(self, input: string)->list:
        return input

    def sintax(self, input: list)->string:      
        return input
    
    def semantics(self, input: string)->string:
        
        p = [m.start() for m in re.finditer('+', input) if '+' in input] 
        m = [m.start() for m in re.finditer('-', input) if '+' in input]
        calc = sorted(p+m)    
        print(calc)
        
        
        return input

    def main(self, input: string):
        preprocessed = self.preprocess(input)
        lexiconized = self.lexicon(preprocessed)
        sintaxed = self.sintax(lexiconized)
        return self.semantics(sintaxed)



if __name__ == "__main__":
    compiler = Compiler()
    print(compiler.main('1+1+2+3'))
    if len(sys.argv) < 2:
        print("Send more args plz")
        exit(1)
    print("Compiling...")
    #print(compiler.main(sys.argv[1]))
    exit(0)
    