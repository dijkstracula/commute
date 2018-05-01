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

        ("# A comment", commute.Comment("A comment")),
        ("#abc", commute.Comment("abc")),

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
        self.assertEqual(len(g.edges), 3)
        self.assertEqual(len(g.edges["busstop"]), 2)

class RoutePrioritization(unittest.TestCase):
    def test_flexroute_prio(self):
        l = [commute.FlexRoute("home", "bart", "15"), commute.FlexRoute("home", "ferry", "25")]
        self.assertEqual(l, sorted(l))

    def test_timedroute_prio(self):
        l = [commute.TimedRoute("north_berkley", "7:15", "millbrae", "8:11"), commute.TimedRoute("north_berkley", "8:15", "millbrae", "9:11")]
        self.assertEqual(l, sorted(l))

    def test_mixed_prio(self):
        l = [commute.FlexRoute("home", "bart", "15"), commute.TimedRoute("north_berkley", "7:15", "millbrae", "8:11")]
        self.assertEqual(l, sorted(l))


if __name__ == "__main__":
    unittest.main()
