""" history
    2021-02-01 DCN: created
    2021-03-28 DCN: implement as just a hierarchical dict with set/get accessors
    2021-04-01 DCN: Add _test
    2021-04-05 DCN: Make compatible with running under the emulator
    """
""" description
    all system state is accessed through here
    both volatile and persistent
    set/get are volatile
    load/store transfers a path from/to the file store
    for the moment its just a crude two-level dictionary: path --> key --> value
    for volatile its just an in-memory dict
    for persistent its a folder: /flash/store in which there is a file for each path
    whose contents is just a stringified (ie. JSON) key --> value dictionary.
    load transfers a specific path from the file system into memory
    save does the opposite
    so to change a value and make it persistent requires to operations: set, then save
    and to access it for the first time requires: load then get (but see below)
    load is lazy, it only does it once
    save is also lazy in that it will not do it if nothing has changed
    any set/get to a path that has been previously saved will re-load it
    """

import config

import ujson as json
import os
import uerrno as errno
import ure as re

_root  = config.root()+'flash/store'     # where in the file system we store our persistent state

_store = {}                              # dict for each path which is a dict of k,v pairs for that path
_dirty = {}                              # True for each path that has changed since the last load/save
_subs  = {}                              # dict for each path which is a dict of k,[f] for that path, where [f] is an array of subscriber functions for that k

DEBUG = 0
log   = None

def set_debug(val):
    global DEBUG, log
    DEBUG = val
    if val:
        import ulogging as logging
        log = logging.getLogger(__name__)
        log.info('logging enabled')

def clean(*,volatile=False,persistent=False,subscribers=False):
    """ clean (i.e. remove) volatile and/or persistent state and/or subscribers
        returns True iff succeeded
        """
    global _store,_dirty,_subs
    OK = True
    if volatile:
        _store = {}
        _dirty = {}
    if subscribers:
        _subs  = {}
    if persistent:
        for path in _find_paths():
            purge(path)
        try:
            os.rmdir(_root)
        except OSError as e:
            if e.args[0] == errno.ENOENT:
                # this means it did not exist, so OK
                pass
            else:
                # oops, sumink else wrong
                if log is not None:
                    log.exc(e,'clean(1): {} not empty'.format(_root))
                OK = False
        except Exception as e:
            # oops, directory not empty, log it
            if log is not None:
                log.exc(e,'clean(2): {} not empty'.format(_root))
            OK = False
    return OK

def set(path,k,v):
    """ set the value of 'k' to 'v' and return what it was before
        """
    global _store, _dirty
    was = get(path,k)
    if was == v:
        # not changing, do nothing
        return was
    _store[path][k] = v                  # set new value
    _dirty[path]    = True               # note its changed
    try:
        for f in _subs[path][k]:
            try:
                f[0](f[1],path,k,was,v)  # call subscriber to changes of this k
            except Exception as e:
                # subscriber failed, log it
                if log is not None:
                    log.exc(e,'set: subscriber to {} in path {} failed'.format(k,path))
    except:
        # assume this means there are no subscribers to this k
        pass
    return was

def get(path,k):
    """ if path does not exist, it is created
        if k does not exist in path None is returned
        """
    global _store
    try:
        test = _store[path]
    except KeyError:
        # its not in memory, try to load from the file system
        load(path)
    try:
        return _store[path][k]
    except KeyError:
        return None

def subscribe(path,k,func,context):
    """ subscribe to changes in the value of k in path by calling func with context as 1st param (usually self)
        func signature must be: def func(context,path,k,old_v,new_v)
        or: Thing class; def func(self,path,k,old_v,new_v)
        returns the current value of k
        """
    global _subs
    if _subs.get(path) is None:
        _subs[path] = {}
    if _subs[path].get(k) is None:
        _subs[path][k] = []
    _subs[path][k].append([func,context])      # TODO: check for duplicates
    return get(path,k)

