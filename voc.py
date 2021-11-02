#!/bin/python3
# -*- coding: utf-8 -*-

#--------------------------------------------------
#
# Author    :   Lasercata
# Date      :   2021.11.02
# Version   :   v1.4.2
# Github    :   https://github.com/lasercata/voc
#
#--------------------------------------------------

version = '1.4.2'

# Todo :
    # Do score for words, to show them with a higher probability next time, or more often ;

##-import
from random import shuffle, randint
from ast import literal_eval

from datetime import datetime as dt
from time import sleep

from os.path import isfile
import sys

import platform

#------For parser
import argparse

##------For Quizlet downloads
#try:
    #from requests_html import HTMLSession

#except ModuleNotFoundError:
    #print("It seems that you don't have the module 'requests_html' installed. It is used to download lists from Quizlet. If you want to install it, enter `pip install requests-html` in your console, or visit 'https://docs.python-requests.org/projects/requests-html/en/latest/'")
    #sleep(1)

# Imported in the __init__ method of GetQuizletVoc because it takes time.

##-Useful functions
def set_list(lst):
    '''
    Return a string representing the list, with line by line key-value.
    Usefull to set readable lists in your programs
    '''

    ret = '['

    for k in lst:
        ret += '\n\t{},'.format(set_str(k))

    ret = ret[:-1] + '\n]'

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


##-VocFile
class VocFile:
    '''Class managing the voc files'''
    
    def __init__(self, fn):
        '''Initiate obj'''
        
        #if fn[-4:] != '.txt':
            #fn += '.txt'
        
        if type(fn) == str:
            print('In VocFile.__init__: fn is a string. It should be a string list.')
            fn = [fn]

        self.fn = fn
    
    
    def _read_file(self, fn):
        '''Return the dict of fn'''
        
        if not isfile(fn):
            raise ValueError(f"Voc: cannot access '{fn}': No such file")
        
        with open(fn, 'r', encoding='utf-8') as f:
            d_str = f.read()
        
        d = literal_eval(d_str)
        
        if type(d) == dict:
            return [d[k] for k in d]
        
        return d


    def read(self):
        '''Read all the files in the list `self.fn`and return the concatenation of the lists.'''

        ret = []
        for l in self.fn:
            ret += self._read_file(l)

        return ret
    
    
    def _get_dct(self, sep=';'):
        d = []
        i = 0

        print('Type <ctrl> + C to quit.')

        while True:
            try:
                d.append(input(f'Words (definition, term), separeted by "{sep}" :').split(sep))
                
                for j, k in enumerate(d[i]):
                    d[i][j] = k.strip(' ') #remove the spaces at the begin and at the end of the words

                d[i] = tuple(d[i])
                i += 1

            except KeyboardInterrupt:
                break

        return d
    
    
    def _write(self, d):
        '''Write `d` in the file.'''
        
        if len(self.fn) > 1:
            print('\n\nYou specified multiple files, but content will only be saved in the first one : "{}"'.format(self.fn[0]))

        d_str = set_list(d) + '\n'
        
        with open(self.fn[0], 'w', encoding='utf-8') as f:
            f.write(d_str)
    
    
    def write(self):
        '''Ask user for `d_str` and write it in `self.fn`'''
        
        if isfile(self.fn[0]):
            o = 0
            while o not in ('y', 'n'):
                o = input(f"File '{self.fn[0]}' already exist.\nOverwrite it (y/n) ?\n>")
            
            if o == 'n':
                return 0
        
        d = self._get_dct()
        self._write(d)
    
    
    def extend(self):
        '''Same as self.write, but extand an existing file.'''
        
        d = self.read()
        d_new = self._get_dct()
        
        self._write(d + d_new)
    
    def display(self, opposite=True, view_md=0):
        '''
        Outputs to the screen the vocabulary list `self.fn`.
        
        - opposite : reverse the columns if True ;
        - view_md : an int which, if odd, change the view mode (space before the words in the first column instead of after).
        '''
        
        d = self.read()
        mx = max(len(k[opposite]) for k in d)
        
        print('\nList "{}" :'.format(self.fn))
        
        for k in d:
            print('\t{} : {}'.format(set_good_len(k[opposite], mx, view_md % 2), k[not opposite]))


