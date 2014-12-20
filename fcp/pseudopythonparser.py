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
        self.unparsed = []
        self.endunparsed = None
        self.unparsedvariable = None
    
    def parse(self, text):
        for line in text.splitlines():
            self.readline(line)
        # if unparsed code remains, that is likely an error in the code.
        if self.unparsedstring.strip() or self.endunparsed:
            raise ValueError("Invalid or too complex code: " + self.endunparsed + "\n" + self.unparsed)
        return self.data
    
    def jsonload(self, text):
        # replace entities which json encodes differently from python.
        text = text.replace(
            " None", " null").replace(
            " True", " true").replace(
            " False", " false").replace(
            # json does not support tuples, so parse them as list.
            " (", " [").replace(
            "),", "],").replace(
            # json cannot handle unicode string markers
            ' u"', ' "').replace(
            ' [u"', ' ["').replace(
            " u'", " '").replace(
            " [u'", " ['")
        try:
            return json.loads(text+"\n")
        except ValueError:
            # on old freesitemrg site entries json can break, so it
            # needs some manual conversion.
            # json uses " for strings but never '. Python may use '
            # for backwards compatibility we have to treat this correctly.
            # If there are two " in a line, then every ' must be escaped 
            # as \' instead of being replaced by ". This requires some care.
            lines = text.splitlines()
            for n, l in enumerate(lines[:]):
                if l.count('"') and not l.count('"') % 2: # even number
                    l = l.replace("'", "\\'")
                    lines[n] = l
                elif "'" in l:
                    l = l.replace("'", '"')
                    lines[n] = l
            text = "\n".join(lines)
            try:
                return json.loads(text+"\n")
            except ValueError:
                print text
                raise
    
    # FIXME: Using a property here might be confusing, because I assign
    #        directly to unparsed. Check whether there’s a cleaner way.
    @property
    def unparsedstring(self):
        """Join and return self.unparsed as a string."""
        return "\n".join(self.unparsed)
    
    def checkandprocessunprocessed(self):
        """Check if the rest of self.unprocessed finishes the line."""
        if self.endunparsed in self.unparsedstring:
            self.data[self.unparsedvariable] = self.jsonload(self.unparsedstring)
            self.unparsed, self.unparsedvariable, self.endunparsed = [], "", ""
    
    def readline(self, line):
        """Read one line of text."""
        # if we have unparsed code and this line does not end it, we just add the code to the unparsed code.
        if self.unparsed and not self.endunparsed:
            raise ValueError("We have unparsed data but we do not know how it ends. THIS IS A BUG.")
        
        if self.unparsed and self.endunparsed:
            self.unparsed.append(line)
        
        if self.unparsed and self.endunparsed and not line.strip().endswith(self.endunparsed):
            return # line is already processed as far as possible
        if self.unparsed and self.endunparsed and line.strip().endswith(self.endunparsed):
            # json uses null for None, true for True and false for False. 
            # We have to replace those in the content and hope that nothing will break.
            data = self.jsonload(self.unparsedstring)
            self.data[self.unparsedvariable] = data
            self.unparsed, self.endunparsed = [], ""
            return
        
        # start reading complex datastructures
        if " = [" in line:
            start = line.index(" = [")
            self.unparsedvariable = line[:start]
            self.unparsed = [line[start+3:]]
            self.endunparsed = "]"
            self.checkandprocessunprocessed()
            return
        elif " = {" in line:
            start = line.index(" = {")
            self.unparsedvariable = line[:start]
            self.unparsed = [line[start+3:]]
            self.endunparsed = "}"
            self.checkandprocessunprocessed()
            return
        
        # handle the easy cases
        # ignore empty lines
        if not line.strip():
            return
        # ignore comments
        if line.strip().startswith("#"):
            return
        # the only thing left to care for are variable assignments
        if not " = " in line:
            return
        
        # prepare reading variables
        start = line.index(" = ")
        variable = line[:start]
        forbiddenvariablechars = " ", ".", "+", "-", "=", "*", "/"
        if True in [i in variable for i in forbiddenvariablechars]:
            raise ValueError("Variables must not contain any of the forbidden characters: " + str(forbiddenvariablechars))
        rest = line[start+3:].strip()
        
        # handle literal values: these are safe to eval
        safevalues = "True", "False", "None" 
        if rest in safevalues:
            self.data[variable] = eval(rest)
            return

        # handle json literals
        safevalues = "true", "false", "null" 
        if rest in safevalues:
            self.data[variable] = json.loads(rest)
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
