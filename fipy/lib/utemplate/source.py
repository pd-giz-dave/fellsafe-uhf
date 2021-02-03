""" history
    2021-01-30 DCN: created by copying the github master from https://github.com/pfalcon/utemplate
    2021-02-02 DCN: Add logging
                    apply templates path to included templates
    2021-02-03 DCN: Show template name auto generated file was created from
    """
""" description
    See documentation for utemplate
    (c) 2014-2019 Paul Sokolovsky. MIT license.
    """

from . import compiled

log = None
DEBUG = 0

def set_debug(val):
    global DEBUG, log
    DEBUG = val
    if val:
        import ulogging as logging
        log = logging.getLogger("utemplate")
        log.debug('logging enabled')


class Compiler:

    START_CHAR = "{"
    STMNT = "%"
    STMNT_END = "%}"
    EXPR = "{"
    EXPR_END = "}}"

    def __init__(self, file_in, file_out, indent=0, seq=0, loader=None):
        self.file_in = file_in
        self.file_out = file_out
        self.loader = loader
        self.seq = seq
        self._indent = indent
        self.stack = []
        self.in_literal = False
        self.flushed_header = False
        self.args = "*a, **d"

    def indent(self, adjust=0):
        if not self.flushed_header:
            self.flushed_header = True
            self.indent()
            self.file_out.write("def render%s(%s):\n" % (str(self.seq) if self.seq else "", self.args))
            self.stack.append("def")
        self.file_out.write("    " * (len(self.stack) + self._indent + adjust))

    def literal(self, s):
        if not s:
            return
        if not self.in_literal:
            self.indent()
            self.file_out.write('yield """')
            self.in_literal = True
        self.file_out.write(s.replace('"', '\\"'))

    def close_literal(self):
        if self.in_literal:
            self.file_out.write('"""\n')
        self.in_literal = False

    def render_expr(self, e):
        self.indent()
        self.file_out.write('yield str(' + e + ')\n')

    def parse_statement(self, stmt):
        tokens = stmt.split(None, 1)
        if tokens[0] == "args":
            if len(tokens) > 1:
                self.args = tokens[1]
            else:
                self.args = ""
        elif tokens[0] == "set":
            self.indent(); self.file_out.write(stmt[3:].strip() + "\n")
        elif tokens[0] == "include":
            if not self.flushed_header:
                # If there was no other output, we still need a header now
                self.indent()
            tokens = tokens[1].split(None, 1)
            args = ""
            if len(tokens) > 1:
                args = tokens[1]

            if tokens[0][0] == "{":
                # we've got {{name}}
                name     = tokens[0][2:-2]
                template = self.loader.compiled_path("").replace("/", ".")                         # get the naked path (with a trailing .)
                template = "'"+template+"'+"+name+".replace('.','_')"                              # add our include name suitably transformed
                self.indent(); self.file_out.write("_ = __import__(%s,None,None,1)\n" % template)  # import it ('1' is upy hack)
                self.indent(); self.file_out.write("yield from _.render(%s)\n" % args)
                # the template referenced must be pre-compiled so the above import works
                # we can't do it auto here 'cos we don't know its name, we only know the
                # name of the variable containing it and that is not in scope here.
                return

            # we've got "name"
            name = tokens[0][1:-1]
            with self.loader.input_open(name) as inc:
                self.seq += 1
                c = Compiler(inc, self.file_out, len(self.stack) + self._indent, self.seq)
                inc_id = self.seq
                self.seq = c.compile(name)
            self.indent(); self.file_out.write("yield from render%d(%s)\n" % (inc_id, args))
        elif len(tokens) > 1:
            if tokens[0] == "elif":
                assert self.stack[-1] == "if"
                self.indent(-1); self.file_out.write(stmt + ":\n")
            else:
                self.indent(); self.file_out.write(stmt + ":\n")
                self.stack.append(tokens[0])
        else:
            if stmt.startswith("end"):
                assert self.stack[-1] == stmt[3:]
                self.stack.pop(-1)
            elif stmt == "else":
                assert self.stack[-1] == "if"
                self.indent(-1); self.file_out.write("else:\n")
            else:
                assert False

    def parse_line(self, l):
        while l:
            start = l.find(self.START_CHAR)
            if start == -1:
                self.literal(l)
                return
            self.literal(l[:start])
            self.close_literal()
            sel = l[start + 1]
            #print("*%s=%s=" % (sel, EXPR))
            if sel == self.STMNT:
                end = l.find(self.STMNT_END)
                assert end > 0
                stmt = l[start + len(self.START_CHAR + self.STMNT):end].strip()
                self.parse_statement(stmt)
                end += len(self.STMNT_END)
                l = l[end:]
                if not self.in_literal and l == "\n":
                    break
            elif sel == self.EXPR:
                #print("EXPR")
                end = l.find(self.EXPR_END)
                assert end > 0
                expr = l[start + len(self.START_CHAR + self.EXPR):end].strip()
                self.render_expr(expr)
                end += len(self.EXPR_END)
                l = l[end:]
            else:
                self.literal(l[start])
                l = l[start + 1:]

    def header(self,name):
        self.file_out.write("# {}: Autogenerated file start\n".format(name))

    def footer(self,name):
        self.file_out.write("# {}: Autogenerated file end\n".format(name))

    def compile(self,name):
        self.header(name)
        for l in self.file_in:
            self.parse_line(l)
        self.close_literal()
        self.footer(name)
        return self.seq


class Loader(compiled.Loader):

    def __init__(self, pkg, dir):
        super().__init__(pkg, dir)       # NB: This does an 'import' so it needs the naked pkg not the transformed path

        self.dir = dir
        if pkg == "__main__":
            # if pkg isn't really a package, don't bother to use it
            # it means we're running from "filesystem directory", not
            # from a package.
            pkg = None

        self.pkg_path = ""
        if pkg:
            # import the package so we can find its path
            p = __import__(pkg)
            if isinstance(p.__path__, str):
                # uPy
                self.pkg_path = p.__path__
            else:
                # CPy
                self.pkg_path = p.__path__[0]
            self.pkg_path += "/"

        if __debug__ and DEBUG:
            log.debug('pkg_path: %s, dir: %s',self.pkg_path,self.dir)


    def input_open(self, template):
        return open(self.input_path(template))
        
    def input_path(self, template):
        return self.pkg_path + self.dir + "/" + template

    def compiled_path(self, template):
        return self.pkg_path + self.dir + "/" + template.replace(".", "_")

    def load(self, name):
        if __debug__ and DEBUG:
            log.debug('loading %s',name)
        try:
            # try for the already compiled version first
            return super().load(name)
        except (OSError, ImportError):
            pass

        # compiled version not there, so compile it now
        compiled_path = self.compiled_path(name) + ".py"
        input_path    = self.input_path(name)

        if __debug__ and DEBUG:
            log.debug('compiling %s from %s into %s',name,input_path,compiled_path)

        f_in  = open(input_path)
        f_out = open(compiled_path, "w")
        c = Compiler(f_in, f_out, loader=self)
        c.compile(name)
        f_in.close()
        f_out.close()

        if __debug__ and DEBUG:
            log.debug('loading compiled %s from %s',name,compiled_path)

        return super().load(name)
