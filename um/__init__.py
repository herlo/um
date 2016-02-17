#!/usr/bin/env python

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


class UandM():

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

    def extract(self, args):
        """Grab useful information from a repository

        :param str args.name: repository name
        """
        pass

    def move(self, args):
        """Grab useful information from a repository

        :param str args.name: repository name
        """
        pass

    def remove(self, args):
        """Grab useful information from a repository

        :param str args.name: repository name
        """
        pass

