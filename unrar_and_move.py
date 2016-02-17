import os
import re
import sys
import glob
import stat
import shutil
import hashlib
import logging
import argparse
import subprocess
import ConfigParser

class SmartHelpFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        # this is the RawTextHelpFormatter._split_lines
        if text.startswith('R|'):
            return text[2:].splitlines()
        return argparse.HelpFormatter._split_lines(self, text, width)

class UandC():

    def __init__(self, config_path=None):
        self.cfgs = {}
        self._load_config(config_path)
        self._set_logger()

        self.logger.debug("configs: {0}".format(self.cfgs))

    def _set_logger(self):
        # create logger with 'spam_application'
        self.logger = logging.getLogger('unrar_and_copy')
        self.logger.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        fh = logging.FileHandler(self.cfgs['logger']['file'])
        fh.setLevel(eval(self.cfgs['logger']['level']))

        # create formatter and add it to the handlers
        formatter = logging.Formatter(self.cfgs['logger']['format'])
        fh.setFormatter(formatter)
        # add the handlers to the logger
        self.logger.addHandler(fh)

    def _load_config(self, path='./.uandm.rc'):
        """Constructor for skein, will create self.cfgs and self.logger

        :param str path: skein.cfg path
        """

        config = ConfigParser.SafeConfigParser()
        try:
            f = open(os.path.abspath(os.path.expanduser(path)))
            config.readfp(f)
            f.close()
        except ConfigParser.InterpolationSyntaxError as e:
            raise Exception("Unable to parse config file: {0}".format(e))

        for section in config.sections():
            if not self.cfgs.has_key(section):
                self.cfgs[section] = {}

            for k, v in config.items(section):
                self.cfgs[section][k] = v

    def extract_and_copy(self, args):
        """Grab useful information from a repository

        :param str args.name: repository name
        """
        pass

def main():

    uc = UandC(config_path='./uandc.rc')
    p = argparse.ArgumentParser(
            description=u"Extract and copy torrents",
        )

    p.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
    p.add_argument("-f", "--force", help="force extract and copy actions",
                    action="store_true")

    p.set_defaults(func=uc.extract_and_copy)

    sp = p.add_subparsers()

    p_ex = sp.add_parser("extract", help=u"extract rar files only",
                    formatter_class=SmartHelpFormatter)
    p_cp = sp.add_parser("copy", help=u"copy extracted files only",
                    formatter_class=SmartHelpFormatter)
    p_rm = sp.add_parser("rm", help=u"remove torrents files only",
                    formatter_class=SmartHelpFormatter)
    p_rm.add_argument("t", help=u"remove torrents")
    p_rm.add_argument("v", help=u"remove videos")
    p_rm.add_argument("-a", "--age", nargs="?",
                    metavar='2d', default="2w", const="1y",
                    help=u"R|Age of files to remove.\n\n"
                    "NOTE: When removing files, if --age/-a\n"
                    "is not provided, files of the specified type older\n"
                    "than 1 year will be removed\n\n"
                    "If a value is not passed, files older than \n"
                    "2 weeks will be removed\n\n"
                    "Age can be represented in multiple ways:\n\n"
                    "Days (eg. 2d)\n"
                    "Weeks (eg. 6w)\n"
                    "Months (eg. 3m)\n"
                    "Years (eg. 1y)\n\n")

    args = p.parse_args()

    #excludes = um.get_excludes()

if __name__ == "__main__":
    sys.exit(main())

