#!/usr/bin/env python2
# encoding: utf-8

"""Implementation of Freenet Commmunication Primitives"""


import sys
import argparse # commandline arguments
import cmd # interactive shell

# first, parse commandline arguments
def parse_args():
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser(description="Implementation of Freenet Communication Primitives")
    parser.add_argument('-u', '--user', default=None, help="Identity to use (default: create new)")
    parser.add_argument('--test', default=False, action="store_true", help="Run the tests")
    args = parser.parse_args()
    return args


# then add interactive usage, since this will be a communication tool
class Babcom(cmd.Cmd):
    prompt = "> "
    def do_hello(self, args):
        """Says Hello

        usage: hello [<name>]"""
        name = args[0] if args[1:] else 'World'
        print "Hello {}".format(name)

    def do_quit(self, args):
        "Leaves the program"
        raise SystemExit

    def do_EOF(self, args):
        "Leaves the program. Commonly called via CTRL-D"
        raise SystemExit


def _test():
    """Run the tests

    >>> True
    True
    """
    try:
        import newbase60
        numtostring = newbase60.numtosxg
    except:
        numtostring = str
        
    import doctest
    tests = doctest.testmod()
    if tests.failed:
        return "☹"*tests.failed + " / " + numtostring(tests.attempted)
    return "^_^ (" + numtostring(tests.attempted) + ")"


if __name__ == "__main__":
    args = parse_args()
    if args.test:
        print _test()
        sys.exit(0)
    print args
    prompt = Babcom()
    prompt.cmdloop('Starting babcom, type help for help')
#!/usr/bin/env python2
# encoding: utf-8

"""Implementation of Freenet Commmunication Primitives"""


import sys
import argparse # commandline arguments
import cmd # interactive shell

# first, parse commandline arguments
def parse_args():
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser(description="Implementation of Freenet Communication Primitives")
    parser.add_argument('-u', '--user', default=None, help="Identity to use (default: create new)")
    parser.add_argument('--test', default=False, action="store_true", help="Run the tests")
    args = parser.parse_args()
    return args


# then add interactive usage, since this will be a communication tool
class Babcom(cmd.Cmd):
    prompt = "> "
    def do_hello(self, args):
        """Says Hello

        usage: hello [<name>]"""
        name = args[0] if args[1:] else 'World'
        print "Hello {}".format(name)

    def do_quit(self, args):
        "Leaves the program"
        raise SystemExit

    def do_EOF(self, args):
        "Leaves the program. Commonly called via CTRL-D"
        raise SystemExit


def _test():
    """Run the tests

    >>> True
    True
    """
    try:
        import newbase60
        numtostring = newbase60.numtosxg
    except:
        numtostring = str
        
    import doctest
    tests = doctest.testmod()
    if tests.failed:
        return "☹"*tests.failed + " / " + numtostring(tests.attempted)
    return "^_^ (" + numtostring(tests.attempted) + ")"


if __name__ == "__main__":
    args = parse_args()
    if args.test:
        print _test()
        sys.exit(0)
    print args
    prompt = Babcom()
    prompt.cmdloop('Starting babcom, type help for help')
