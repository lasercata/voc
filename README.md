# voc
Python3 Argparse script which help to learn vocabulary. Also available in menu console mode (execute it without arguments).

The program ask for term (or definition), and shows if the answer is good or not. If not, it shows what was the right answer. At the end, the succes percentage is shown, with all the missed words.

It is possible to write your own vocabulary list, and you can download onr from a Quizlet link.

## Installing
Download the script `voc.py` ;

Make it executable : 

```bash
$ chmod +x voc.py
```

## Usage
```
$./voc.py -h
usage: voc [-h] [-v] [-o] [-r] [-s] [-a] [-D URL] [-d] [-n NUMBER] [listname ...]

Help to learn vocabulary.

positional arguments:
  listname              List[s] to learn.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Show Voc version and exit
  -o, --opposite        Reverse learning mode (write definitions instead of terms).
  -r, --random          Randomise the learning mode (ask for both terms and definitions). If
                        used with "-o", only this is taken in account.
  -s, --save            Save a new file.
  -a, --append          Append new words to an existing file.
  -D URL, --download URL
                        Download a list from a Quizlet link.
  -d, --display         Display the vocabulary list `listname`. The flag -o reverse the
                        columns. The flag -n 1 change the view mode (space before the words in
                        the first column instead of after).
  -n NUMBER, --number NUMBER
                        The number of words asked. If it is 0, learn all the words.

Examples :
        Learn list 'list.txt' :   ./voc.py list.txt
        Learn opposite way    :   ./voc.py -o list.txt
        Save a new list       :   ./voc.py -s filename.txt
        Learn 10 words        :   ./voc.py -n 10 list.txt
```
