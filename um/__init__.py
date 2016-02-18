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

from rarfile import RarFile


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

    def _in_excludes_file(self, filename):
        """Return whether filename is in excludes file

        :param str filename: file to check
        """
        with open(self.cfgs['path']['excludes'], 'r') as f:
            #self.logger.debug("filename: {0}".format(filename))
            for line in f:
                print('line: {0}'.format(line.strip('\n')))
                self.logger.debug("exclude_file: {0}".format(line.strip('\n')))
                return [True if line.strip('\n') == filename else False for line in f ]

    def extract(self, args):
        """Walk the dir `path.torrents`, find rar files, extract files.
        Skip files found in the path.exclude file.
        """
        excludes = []
        glob_cmp = '{0}/**/*.rar'.format(self.cfgs['path']['torrent'])
        for filename in glob.iglob(glob_cmp):
            if not self._in_excludes_file(filename):
                self.logger.debug("extracting filename: {0}".format(filename))
                rar = RarFile(filename)
                rar.extractall(path=self.cfgs['path']['extract'])
                rar.close()
                excludes.append(filename)

        if len(excludes) > 0:
            self.logger.debug('excludes: {0}'.format(excludes))
            with open(self.cfgs['path']['excludes'], 'a') as f:
                for e in excludes:
                    f.write('{0}\n'.format(e))




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

