#!/usr/bin/python
"""
commpute.py : A commute planner.  I should have done this in Prolog.

Input file format, roughly:

DOC = <COMMENT>* <NL> <HEADER> <NL> ROUTE+
HEADER = <start> <dest>
ROUTE = FLEX_ROUTE | TIMED_ROUTE | COMMENT
FLEX_ROUTE = f <name> <start> <dest> <duration>
TIMED_ROUTE = t <name> <start> <start_time> <dest> <dest_time>

name, start, dest all probably /\w+/ or /"[^"]"/.
duration and times probably all /\d\d:\d\d/.

I kind of also want things like tracking commuting costs (for TimedRoute),
and calories burnt (for cycling flex routes), etc.  Might also be nice to
indicate commute type (ferry, BART, bus, etc...) and be able to prefer one
kind over another...
"""

from collections import defaultdict, namedtuple
import fileinput
import datetime
import re

class CommuteGraph:
    def __init__(self, lines):
        """Constructs a new CommuteGraph by parsing the supplied entries."""
        self.edges = defaultdict(list)

        entries = [parse(line) for line in lines]
        # Ensure we have no parse errors.
        for i, e in enumerate(entries):
            if e is None:
                raise Exception("Syntax error on line {0}: \"{1}\"".format(i+1, lines[i]))

        # Scan ahead until we find the header.
        for i in range(0, len(entries)):
            e = entries[i]
            if isinstance(e, Header):
                break
            elif isinstance(e, Comment):
                next
            if isinstance(e, FlexRoute) or isinstance(e, TimedRoute):
                raise Exception("Routes appearing before header")

        # There must be a header.
        if i == len(entries):
            raise Exception("Missing header line")

        # Build the graph.
        for e in entries[i+1:]:
            if isinstance(e, FlexRoute):
                self.add_flexroute(e)
            elif isinstance(e, TimedRoute):
                self.add_timedroute(e)
            elif isinstance(e, Comment):
                next
            elif isinstance(e, Header):
                raise Exception("Duplicate header")
            else:
                raise Exception("Unexpected entry type {0}".format(e.__class__))

    def add_flexroute(self, fr):
        """Adds a flex route to the commute graph. """
        pass

    def add_timedroute(self, tr):
        """Adds a timed route to the commute graph. """
        pass

#############################################################################
# Input parsing
#############################################################################

word_pat = '(\w+)'
time_pat = '(\d?\d:\d{2})'
dur_pat = '(\d+)'
header_re = re.compile('(\w+)\s+(\w+)')
flex_re = re.compile("f {0}\s+{1}\s+{2}\s*".format(word_pat, word_pat, dur_pat))
timed_re = re.compile("t {0}\s+{1}\s+{2}\s+{3}\s*".format(word_pat, time_pat, word_pat, time_pat))
comment_re = re.compile("#\s*(.*)")

class FlexRoute:
    """A flexible route for the commute graph.  A FlexRoute is an edge
    that can be processed at any time.  For instance, cycling from my house
    to the train might take 15 minutes, but I can do so at any point."""
    def __init__(self, start, dest, duration):
        self.start = start
        self.dest = dest
        self.duration = validateDuration(duration)

    def __eq__(self, other):
        return self.start == other.start and self.dest == other.dest and self.duration == other.duration

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "FlexRoute({0}, {1}, {2})".format(self.start, self.dest, self.duration)

class TimedRoute:
    """A timed route to the commute graph.  A timed route is an edge
    that can only be processed at or after the current time."""
    def __init__(self, start, start_time, dest, dest_time):
        self.start = start
        self.start_time = validateTime(start_time)
        self.dest = dest
        self.dest_time = validateTime(dest_time)

        if self.start_time >= self.dest_time:
            raise Exception("Start time must be before dest time!")

    def __eq__(self, other):
        return self.start == other.start and self.dest == other.dest and self.start_time == other.start_time and self.dest_time == other.dest_time

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "TimedRoute({0}, {1}, {2}, {3})".format(self.start, self.start_time, self.dest, self.dest_time)

Comment = namedtuple('Comment', ['contents'])
Header = namedtuple('Header', ['start', 'dest'])

def parse(line):
    m = re.match(flex_re, line)
    if m is not None:
        return FlexRoute(m.group(1), m.group(2), m.group(3))

    m = re.match(timed_re, line)
    if m is not None:
        return TimedRoute(m.group(1), m.group(2), m.group(3), m.group(4))

    m = re.match(header_re, line)
    if m is not None:
        return Header(m.group(1), m.group(2))

    m = re.match(comment_re, line)
    if m is not None:
        return Comment(m.group(1))

    return None

def validateTime(tok):
    """Produces a datetime.time from the current token."""
    h, m = tok.split(":")
    return datetime.time(hour=int(h), minute=int(m))

def validateDuration(tok):
    """Produces a TimeDelta from the current token."""
    return datetime.timedelta(minutes=int(tok))



if __name__ == "__main__":
    g = CommuteGraph(fileinput.input())
    #TODO: g.do_the_thing()
