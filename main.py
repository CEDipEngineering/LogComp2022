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
        symbols = ['+', '-']
        running = True
        while running:
            # print(input)
            if len(input) == 0 or ('+' not in input and '-' not in input):
                running = False
                raise ValueError
            a_str = ''
            b_str = ''
            a = 0
            b = 0
            i=0
            while input[i] not in symbols:
                i+=1
            a_str = input[0:i]
            j = i+1
            while j<len(input) and input[j] not in symbols:
                j+=1
            b_str = input[i+1:j]
            a_str = a_str.replace(" ", "")
            b_str = b_str.replace(" ", "")
            a = int(a_str)
            b = int(b_str)
            # print(a_str)
            # print(input[i])
            # print(b_str)
            if input[i] == '+':
                input = input.replace(input[0:j], str(a + b),1)
            elif input[i] == '-':   
                input = input.replace(input[0:j], str(a - b),1)
            if len(input) == 0 or ('+' not in input and '-' not in input) or input.startswith('-'):
                running = False
        return input

    def main(self, input: string):
        preprocessed = self.preprocess(input)
        lexiconized = self.lexicon(preprocessed)
        sintaxed = self.sintax(lexiconized)
        return self.semantics(sintaxed)



if __name__ == "__main__":
    compiler = Compiler()
    if len(sys.argv) < 2:
        print("Send more args plz")
        exit(1)
    # print("Compiling...")
    print(compiler.main(sys.argv[1]))
    exit(0)
    