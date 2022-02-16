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
        # match_dict = {}
        # i = 0
        # for char in input:
        #     if char in symbols:
        #         match_dict[i] = char
        #     i+=1
        # n=len(match_dict.keys())
        # j = 0
        # while j<n-1:
        #     print(input[match_dict[j]:match_dict[j+1]])
        #     j+=1
        # print(match_dict) 
        # 
        running = True
        while running:
            if len(input) == 0 or ('+' not in input and '-' not in input):
                running = False
                raise ValueError
                continue
            curr_op = None
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
            try:
                a = int(a_str)
                b = int(b_str)
            except ValueError:
                print("Invalid string input, try again!")
                return ""
            # print(a_str)
            # print(input[i])
            # print(b_str)
            if input[i] == '+':
                input = input.replace(input[0:j], str(a + b),1)
            elif input[i] == '-':   
                input = input.replace(input[0:j], str(a - b),1)
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
    