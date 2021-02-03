""" history
    2021-01-30 DCN: created from github master as part of utemplate - see source.py
    2021-02-02 DCN: Add __init__ so can use this loader as the 'top' from picoweb
                    Use self.input_path() not DIY
                    self.compiled_path() now does not add the .py extension, so do it here
    2021-02-03 DCN: Add logging
    """
""" description
    Force re-compile of a template by removing the existing compiled version
    (c) 2014-2020 Paul Sokolovsky. MIT license.
    """

from os import stat, remove
from . import source


class Loader(source.Loader):

    def __init__(self, pkg, dir):
        super().__init__(pkg, dir)

    def load(self, name):
        o_path = self.compiled_path(name) + '.py'
        i_path = self.input_path(name)
        if __debug__ and source.DEBUG:
            source.log.debug('recompile.load: try %s from %s',i_path,o_path)
        try:
            o_stat = stat(o_path)
            i_stat = stat(i_path)
            if i_stat[8] > o_stat[8]:
                # input file is newer, remove output to force recompile
                remove(o_path)
                if __debug__ and source.DEBUG:
                    source.log.debug('recompile.load: removed out of date %s',o_path)
        except OSError:
            if __debug__ and source.DEBUG:
                source.log.debug('recompile.load: not compiled yet %s',i_path)
        finally:
            return super().load(name)
