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
import functools
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

        self.start = entries[i].start
        self.dest = entries[i].dest

        # Build the graph.
        for e in entries[i+1:]:
            if isinstance(e, FlexRoute) or isinstance(e, TimedRoute):
                self.edges[e.start].append(e)
            elif isinstance(e, Comment):
                next
            elif isinstance(e, Header):
                raise Exception("Duplicate header")
            else:
                raise Exception("Unexpected entry type {0}".format(e.__class__))

        # Lastly, sort the routes according to priority.
        for k, v in self.edges.items():
            v.sort()


    def find_path(self, start, dest):
        """traverses the commute graph and finds the paths that exist from start
        to dest, with the "don't get on routes that have already departed"
        timing constraint. """
        def dfs_unconstrained(start, dest, seen, acc):
            """Does a DFS from start to dest.  In this state we have not encountered
            any timed routes, so our accumulator is the amount of time spent commuting
            along those flex states.  If we encounter a timed state, we have to
            transition to recursing with dfs_constrained()."""
            pass
        def dfs_constrained(start, dest, seen, acc):
            """Does a DFS from start to dest.  In this state we have encountered
            timed routes, so accumulator is the current "timestamp" of our arrival at
            the previous state.  TODO: what if there is no previous state? Think this
            one through."""
            pass
        dfs_unconstrained(start, dest, set(), 0)


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


def route_le(a,b):
    """Returns the route with the greatest "priority", which we define as follows:
      - Always prefer flexibile routes over timed routes
      - Prefer shorter flex routes over longer ones
      - Prefer timed routes that leave earler than ones that leave later.
    """
    if (isinstance(a, FlexRoute) and isinstance(b, FlexRoute)):
        return a.duration < b.duration
    if (isinstance(a, FlexRoute) and isinstance(b, TimedRoute)):
        return True
    if (isinstance(a, TimedRoute) and isinstance(b, FlexRoute)):
        return False
    return a.start < b.start

@functools.total_ordering
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
    
    def __le__(self, other):
        return route_le(self, other)

    def __repr__(self):
        return "FlexRoute({0}, {1}, {2})".format(self.start, self.dest, self.duration)

@functools.total_ordering
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

    def __le__(self, other):
        return route_le(self, other)

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
