#!/bin/python3
# -*- coding: utf-8 -*-

#--------------------------------------------------
#
# Author    :   Lasercata
# Date      :   2021.02.20
version = '1.1'
#
#--------------------------------------------------

# Todo :
    # Do score for words, to show them with a higher probability next time, or more often ;
    # Maybe a QCM ;

##-import
from random import shuffle
from ast import literal_eval

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


class VocFile:
    '''Class managing the voc files'''
    
    def __init__(self, fn):
        '''Initiate obj'''
        
        if fn[-4:] != '.txt':
            fn += '.txt'
        
        self.fn = fn
    
    
    def read(self):
        '''Return the dict in self.fn'''
        
        if not isfile(self.fn):
            raise ValueError(f"Voc: cannot access '{self.fn}': No such file")
        
        with open(self.fn, 'r') as f:
            d_str = f.read()
        
        return literal_eval(d_str)
    
    
    def _get_dct(self):
        d = {}
        i = 0

        print('Type <ctrl> + C to quit.')

        while True:
            try:
                d[i] = tuple(input('Words (fra,[lang]), separeted by a comma :').split(','))
                i += 1

            except KeyboardInterrupt:
                break

        return set_dict(d)
    
    
    def write(self):
        '''Ask user for `d_str` and write it in `self.fn`'''
        
        if isfile(self.fn):
            o = 0
            while o not in ('y', 'n'):
                o = input(f"File '{self.fn}' already exist.\nOverwrite it (y/n) ?\n>")
            
            if o == 'n':
                return 0
        
        d_str = self._get_dct()
        
        with open(self.fn, 'w') as f:
            f.write(d_str)
        

##-main
def learn(d, mode=0):
    '''
    Learn by asking :
        - [lang] with french shown if mode is 0 ;
        - french with [lang] shown if mode is 1.
    '''
    
    shuffle(d)
    md1 = (1, 0)[mode]
    lth = len(d)
    wrong = []
    i = 0
    
    print('Press <ctrl> + C to interrupt, anytime')
    
    for j, k in enumerate(d):
        try:
            answer = input('\n{}/{} - {} :\n>'.format(j + 1, lth, d[k][mode]))
            
            if answer == d[k][md1]:
                print('Good !')
                i += 1
            
            else:
                print('Wrong : word was "{}"'.format(d[k][md1]))
                wrong.append(d[k][md1])
    
        except KeyboardInterrupt:
            if j == 0:
                sys.exit()
                
            break
    
    print('\nScore : {} good, {} wrong, on {} words (out of {}).\nPercentage : {}% good'.format(i, len(wrong), i + len(wrong), lth, round(i / (i + len(wrong)) * 100)))
    
    if len(wrong) > 0:
        print('\n\nTo revise : \n\t{}'.format('\n\t'.join(wrong)))


##-UI
class Parser:
    '''Defining the UI'''
    
    def __init__(self):
        '''Initiate Parser'''

        self.parser = argparse.ArgumentParser(
            prog='Voc',
            description='Help to learn voc.',
            epilog="Examples :\n\tLearn list 'list.txt' :   ./voc.py list.txt\n\tLearn opposite way    :   ./voc.py -o list.txt\n\tSave a new list       :   ./voc.py -s filename.txt",
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
        
    
    def parse(self):
        '''Parse the args'''

        #------Check arguments
        args = self.parser.parse_args()
        
        if args.save:
            VocFile(args.listname).write()
        
        else:
            learn(VocFile(args.listname).read(), args.opposite)


    class Version(argparse.Action):
        '''Class used to show Voc version.'''

        def __call__(self, parser, namespace, values, option_string):

            print(f'Voc v{version}')
            parser.exit()


##-run
if __name__ == '__main__':
    
    app = Parser()
    app.parse()
