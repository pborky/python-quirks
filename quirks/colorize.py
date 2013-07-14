
try:
    from fabulous.color import bold,italic,underline,strike,blink,flip, \
                                black,red,green,yellow,blue,magenta,cyan,white ,\
                                highlight_black,highlight_red,highlight_green,highlight_yellow,highlight_blue,\
                                highlight_magenta,highlight_cyan,highlight_white
    from functional import *
    boldblack = combinator(bold ,black)
    boldred = combinator(bold ,red)
    boldgreen = combinator(bold ,green)
    boldyellow = combinator(bold ,yellow)
    boldblue = combinator(bold ,blue)
    boldmagenta = combinator(bold ,magenta)
    boldcyan = combinator(bold ,cyan)
    boldwhite = combinator(bold ,white)
    eraserest = lambda x:'\033[K'
except ImportError:
    print 'fabulous not found, colors are disabled'
    highlight_black=highlight_red=highlight_green=highlight_yellow=highlight_blue=\
    highlight_magenta=highlight_cyan=highlight_white=bold=italic=underline=strike=\
    blink=flip=black=red=green=yellow=blue=magenta=cyan=white =\
    boldblack,boldred,boldgreen,boldyellow,boldblue,boldmagenta,boldcyan,boldwhite = lambda x:x
    


class colorize(object):
    def __init__(self,*colors):
        import re
        self.colors = colors
        # format mini-language
        self.fml = re.compile(r'(?:(##)|#([^#]+)#|(%(?:[^{}]?(?:<|>|\+|^))?(?:\+|-|\s)?#?0?(?:[0-9]+)?,?(?:[.][0-9]+)?(?:b|c|d|e|E|f|F|g|G|n|o|s|x|X)))')
    def __iter__(self):
        return iter(self.colors)
    def _rainbow(self):
        class Rainbow:
            def __init__(self,iter):
                self.iter = iter
            def _apply_color(self,s):
                try:
                    color = self.iter.next()
                    return unicode(color(s)) if callable(color) else s
                except StopIteration:
                    return s
            def __call__(self, matcher):
                return self._apply_color(reduce(lambda a,x:x,filter(None,matcher.groups()),None))


        return Rainbow(iter(self))

    def __mul__(self, s):
        return self.fml.sub(self._rainbow(),s)
