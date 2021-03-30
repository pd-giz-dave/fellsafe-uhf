""" history
    2021-02-01 DCN: created
    2021-03-28 DCN: implement as just a hierarchical dict with set/get accessors
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

import ujson
import uos
import uerrno
import ure
from micropython import const

_root  = const('/flash/store/')          # where in the file system we store our persistent state

_store = {}                              # dict for each path which is a dict of k,v pairs for that path
_dirty = {}                              # True for each path that has changed since the last load/save
_subs  = {}                              # dict for each path which is a dict of k,[f] for that path, where [f] is an array of subscriber functions for that k

def set(path,k,v):
    # set the value of 'k' to 'v' and return what it was before
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
                f(path,k,was,v)          # call subscriber to changes of this k
            except:
                # subscriber failed, log it
                TODO
    except:
        # assume this means there are no subscribers to this k
        pass
    return was

def get(path,k):
    # if path does not exist, it is created
    # if k does not exist in path None is returned
    global _store, _dirty
    if _store[path] is None:
        # its not in memory, see if its in the file system
        _store[path] = load(path)        # returns empty dict if it does not exist
        _dirty[path] = False             # its not dirty
    return _store[path][k]

def load(path):
    # attempt to load the given path
    # on success return a dict of path contents
    # on error return an empty dict
    # each path can reside in the file system multiple times under different revisions
    # we always load the latest revision
    obj = {}                             # default response
    try:
        f = open(_find_latest(path))      # will throw an OSError if does not exist
        obj = ujson.load(f)              # will throw a ValueError if not JSON
    except:
        # this probably means it does not exist in the file system
        # don't care - just return the default response
        pass
    return obj

def save(path):
    # save path to file system if its _dirty
    # return True iff OK
    # return False iff failed (means it was dirty but save failed)
    # this function is fail safe in that it writes the new version before it destroys the oldest
    # each path can have several revisions indicated by a trailing dot number (path.2 etc)
    # physical valid revisions in the file system are in the range 2..n
    # revision 0 is reserved for the new the version being created here and is transient
    # revision 1 is reserved for a holding name meaning "there are no revisions"
    global _store, _dirty
    if _dirty[path] is None:
        # path never been used, so cannot be dirty, so do nothing
        return True
    if not _dirty[path]:
        # its not been changed, so do nothing
        return True
    tempname = _root+path+'.0'
    try:
        f = open(tempname,'w')           # revision 0 is transitory so we don't care if we lose it, opening 'w' is OK
    except OSError as e:
        if e.args[0] == uerrno.ENOENT:
            # this probably means the path does not exist - so make it
            try:
                uos.mkdir(_root)
            except:
                # assume this is dir already exists
                pass
            # now try the open again
            try:
                f = open(tempname,'w')
            except:
        else:
            # oops - log it
            # TODO
            f.close()
            return False
    except Exception as e:
        # oops - log it
        # TODO
        f.close()
        return False
    try:
        f.write(ujson.dumps(_store[path]))
    except e:
        # write failed - log it
        # TODO
        f.close()
        return False
    f.close()
    # we've now written revision 0 OK, so now rename it to the next revision
    nextrev  = int(_find_latest(path).split('.')[-1])+1
    nextname = _root+path+'.'+str(nextrev)
    try:
        uos.rename(tempname,nextname) # NB: the first physical revision will be #2
    except:
        # rename failed - log it
        # TODO
        return False
    # to stop file space being gobbled up, now delete the oldest
    firstname = find_earliest(path)
    if firstname <> nextname:
        # there is an earlier revision, dump it
        try:
            uos.remove(firstname)
        except:
            # don't care
            pass
    return True

def purge(path):
    # remove all revisions of the given path from the file system
    # returns a count of revisions removed
    purged = 0
    for rev in _find_revisions(path)
        try:
            uos.remove(rev)
            purged += 1
        except Exception as e:
            #oops can't delete file, log it
            # TODO
            pass
    return purged

def flush():
    # save all dirty paths
    for path in _dirty:
        if _dirty[path]:
            save(path)

def subscribe(path,k,func):
    # subscribe to changes in the value of k in path by calling func
    # func signature must be: def func(path,k,old_v,new_v)
    # returns the initial value of k
    global _subs
    if _subs[path] is None:
        _subs[path] = {}
    if _subs[path][k] is None:
        _subs[path][k] = []
    _subs[path][k].append(func)
    return get(path,k)

def _find_latest(path):
    # find the latest revision for the given path in the file system
    # returns revision 1 iff none found
    # revision 0 is ignored
    return _find_revisions(path,1)[-1]

def _find_earliest(path):
    # find the earliest revision for the given path in the file system
    # returns revision 1 iff none found
    # revision 0 is ignored
    return _find_revisions(path,1)[0]

def _find_revisions(path,default=None):
    # get a list of revisions for the given path in rev number order
    # iff default is given, it must be an int that defines the revision number
    # and that is returned if there are no revisions in the file system
    # rev 0 is never returned (except as a default)
    revs = []
    try:
        for rev in uos.listdir(_root):
            if ure.match('^'+path+'\.0+',rev):
                # ignore rev 0
                pass
            if ure.match('^'+path+'\.[0-9]+',rev):
                revs.append(rev)
    except:
        # this probably means the store has not been created yet, so there are no revisions
        pass
    if len(revs) == 0 and default is not None:
        revs.append(_root+path+'.'+str(default))
    return sorted(revs)
