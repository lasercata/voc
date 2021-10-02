#!/bin/python3
# -*- coding: utf-8 -*-

#--------------------------------------------------
#
# Author    :   Lasercata
# Date      :   2021.10.02
version = '1.3.1'
#
#--------------------------------------------------

# Todo :
    # Do score for words, to show them with a higher probability next time, or more often ;
    # Maybe a QCM ;
    # Analyse answer (to not set wrong if there is an error while typing) ;

##-import
from random import shuffle
from ast import literal_eval

from datetime import datetime as dt
from time import sleep

from os.path import isfile
import sys

#------For parser
import argparse

##-Useful functions
def set_dict(dct):
    '''
    Return a string representing the dict, with line by line key-value.
    Usefull to set readable dict in your programs
    '''

    ret = '{'

    for k in dct:
        ret += '\n\t{}: {},'.format(set_str(k), set_str(dct[k]))

    ret = ret[:-1] + '\n}'

    return ret


def set_str(obj):
    if type(obj) == str:
        return "'{}'".format(obj)

    return '{}'.format(obj)


def set_good_len(word, mx, opposite=False):
    '''return word formated to have length of mx'''
    
    while len(word) < mx:
        if opposite:
            word = ' ' + word
        
        else:
            word += ' '
    
    return word


class VocFile:
    '''Class managing the voc files'''
    
    def __init__(self, fn):
        '''Initiate obj'''
        
        #if fn[-4:] != '.txt':
            #fn += '.txt'
        
        self.fn = fn
    
    
    def read(self):
        '''Return the dict in self.fn'''
        
        if not isfile(self.fn):
            raise ValueError(f"Voc: cannot access '{self.fn}': No such file")
        
        with open(self.fn, 'r') as f:
            d_str = f.read()
        
        return literal_eval(d_str)
    
    
    def _get_dct(self, sep=','):
        d = {}
        i = 0

        print('Type <ctrl> + C to quit.')

        while True:
            try:
                d[i] = tuple(input(f'Words (fra,[lang]), separeted by "{sep}" :').split(sep))
                
                for k in d[i]:
                    d[i][k] = d[i][k].strip(' ') #remove the spaces at the begin and at the end of the words

                i += 1

            except KeyboardInterrupt:
                break

        return d
    
    
    def _write(self, d):
        '''Write `d` in the file.'''
        
        d_str = set_dict(d) + '\n'
        
        with open(self.fn, 'w') as f:
            f.write(d_str)
    
    
    def write(self):
        '''Ask user for `d_str` and write it in `self.fn`'''
        
        if isfile(self.fn):
            o = 0
            while o not in ('y', 'n'):
                o = input(f"File '{self.fn}' already exist.\nOverwrite it (y/n) ?\n>")
            
            if o == 'n':
                return 0
        
        d = self._get_dct()
        self._write(d)
    
    
    def extend(self):
        '''Same as self.write, but extand an existing file.'''
        
        d = self.read()
        i = len(d)
        
        d_new = self._get_dct()
        
        for k in d_new:
            d[k + i] = d_new[k]
        
        self._write(d)
    
    def display(self, opposite=True, view_md=0):
        '''
        Outputs to the screen the vocabulary list `self.fn`.
        
        - opposite : reverse the columns if True ;
        - view_md : an int which, if odd, change the view mode (space before the words in the first column instead of after).
        '''
        
        d = self.read()
        mx = max(len(d[k][0]) for k in d)
        
        print('\nList "{}" :'.format(self.fn))
        
        for k in d:
            print('\t{} : {}'.format(set_good_len(d[k][opposite], mx, view_md % 2), d[k][not opposite]))
        

##-main
def learn(d, mode=0, n=0):
    '''
    Learn by asking :
        - [lang] with french shown if mode is 0 ;
        - french with [lang] shown if mode is 1.
    
    - d : the vocabulary list, of the form {0: ('fra', 'ita'), 1: ('fra2', 'ita2'), ...} ;
    - mode : indicate the learn direction ;
    - n : the number of words to learn. If n == 0, learn all the words in the list. If 0 < n < len(d), the function remove the words randomly.
    '''
    
    if mode not in (0, 1):
        raise ValueError('The mode should be in (0, 1), but "{}" was found !'.format(mode))
    
    if n < 0:
        raise ValueError('The argument "n" can not be negative ! ("{}" found)'.format(n))
    
    if n > len(d):
        print('n is bigger than the number of words. Only {} words will be learned.\n'.format(len(d)))
    
    old_len = len(d)
    shuffle(d)
    
    if n != 0:
        for k in range(len(d)):
            if (k + 1) > n:
                del d[k]
    
    md1 = (1, 0)[mode]
    lth = len(d)
    wrong = []
    i = 0
    
    print('Press <ctrl> + C to interrupt, anytime')
    t0 = dt.now()
    
    for j, k in enumerate(d):
        try:
            answer = input('\n{}/{} - {} :\n>'.format(j + 1, lth, d[k][mode])).strip(' ')

            if d[k][md1][-1] not in ('$', '*') and answer[-1] in ('$', '*'):
                answer = answer[:-1] # Remove '$' or '*' at the end of the answer if misclicked.
            
            if answer == d[k][md1]:
                print('Good !')
                i += 1
            
            else:
                print('Wrong : word was "{}"'.format(d[k][md1]))
                wrong.append(d[k][md1])
    
        except KeyboardInterrupt:
            if j == 0:
                print('')
                sys.exit()
                
            break
    
    t = dt.now() - t0
    
    print('\nScore : {} good, {} wrong, on {} words (out of {} in list).\nPercentage : {}% good\nTime : {} s\nTime per word average : {} s'.format(i, len(wrong), i + len(wrong), old_len, round(i / (i + len(wrong)) * 100), t, t / (i + len(wrong))))
    
    if len(wrong) > 0:
        print('\n\nTo revise : \n\t{}'.format('\n\t'.join(wrong)))


