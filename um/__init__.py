#!/usr/bin/env python

import os
import re
import sys
import glob
import stat
import shutil
import hashlib
import fnmatch
import logging
import argparse
import subprocess
import ConfigParser
import rarfile

from pymdeco import services


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
        if '.unrar_excludes' in filename: return True
        with open(self.cfgs['path']['excludes'], 'r') as f:
            for line in f:
                if filename in line.strip('\n'):
                    self.logger.debug("excluding file: {0}".format(line))
                    return True
        return False

    def extract(self, args):
        """Walk the dir `path.torrents`, find rar files, extract files.
        Skip files found in the path.exclude file.
        """
        self.logger.info("START extracting files")
        excludes = []
        glob_cmp = '{0}/**/*.rar'.format(self.cfgs['path']['torrents'])
        for filename in glob.iglob(glob_cmp):
            self.logger.debug("extracting filename: {0}".format(filename))
            if not self._in_excludes_file(os.path.basename(filename)) or args.force:
                try:
                    rar = rarfile.RarFile(filename)
                    rar.extractall(path=self.cfgs['path']['extract'])
                    rar.close()
                    excludes.append(os.path.basename(filename))
                except rarfile.NeedFirstVolume as e:
                    pass

        self._write_excludes(excludes)
        self.logger.info("END extracting files")


    def _write_excludes(self, excludes):
        """Write out the excludes file
        """
        if len(excludes) > 0:
            self.logger.debug('writing excludes: {0}'.format(excludes))
            with open(self.cfgs['path']['excludes'], 'a') as f:
                for e in excludes:
                    if not self._in_excludes_file(os.path.basename(e)):
                        f.write('{0}\n'.format(e))


    def copy(self, args):
        """Copy media files from torrent path to extracted path

        NOTE: This will only copy files that are not in the exclude list
        unless of course, the force flag is in play.
        """

        self.logger.info("START copying files")
        dir_dict = {}
        excludes = []

        extensions = self.cfgs['ext']['video'] + ',' + self.cfgs['ext']['audio']

        for ext in extensions.split(','):
            pattern = '*.{0}'.format(ext)
            self.logger.debug('copy pattern: {0}'.format(pattern))
            for root, dirs, files in os.walk(
                        '{0}/'.format(self.cfgs['path']['torrents'])):
                for basename in files:
                    if fnmatch.fnmatch(basename, pattern):
                        filename = os.path.join(root, basename)

                        if not self._in_excludes_file(os.path.basename(filename)) or args.force:

                            try:
                                dest = self.cfgs['path']['extract']
                                self.logger.info("cp {0} -> {1}".format(filename, dest))
                                shutil.copy(filename, dest)
                            except:
                                pass
                            excludes.append(os.path.basename(filename))

        self._write_excludes(excludes)
        self.logger.info("END copying files")


    def extract_and_copy(self, args):
        """Run the extract() and copy() methods back-to-back
        """
        self.extract(args)
        self.copy(args)

    def _get_media_type(self, filename):

        srv = services.FileMetadataService()
        meta = srv.get_metadata(filename)
        return meta['file_type']

    def move(self, args):
        """Move files from extracted path to media paths
        """
        self.logger.info("START moving extracted files")
        dir_dict = {}

        extensions = self.cfgs['ext']['video'] + ',' + self.cfgs['ext']['audio']

        for ext in extensions.split(','):
            pattern = '*.{0}'.format(ext)
            self.logger.debug('move pattern: {0}'.format(pattern))
            for root, dirs, files in os.walk(
                        '{0}/'.format(self.cfgs['path']['extract'])):
                self.logger.debug('walking {0}'.format(self.cfgs['path']['extract']))
                for basename in files:
                    if fnmatch.fnmatch(basename, pattern):
                        filename = os.path.join(root, basename)

                        media_type = self._get_media_type(filename)
                        self.logger.debug("{0} is of type "
                                "'{1}'".format(os.path.basename(os.path.expanduser(filename)),
                                media_type))

                        try:
                            if media_type == 'video':
                                dest = self.cfgs['path']['video']
                            elif media_type == 'audio':
                                dest = self.cfgs['path']['audio']

                            self.logger.info("mv {0} -> {1}".format(filename, dest))
                            shutil.move(filename, dest)
                        except:
                            self.logger.debug("FAILED to mv {0} -> {1}".format(filename, dest))

        self.logger.info("END moving extracted files")

    def remove(self, args):
        """Grab useful information from a repository

        :param str args.name: repository name
        """
        pass

