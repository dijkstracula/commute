import commute
import datetime
import re
import unittest

class Tokenizing(unittest.TestCase):
    words = [ ('word', True), ('two words', False) ]
    times = [ ('01:23', True), ('1:23', True), ('11:59', True), ('99:99', True) ]

    def test_word_tokenization(self):
        r = re.compile("^" + commute.word_pat + "$")
        for token, expected in self.words:
            actual = re.fullmatch(r, token) is not None
            self.assertEqual(expected, actual)

    def test_time_tokenization(self):
        r = re.compile("^" + commute.time_pat + "$")
        for token, expected in self.times:
            actual = re.match(r, token) is not None
            self.assertEqual(expected, actual)

class LineParsing(unittest.TestCase):
    values = [
        ("home work", commute.Header("home", "work")),

        ("# A comment", None),
        ("#abc", None),

        ("f home train 15", commute.FlexRoute("home", "train", "15")),

        ("t north_berkeley 7:15 millbrae 8:11 ", commute.TimedRoute("north_berkeley", "7:15", "millbrae", "8:11")),
        ]

    def test_line_parsing(self):
        for line, expected in self.values:
            actual = commute.parse(line)
            self.assertEqual(actual, expected)

class DocumentParsing(unittest.TestCase):
    lines = ["# A sample commute from my hometown.",
             "home macewan",
             "f home busstop 5",
             "t busstop 7:00 legislature 7:35",
             "t busstop 7:15 legislature 7:50",
             "f legislature macewan 15"]

    def test_multiline_parse(self):
        g = commute.CommuteGraph(self.lines)
        self.assertEqual(len(g.edges), 4)
        self.assertEqual(len(g.edges["home"]), 1) #busstop
        self.assertEqual(len(g.edges["busstop"]), 3) #leg1, leg2, home
        self.assertEqual(len(g.edges["macewan"]), 1) #leg

    def test_dfs(self):
        g = commute.CommuteGraph(self.lines)
        #print([list(r) for r in g.find_path("home", "macewan")])

class FlexRoutePromoting(unittest.TestCase):
    f = commute.FlexRoute("home", "bart", "15")
    ts = datetime.time(12, 00, 00)
    def test_premote_from_begin_ts(self):
        t = self.f.promote(begin_ts=self.ts)
        self.assertEqual(t, commute.TimedRoute("home", "12:00", "bart", "12:15"))
    def test_premote_from_dest_ts(self):
        t = self.f.promote(end_ts=self.ts)
        self.assertEqual(t, commute.TimedRoute("home", "11:45", "bart", "12:00"))

class RoutePrioritization(unittest.TestCase):
    def test_flexroute_prio(self):
        l = [commute.FlexRoute("home", "bart", "15"), commute.FlexRoute("home", "ferry", "25")]
        self.assertEqual(l, sorted(l))

    def test_timedroute_prio(self):
        l = [commute.TimedRoute("north_berkeley", "7:15", "millbrae", "8:11"), commute.TimedRoute("north_berkeley", "8:15", "millbrae", "9:11")]
        self.assertEqual(l, sorted(l))

    def test_mixed_prio(self):
        l = [commute.FlexRoute("home", "bart", "15"), commute.TimedRoute("north_berkeley", "7:15", "millbrae", "8:11")]
        self.assertEqual(l, sorted(l))


if __name__ == "__main__":
    unittest.main()
