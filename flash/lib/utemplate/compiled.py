""" history
    2021-01-30 DCN: created from github master as part of utemplate - see source.py
    """
""" description
    Load the compiled version of a template and return its 'render' function iff it exists.
    The 'load' here is called speculatively by 'source.load' to by-pass the compile function when its already been done.
    If its not been done this will raise an exception that is caught there.
    """
    
class Loader:

    def __init__(self, pkg, dir):
        if dir == ".":
            dir = ""
        else:
            dir = dir.replace("/", ".") + "."
        if pkg and pkg != "__main__":
            dir = pkg + "." + dir
        self.p = dir

    def load(self, name):
        name = name.replace(".", "_")
        return __import__(self.p + name, None, None, (name,)).render   # NB: we're returning the function here, not calling it
