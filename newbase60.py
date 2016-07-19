'''newbase60.py - Python implementation of Tantek's NewBase60 
    http://tantek.pbworks.com/w/page/19402946/NewBase60
    by Kevin Marks
    Licence CC0
    based on http://faruk.akgul.org/blog/tantek-celiks-newbase60-in-python-and-java/'''

CHARACTERS = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ_abcdefghijkmnopqrstuvwxyz'

NUMBERS = dict(zip(CHARACTERS,range(len(CHARACTERS))))
NUMBERS['l'] = 1 # typo lowercase l to 1
NUMBERS['I'] = 1 # typo capital I to 1
NUMBERS['O'] = 0 # typo capital O to 0


def numtosxg(n):
    s = ''
    if not isinstance(n, int) or n == 0:
        return '0'
    while n > 0:
        n, i = divmod(n, 60)
        s = CHARACTERS[i] + s
    return s


def sxgtonum(s):
    n = 0
    for c in s:
        n = n * 60 + NUMBERS.get(c,0)
    return n