##-GetQuizletVoc
class GetQuizletVoc:
    '''Fetch a vocabulary from Quizlet'''

    def __init__(self, url):
        '''Initiate attributes'''

        self.url = url
        self.pattern = '<span class="TermText notranslate lang-'
        self.pattern2 = 'en">'
        
        try:
            from requests_html import HTMLSession

        except ModuleNotFoundError as err:
            print('To do this, you need to install "requests-html" python module, either with `pip install requests-html` or by visiting "https://docs.python-requests.org/projects/requests-html/en/latest/".')
            raise ModuleNotFoundError(err)
        
        global HTMLSession
            


    def _find_all(self, txt:str, sub:str):
        '''Return all the indexes where sub is in txt.'''

        ret = []
        k = 0

        while True:
            i = txt.find(sub, k)

            if i == -1:
                return ret

            ret.append(i)
            k = i + len(sub)


    def _get_html(self):
        '''Return the html code for the Quizlet page.'''
        
        ses = HTMLSession()
        
        try:
            quizlet = ses.get(self.url)
        
        except Exception as err:
            print(err)
            return -1
            
        return quizlet.text


    def _get(self):
        '''Return two lists of words, first is definition, second is a list of terms.'''

        html = self._get_html()        
        if html == -1:
            return -1
            
        ind = self._find_all(html, self.pattern)

        lst_1 = []
        lst_2 = []

        for k, i in enumerate(ind):
            begin = i + len(self.pattern) + len(self.pattern2)

            w = ''
            for char in html[begin:]:
                if char == '<': # html[begin:] is of the form 'word</span>...'
                    break

                w += char

            if k % 2 == 0:
                lst_2.append(w)
            else:
                lst_1.append(w)

        return lst_1, lst_2


    def get_list(self):
        '''Return the list of tuples formatted for voc script.'''

        g = self._get()
        if g == -1:
            return -1
            
        l1, l2 = g
        ret = []

        for i, j in zip(l1, l2):
            ret.append((i, j))

        return ret


    def download(self, fn):
        '''Write the list in a file.'''

        l = self.get_list()
        if l == -1:
            return -1
        
        data = set_list(l) + '\n'

        if isfile(fn):
            o = ''
            while o not in ('o', 'n', 'c'):
                o = input(f"File '{fn}' already exist.\nOverwrite it (o), change name (n), or cancel (c) ?\n>").lower()

            if o == 'c':
                return -1
            
            if o == 'n':
                return self.download(input('\nFilename :\n>'))

        with open(fn, 'w', encoding='utf-8') as f:
            f.write(data)


