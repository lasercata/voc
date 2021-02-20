# voc
Python3 Argparse script which help to learn vocabulary

## Installing
Download the script `voc.py` ;

Make it executable : 

```bash
$ chmod +x voc.py
```

## Usage
```bash
$./voc.py -h
usage: Voc [-h] [-v] [-o] [-s] listname

Help to learn voc.

positional arguments:
  listname        List to learn.

optional arguments:
  -h, --help      show this help message and exit
  -v, --version   Show Voc version and exit
  -o, --opposite  Reverse learning mode (if learning italian, write in your lang instead of in italian).
  -s, --save      Save a new file.

Examples :
        Learn list 'list.txt' :   ./voc.py list.txt
        Learn opposite way    :   ./voc.py -o list.txt
        Save a new list       :   ./voc.py -s filename.txt
```
