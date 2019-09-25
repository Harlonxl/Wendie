import unittest
from utils import utils

class UtilsTest(unittest.TestCase):
    def test_shortkey(self):
        key = utils.shortkey('https://pan.baidu.com/s/1NIwb1Rp3brvTXuVVlClZsg')
        self.assertEqual(key, '1NIwb1Rp3brvTXuVVlClZsg')