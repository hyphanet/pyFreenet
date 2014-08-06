#!/usr/bin/env python
# encoding: utf-8

"""
Safe method for reading files in the pseudo python syntax used for storing pyFreenet configurations.

This CANNOT read all kinds of python files. It is purely a specialized
reader for a very restricted subset of python code.

It uses json for reading more complex assignments.
"""

# this requires at least python 2.6.
import json

# Firstoff we need a reader which can be given consecutive lines and parse these into a dictionary of variables.
class Parser:
    def __init__(self):
        """Reads config files in Pseudo-Python-Syntax.

        >>> p = Parser()
        >>> p.parse("a = 1")
        {'a': 1}
        >>> p = Parser()
        >>> p.parse("b = [1,2,3,'a']")
        {'b': [1, 2, 3, u'a']}
        >>> p = Parser()
        >>> p.parse('''c = [ { 'a': 1,
        ...   'b': "c",
        ...   'd': [1, 2, 3, None, False, True, "e"]}]
        ...   ''')
        {'c': [{u'a': 1, u'b': u'c', u'd': [1, 2, 3, None, False, True, u'e']}]}
        """
        self.data = {}
        self.unparsed = ""
        self.endunparsed = None
        self.unparsedvariable = None
    
    def parse(self, text):
        for line in text.splitlines():
            self.readline(line)
        # if unparsed code remains, that is likely an error in the code.
        if self.unparsed.strip() or self.endunparsed:
            raise ValueError("Invalid or too complex code: " + self.endunparsed + "\n" + self.unparsed)
        return self.data
    
    def jsonload(self, text):
        # replace entities which json encodes differently from python.
        text = text.replace(
            " None", " null").replace(
            " True", " true").replace(
            " False", " false").replace(
            # json uses " for strings but never '. Python may use '
            "'", '"').replace(
            # json does not support tuples, so parse them as list.
            " (", " [").replace(
            "),", "],").replace(
            # json cannot handle unicode string markers
            ' u"', ' "').replace(
            ' [u"', ' ["')
        try:
            return json.loads(text+"\n")
        except ValueError:
            print text
            raise
    
    def checkandprocesslinerest(self, unparsed):
        """Check if the rest of the line finishes the line."""
        if self.endunparsed in self.unparsed:
            self.data[self.unparsedvariable] = self.jsonload(self.unparsed)
            self.unparsed, self.unparsedvariable, self.endunparsed = "", "", ""
    
    def readline(self, line):
        """Read one line of text."""
        # check unparsed code
        if self.unparsed:
            if not self.endunparsed:
                raise ValueError("We have unparsed data but we do not know how it ends." 
                                 "THIS IS A BUG.")
            else:
                self.unparsed += "\n" + line
                # if the line ends the unparsed code, store it.
                if line.strip().endswith(self.endunparsed):
                    # json uses null for None, true for True and false for False. 
                    # We have to replace those in the content and hope that nothing will break.
                    self.data[self.unparsedvariable] = self.jsonload(self.unparsed)
                    self.unparsed, self.endunparsed = "", ""
                # if the line does not end the unparsed code, just
                # keep the code we added to the unparsed code
                return
                
        
        # start reading complex datastructures
        if " = [" in line:
            start = line.index(" = [")
            self.unparsedvariable = line[:start]
            self.unparsed = line[start+3:]
            self.endunparsed = "]"
            self.checkandprocesslinerest(self.unparsed)
            return
        if " = {" in line:
            start = line.index(" = {")
            self.unparsedvariable = line[:start]
            self.unparsed = line[start+3:]
            self.endunparsed = "}"
            self.checkandprocesslinerest(self.unparsed)
            return
        
        # handle the easy cases
        if (not line.strip()                # ignore empty lines
            or line.strip().startswith("#") # ignore comments
            or not " = " in line):          # the only thing left to
                                            # care for are variable
                                            # assignments
            return
        
        # prepare reading variables
        start = line.index(" = ")
        variable = line[:start]
        # TODO: use a pre-created regexp for higher speed.
        forbiddenvariablechars = " ", ".", "+", "-", "=", "*", "/"
        if True in [i in variable for i in forbiddenvariablechars]:
            raise ValueError("Variables must not contain any of the forbidden characters: " + str(forbiddenvariablechars))
        rest = line[start+3:].strip()
        
        # handle literal values: these are safe to eval
        safevalues = "True", "False", "None" 
        if rest in safevalues:
            self.data[variable] = eval(rest)
            return
        
        # handle numbers: these are safe to eval, too
        numberchars = set(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."])
        if not False in [i in numberchars for i in rest]:
            self.data[variable] = eval(rest)
            return
        
        # finally handle strings
        if rest.startswith("'") and rest.endswith("'") or rest.startswith('"') and rest.endswith('"'):
            self.data[variable] = rest[1:-1]
            return
        
        # if we did not return by now, the file is malformed (or too complex)
        raise ValueError("Invalid or too complex code: " + line)

if __name__ == "__main__":
    from doctest import testmod
    testmod()
