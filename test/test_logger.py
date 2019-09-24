from utils.logger import logger
import unittest
import logging
import os

class LoggerTest(unittest.TestCase):
    def test_init(self):
        self.assertTrue(isinstance(logger, logging.Logger))

    def test_info(self):
        logger.info('logger info test')
        info_file = '../log/wendie.INFO.log'
        self.assertTrue(os.path.exists(info_file))

    def test_error(self):
        logger.error('logger error test')
        error_file = '../log/wendie.ERROR.log'
        self.assertTrue(os.path.exists(error_file))


if __name__ == '__main__':
    unittest.main()
