import unittest

from item import *


class OptionTest(unittest.TestCase):
    def test_options_1(self):
        opt1 = Option('공', 10)
        opt2 = Option('공', 5)
        opt3 = Option('공속', -7)

        self.assertEqual(Option('공', 15), opt1 + opt2)
        self.assertEqual(Option('공', -5), opt2 - opt1)
        self.assertRaises(AssertionError, lambda: opt3 + opt1)

    def test_optionspec_1(self):
        options1 = [Option('공', 3), Option('공속', 11), Option('흡', 5)]
        options2 = [Option('공속', -5), Option('방', 7), Option('체', 21)]

        added = OptionSpec([Option('공', 3), Option('공속', 6), Option('흡', 5), Option('방', 7), Option('체', 21)])
        self.assertEqual(added, OptionSpec(options1) + OptionSpec(options2))

        subtracted = OptionSpec([Option('공', 3), Option('공속', 16), Option('흡', 5), Option('방', -7), Option('체', -21)])
        self.assertEqual(subtracted, OptionSpec(options1) - OptionSpec(options2))


class ItemTest(unittest.TestCase):
    def test_item_1(self):
        item1 = Item('장갑', [Option('공속', 5), Option('체', 15)])
        self.assertEqual('Item[장갑] - {공속 +5 / 체 +15}', str(item1))

        self.assertEqual(False, item1.add_option(Option('체', 10)))
        self.assertEqual(True, item1.add_option(Option('체', -10)))
        self.assertEqual(True, item1.add_option(Option('회', 10)))
        self.assertEqual(OptionSpec([Option('공속', 5), Option('체', 5), Option('회', 10)]), item1.get_spec())

        self.assertEqual('Item[장갑] - {공속 +5 / 체 +15 / 회 +10} / {체 -10}', str(item1))

    def test_itemset_1(self):
        item_set1 = ItemSet([
            Item('모자', [Option('공', 4), Option('방', 10)]),
            Item('장갑', [Option('공속', -5), Option('방', 7), Option('체', 21)]),
            Item('신발', [Option('뎀증', 15), Option('체', 7)]),
        ])
        self.assertEqual(OptionSpec([Option('공', 4), Option('공속', -5), Option('방', 17), Option('체', 28), Option('뎀증', 15)]),
                         item_set1.get_spec())