def load(path):
    """ attempt to load the given path into the store
        this completely replaces the current store for the given path
        returns True if the store was loaded from the file system
        returns False (and sets the store empty) if not loaded (for any reason)
        each path can reside in the file system multiple times under different revisions
        we always load the latest revision
        NB: the first 'get' for anything in a path triggers a load attempt on it
        """
    global _store, _dirty
    _dirty[path] = False                 # set its not dirty
    latest = _root+'/'+_find_latest(path)# find the latest version to load
    try:
        f = open(latest)                 # will throw an OSError if does not exist
        _store[path] = json.load(f)     # will throw a ValueError if not JSON
        return True                      # tell caller its there
    except Exception as e:
        # this probably means it does not exist in the file system
        _store[path] = {}                # set an empty store
        return False                     # tell caller its not there

def save(path):
    """ save path to file system if its _dirty
        return True iff OK
        return False iff failed (means it was dirty but save failed)
        this function is fail safe in that it writes the new version before it destroys the oldest
        each path can have several revisions indicated by a trailing dot number (path.2 etc)
        physical valid revisions in the file system are in the range 2..n
        revision 0 is reserved for the new the version being created here and is transient
        revision 1 is reserved for a holding name meaning "there are no revisions"
        """
    global _store, _dirty
    if _dirty.get(path) is None:
        # path never been used, so cannot be dirty, so do nothing
        return True
    if not _dirty[path]:
        # its not been changed, so do nothing
        return True
    tempname = _root+'/'+path+'.0'
    try:
        f = open(tempname,'w')           # revision 0 is transitory so we don't care if we lose it, opening 'w' is OK
    except OSError as e:
        if e.args[0] == errno.ENOENT:
            # this probably means the path does not exist - so make it
            try:
                os.mkdir(_root)
            except OSError as e:
                if e.args[0] == errno.EEXIST:
                    # dir already exists, that's OK
                    pass
                else:
                    # oops
                    if log is not None:
                        log.exc(e,'save: cannot create dir {}'.format(_root))
                    return False
            # now try the open again
            try:
                f = open(tempname,'w')
            except Exception as e:
                # oops, cannot open even after created the root folder - log it
                if log is not None:
                    log.exc(e,'save: cannot create path {}'.format(tempname))
                return False
        else:
            # oops - log it
            if log is not None:
                log.exc(e,'save: cannot access {}'.format(_root))
            return False
    except Exception as e:
        # oops - log it
        if log is not None:
            log.exc(e,'save: (2)cannot access {}'.format(_root))
        return False
    try:
        f.write(json.dumps(_store[path]))
    except Exception as e:
        # write failed - log it
        if log is not None:
            log.exc(e,'save: cannot write json of path {} to {}'.format(path,tempname))
        f.close()
        return False
    f.close()
    # we've now written revision 0 OK, so now rename it to the next revision
    nextrev  = int(_find_latest(path).split('.')[-1])+1
    nextname = _root+'/'+path+'.'+str(nextrev)
    try:
        os.rename(tempname,nextname) # NB: the first physical revision will be #2
    except Exception as e:
        # rename failed - log it
        if log is not None:
            log.exc(e,'save: cannot rename {} to {}'.format(tempname,nextname))
        return False
    # to stop file space being gobbled up, now delete the oldest
    firstname = _root+'/'+_find_earliest(path)
    if firstname != nextname:
        # there is an earlier revision, dump it
        try:
            os.remove(firstname)
        except:
            # don't care
            pass
    _dirty[path] = False                 # its clean now
    return True

def flush():
    """ save all dirty paths
        return count of dirty paths found and saved
        """
    flushed = 0
    for path in _dirty:
        if _dirty[path]:
            save(path)
            flushed += 1
    return flushed

def purge(path):
    """ remove all revisions of the given path from the file system
        returns a count of revisions removed
        """
    purged = 0
    for rev in _find_revisions(path,find_all=True):
        rev = _root+'/'+rev
        try:
            os.remove(rev)
            purged += 1
        except Exception as e:
            # oops can't delete file, log it, but otherwise don't care
            if log is not None:
                log.exc(e,'purge: cannot remove {} from {}'.format(rev,_root))
            pass
    return purged