##-Main
class Voc:
    
    def __init__(self, d):
        '''
        Initiate Voc class.
        
        - d : he vocabulary list, of the form [('fra', 'ita'), ('fra2', 'ita2'), ...] ;
        '''
        
        self.d = d
    
    
    def _is_good(self, user_answer, good_word):
        '''Return a bool indicating if the user answer correspond to the good word.'''
        
        if good_word[-1] not in ('$', '*', '7') and len(user_answer) > 0:
            if user_answer[-1] in ('$', '*', '7'):
                user_answer = user_answer[:-1] # Remove '$' or '*' or '7' at the end of the answer if miss-clicked.
        
        if user_answer == good_word:
            return True
        
        for k in (', ', ' / ', ' ; ', '/', ',', ';'):
            if user_answer in good_word.split(k):
                print('There is also : {}'.format('"' + '", "'.join(i for i in good_word.split(k) if i != user_answer) + '"'))
                return True
        
        return user_answer == good_word
    
    
    def learn(self, mode=0, n=0):
        '''
        Learn by asking for :
            - term, with definition shown if mode is 0 ;
            - definition, with term shown if mode is 1.
        
        - mode : indicate the learn direction ;
        - n : the number of words to learn. If n == 0, learn all the words in the list. If 0 < n < len(d), the function remove the words randomly.
        '''
        
        d = list(self.d)
        
        if mode not in (0, 1, 2):
            raise ValueError('The mode should be in (0, 1, 2), but "{}" was found !'.format(mode))
        
        if n < 0:
            raise ValueError('The argument "n" can not be negative ! ("{}" found)'.format(n))
        
        if n > len(d):
            print('n is bigger than the number of words. Only {} words will be learned.\n'.format(len(d)))
        
        old_len = len(d)
        shuffle(d)
        
        if n != 0:
            d = d[:n]
        
        if mode != 2:
            md = int(mode)
            md1 = (1, 0)[md]
            
        lth = len(d)
        wrong = []
        i = 0
        
        print('Press <ctrl> + C to interrupt, anytime')
        t0 = dt.now()
        
        for j, k in enumerate(d):
            try:
                if mode == 2:
                    md = randint(0, 1)
                    md1 = (1, 0)[md]
                    
                answer = input('\n{}/{} - {} :\n>'.format(j + 1, lth, k[md])).strip(' ')
                
                if self._is_good(answer, k[md1]):
                    print('Good !')
                    i += 1
                
                else:
                    print('Wrong : word was "{}"'.format(k[md1]))
                    wrong.append(k[md1])
        
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
            nargs='*',
            help='List[s] to learn.'
        )

        self.parser.add_argument(
            '-v', '--version',
            help='Show Voc version and exit',
            nargs=0,
            action=self.Version
        )

        self.parser.add_argument(
            '-o', '--opposite',
            help='Reverse learning mode (write definitions instead of terms).',
            action='store_true'
        )

        self.parser.add_argument(
            '-r', '--random',
            help='Randomise the learning mode (ask for both terms and definitions). If used with "-o", only this is taken in account.',
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
            '-D', '--download',
            help='Download a list from a Quizlet link.',
            metavar='URL'
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

        if args.listname == []:
            print('voc: error: argument listname is requied')
            sys.exit(-1)
        
        if args.display:
            VocFile(args.listname).display(args.opposite, (args.number, 0)[args.number == None])
        
        elif args.append:
            VocFile(args.listname).extend()
        
        elif args.save:
            VocFile(args.listname).write()
        
        elif args.download != None:
            try:
                if GetQuizletVoc(args.download).download(args.listname[0]) == -1:
                    return -1
            
            except ModuleNotFoundError:
                sys.exit()
            
            else:
                lst_name = args.download.split('/')[-1] if args.download.split('/')[-1] != '' else args.download.split('/')[-2]
                print('\nList "{}" saved as "{}"'.format(lst_name, args.listname[0]))
        
        else:
            n = (args.number, 0)[args.number == None]
            
            mode = args.opposite
            if args.random:
                mode = 2
            
            if n < 0:
                print('The argument "n" can not be negative ! ("{}" found)'.format(n))
                sys.exit(-1)
            
            Voc(VocFile(args.listname).read()).learn(mode, n)


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
            print('    2.Learn a list with reversed questions (write definitions instead of terms)')
            print('    3.Learn list with random language input')
            print('    4.Save a NEW list')
            print('    5.Append to a list')
            print('    6.Display a list')
            print('    7.Download a list from Quizlet')
            print('    ----------------')
            print('    v.Show version')
            
            c = input('\n>')
            
            if c.lower() in ('0', 'exit', 'quit', 'q'):
                if platform.system() == 'Windows':
                    if input('Sure ? (y/n) :\n>').lower() in ('y', 'yes', 'o', 'oui'):
                        sys.exit()
                
                else:
                    sys.exit()
            
            elif c == '1':
                Voc(VocFile(self.ask_fn()).read()).learn()
                sleep(1)
            
            elif c == '2':
                Voc(VocFile(self.ask_fn()).read()).learn(mode=1)
                sleep(1)
            
            elif c == '3':
                Voc(VocFile(self.ask_fn()).read()).learn(mode=2)
                sleep(1)
            
            elif c == '4':
                VocFile(self.ask_fn()).write()
                sleep(0.5)
            
            elif c == '5':
                VocFile(self.ask_fn()).extend()
                sleep(0.5)
            
            elif c == '6':
                VocFile(self.ask_fn()).display()
                sleep(0.5)
            
            elif c == '7':
                try:
                    url = input('\nURL :\n>')
                    getter = GetQuizletVoc(url)
                    fn = input('\nFilename :\n>')
                    getter.download(fn)
                    
                except ModuleNotFoundError:
                    sleep(2) #Error message is shown in GetQuizletVoc.__init__
                
                else:
                    lst_name = url.split('/')[-1] if url.split('/')[-1] != '' else url.split('/')[-2]
                    print('\nList "{}" saved as "{}"'.format(lst_name, fn))
                    
                sleep(0.5)
            
            elif c == 'v':
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
