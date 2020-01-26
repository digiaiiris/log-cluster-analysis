#!/usr/bin/python
# coding=utf-8

import unittest
from ic_analysis.IdentifiersConfig import IdentifiersConfig


class TestIdentifiersConfig(unittest.TestCase):

    def test_simple_process_config(self):
        ic = IdentifiersConfig()
        ids = ic.process_config({
            'ABC': 'abc',
            'DEF': 'def'
            })
        self.assertEqual(len(ids), 2)
        self.assertEqual(ids['ABC'], 'abc')
        self.assertEqual(ids['DEF'], 'def')

    def test_intermittent_process_config(self):
        ic = IdentifiersConfig()
        ids = ic.process_config({
            'ABC': 'abc',
            '!DEF': 'def'
            })
        self.assertEqual(len(ids), 1)
        self.assertEqual(ids['ABC'], 'abc')

    def test_reference_process_config(self):
        ic = IdentifiersConfig()
        ids = ic.process_config({
            'ABC': 'abc %{DEF}',
            '!DEF': 'def'
            })
        self.assertEqual(len(ids), 1)
        self.assertEqual(ids['ABC'], 'abc def')

    def test_recursive_reference_process_config(self):
        ic = IdentifiersConfig()
        ids = ic.process_config({
            'ABC': 'abc %{DEF}',
            '!DEF': 'def %{GHI} %{JKL}',
            'GHI': 'ghi',
            '!JKL': 'jkl'
            })
        self.assertEqual(len(ids), 2)
        self.assertEqual(ids['ABC'], 'abc def ghi jkl')
        self.assertEqual(ids['GHI'], 'ghi')


if __name__ == '__main__':
    unittest.main()