def _find_latest(path):
    """ find the latest revision for the given path in the file system
        returns revision 1 iff none found
        revision 0 is ignored
        """
    return _find_revisions(path,1)[-1]

def _find_earliest(path):
    """ find the earliest revision for the given path in the file system
        returns revision 1 iff none found
        revision 0 is ignored
        """
    return _find_revisions(path,1)[0]

def _find_revisions(path,default=None,*,find_all=False):
    """ get a list of revisions for the given path in rev number order
        iff default is given, it must be an int that defines the revision number
        and that is returned if there are no revisions in the file system
        rev 0 is never returned (except as a default) unless find_all is asserted
        """
    revs = []
    try:
        for rev in os.listdir(_root):
            if not find_all and re.match('^'+path+'\.0+',rev):
                # ignore rev 0
                pass
            if re.match('^'+path+'\.[0-9]+',rev):
                revs.append(rev)
    except:
        # this probably means the store has not been created yet, so there are no revisions
        pass
    if len(revs) == 0 and default is not None:
        revs.append(path+'.'+str(default))
    return sorted(revs)

def _find_paths():
    """ find all paths in the file system _store
        a 'path' is anything with a numeric extension (without the extension)
        """
    paths = []
    try:
        for path in os.listdir(_root):
            match = re.match('(.*)\.[0-9]+$',path)
            if match:
                path = match.group(1)
                is_dup = False
                for dup in paths:
                    if dup == path:
                        is_dup = True
                        break
                if not is_dup:
                    paths.append(path)
    except:
        # this probably means the store has not been created yet, so there are no paths
        pass
    return sorted(paths)

def _test():
    """ test everything, from nothing
        """

    set_debug(True)
    import tester

    def change_callback(context,path,k,was,now):
        context['path'] = path
        context['k'   ] = k
        context['was' ] = was
        context['now' ] = now

    def check_callback(context,path,k,was,now):
        result = ''
        if context.get('path') != path:
            result += ' & expected path {}, got {}'.format(path,context.get('path'))
        if context.get('k')    != k:
            result += ' & expected k {}, got {}'.format(k,context.get('k'))
        if context.get('was')  != was:
            result += ' & expected was {}, got {}'.format(was,context.get('was'))
        if context.get('now')  != now:
            result += ' & expected now {}, got {}'.format(now,context.get('now'))
        if result == '':
            result = 'OK'
        return result

    # start from nothing
    clean(volatile=True,persistent=True,subscribers=True)

    context = {} # for subscriber test
    tests = [
        # test name,expected result,function to call,[(function positional parameters...,),][{function keyword parameters...,}]
        # set/get
        ('get-not-exist'          ,None        ,get,('test','key',)),
        ('set-initial'            ,None        ,set,('test','key','exists',)),
        ('get-exists'             ,'exists'    ,get,('test','key',)),
        # subscriber
        ('subscribe'              ,'exists'    ,subscribe,('test','key',change_callback,context),),
        ('change-a-value'         ,'exists'    ,set,('test','key','not exists',)),
        ('check-subscriber-called','OK'        ,check_callback,(context,'test','key','exists','not exists',)),
        # load/save
        ('load-nothing'           ,False       ,load,('nothing',)),
        ('save-test'              ,True        ,save,('test',)),
        ('set-a-change'           ,'not exists',set,('test','key','not saved',)),
        ('check-the-set'          ,'not saved' ,get,('test','key',)),
        ('load-saved'             ,True        ,load,('test',)),
        ('check-saved'            ,'not exists',get,('test','key',)),
        # flush/purge/clean
        ('set-another-path'       ,None        ,set,('test2','key2','something',)),
        ('flush'                  ,1           ,flush),
        ('purge'                  ,1           ,purge,('test',)),
        ('clean'                  ,True        ,clean,{'persistent':True,}),
        ('purge-is-empty'         ,0           ,purge,('test',))
    ]
    failures = tester.run(__name__,tests,stop_on_fail=True)

    # tidy up (unless there are failures, then leave the evidence)
    if failures == 0:
        clean(volatile=True,persistent=True,subscribers=True)