##-UI
class Parser:
    '''Defining the UI'''
    
    def __init__(self):
        '''Initiate Parser'''

        self.parser = argparse.ArgumentParser(
            prog='voc',
            description='Help to learn vocabulary.',
            epilog="Examples :\n\tLearn list 'list.txt' :   ./voc.py list.txt\n\tLearn opposite way    :   ./voc.py -o list.txt\n\tSave a new list       :   ./voc.py -s filename.txt\n\tLearn 10 words        :   ./voc.py -n 10 list.txt",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        self.parser.add_argument(
            'listname',
            help='List to learn.'
        )

        self.parser.add_argument(
            '-v', '--version',
            help='Show Voc version and exit',
            nargs=0,
            action=self.Version
        )

        self.parser.add_argument(
            '-o', '--opposite',
            help='Reverse learning mode (if learning italian, write in your lang instead of in italian).',
            action='store_true'
        )

        self.parser.add_argument(
            '-s', '--save',
            help='Save a new file.',
            action='store_true'
        )

        self.parser.add_argument(
            '-a', '--append',
            help='Append new words to an existing file.',
            action='store_true'
        )

        self.parser.add_argument(
            '-d', '--display',
            #dest='LIST',
            help='Display the vocabulary list `listname`. The flag -o reverse the columns. The flag -n 1 change the view mode (space before the words in the first column instead of after).',
            action='store_true'
        )

        self.parser.add_argument(
            '-n', '--number',
            help='The number of words asked. If it is 0, learn all the words.',
            type=int
        )
        
    
    def parse(self):
        '''Parse the args'''

        #------Check arguments
        args = self.parser.parse_args()
        
        if args.display:
            VocFile(args.listname).display(args.opposite, (args.number, 0)[args.number == None])
        
        elif args.append:
            VocFile(args.listname).extend()
        
        elif args.save:
            VocFile(args.listname).write()
        
        else:
            n = (args.number, 0)[args.number == None]
            
            if n < 0:
                print('The argument "n" can not be negative ! ("{}" found)'.format(n))
                sys.exit(-1)
            
            learn(VocFile(args.listname).read(), args.opposite, n)


    class Version(argparse.Action):
        '''Class used to show Voc version.'''

        def __call__(self, parser, namespace, values, option_string):

            print(f'Voc v{version}')
            parser.exit()


class Menu:
    '''Defining a menu.'''
    
    def __init__(self):
        '''Initiate this class'''
        
        pass
    
    def ask_fn(self):
        '''Ask the user for the filename.'''
        
        fn = input('Enter the filename :\n>')
            
        if (fn[-4:] != '.txt') and (not isfile(fn)) and (isfile(fn + '.txt')):
            fn += '.txt'
        
        return fn
    
    
    def show(self):
        
        try:
            self.show_()
        
        except KeyboardInterrupt:
            if input('Exit ? (y/n)') == 'y':
                sys.exit()
        
    
    def show_(self):
        '''Show a menu'''
        
        while True:
            print('\n\nMenu :')
            print('    0.Quit')
            print('    ----------------')
            print('    1.Learn a list')
            print('    2.Save a NEW list')
            print('    3.Append to a list')
            print('    4.Display a list')
            print('    ----------------')
            print('    5.Show version')
            
            c = input('\n>')
            
            if c.lower() in ('0', 'exit', 'quit', 'q'):
                sys.exit()
            
            elif c == '1':
                learn(VocFile(self.ask_fn()).read())
                sleep(1)
            
            elif c == '2':
                VocFile(self.ask_fn()).write()
                sleep(0.5)
            
            elif c == '3':
                VocFile(self.ask_fn()).extend()
                sleep(0.5)
            
            elif c == '4':
                VocFile(self.ask_fn()).display()
                sleep(0.5)
            
            elif c == '5':
                print(f'Voc v{version}')
                sleep(1)
            
            else:
                print('"{}" is NOT an option of this menu !!!'.format(c))
                sleep(0.5)


##-run
if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        app = Parser()
        app.parse()
    
    else:
        Menu().show()
