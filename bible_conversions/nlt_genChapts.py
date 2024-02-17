from rwt.books import books
import itertools
from html.parser import HTMLParser

ODIR='out'
# ~~~~ from existing wikibibles...
#  {{Bible Old Nav
#  |1=New Living Translation (NLT)
#  |2=Genesis 26
#  |3=[[Genesis 25 (NLT)|GEN 25]]
#  |4=[[Genesis 27 (NLT)|GEN 27]]}}

# <span id="V1"><sup>'''1'''</sup></span>&nbsp;

# ~~~~~~~
def vnum(n):
    """Generate a verse number string for the text"""
    return f'<span id="V{n}"><sup>\'\'\'{n}\'\'\'</sup></span>&nbsp;'

def heading(title):
    """Generate a heading in the text"""
    return f'== {title} =='

def prev_chap(bnum,cnum):
    """Determine the previous chapter from the current one. Returns None if there isn't one!"""
    if cnum == 0:
        if bnum == 0: return (None,None)
        bnum = bnum - 1
        cnum = len(books[bnum]['chapters'])
    return (bnum, cnum - 1)

def next_chap(bnum,cnum):
    """Determine the next chapter from the current one. Returns None if there isn't one!"""
    cnum = cnum + 1
    if cnum == len(books[bnum]['chapters']):
        bnum, cnum = bnum + 1, 0
        if bnum == len(books): return (None,None)
    return (bnum, cnum)

def make_short_link(bnum,cnum):
    """Make a short link from a book and chapter number"""
    if bnum is None:
        return '[[New Living Translation (NLT)|Contents]]'
    s,l  = books[bnum]['short'], books[bnum]['long']
    c,sc = books[bnum]['chapters'][cnum]['title'], None
    if c == 'Introduction': sc = 'Intro'
    return f"[[{l} {c} (NLT)|{s} {sc or c}]]"

def make_long_link(bnum,cnum):
    """Make a long link from a book and chapter number"""
    if bnum is None:
        return '[[New Living Translation (NLT)|Contents]]'
    l,c = books[bnum]['long'], books[bnum]['chapters'][cnum]['title']
    return f"[[{l} {c} (NLT)|{l} {c}]]"

def generate_nav(bnum, cnum):
    cbook = books[bnum]
    prev_link = make_short_link(*prev_chap(bnum,cnum))
    next_link = make_short_link(*next_chap(bnum,cnum))
    return f'''{{{{Bible  {cbook['testament']} Nav
|1=New Living Translation (NLT)
|2={cbook['long']} {cbook['chapters'][cnum]['title']}
|3={prev_link}
|4={next_link}
}}}}'''

def make_chapter_filename(bnum,cnum):
    """Generate the correct output file name"""
    cbook = books[bnum]
    return f"{ODIR}/{cbook['long'].replace(' ','_')}_{cbook['chapters'][cnum]['title']}_(NLT).wikitext"

class ParseStrat: # parser strategies...
    """ParseStrat derivatives are strategies for HTMLParsers to use. They are (mostly) stateless and always return what the
    next state should be."""
    def stag(self, parent, tag, attrs):
        return self 
    def etag(self, parent, tag):
        return self
    def data(self, parent, data):
        return self

## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Note Text ParseStrats ~~~~~~~~~~~~~~~~~~~~
class PassThruA(ParseStrat):
    def __init__(self, notepara):
        self._notepara = notepara
        self._txt = []
    def data(self, parent, data):
        self._txt.append(data)
        return self
    def etag(self, parent, tag):
        if tag == 'a':
            self._notepara.add(''.join(self._txt))
            return self._notepara
        return self

class NotePara(ParseStrat):
    def __init__(self):
        self._id = None
        self._txt = []
    def add(self, txt):
        self._txt.append(txt)
    def stag(self, parent, tag, attrs):
        match tag:
            case 'a': 
                self._id = parent.attr(attrs,'id')
                if not self._id:
                    raise RuntimeError("note paragraph with no id!")
                return PassThruA(self)
            case 'i' | 'em':
                self.add("''")
            case 'b' | 'strong':
                self.add("'''")
        return self 
    def etag(self, parent, tag):
        match tag:
            case 'p':
                parent.add_note(self._id,''.join(self._txt))
                return NoteDiv()
            case 'i' | 'em':
                self.add("''")
            case 'b' | 'strong':
                self.add("'''")
        return self
    def data(self, parent, data):
        self.add(data)
        return self

class NoteDiv(ParseStrat):
    def stag(self, parent, tag, attrs):
        if tag == 'p' and parent.attr(attrs,'class') == 'bible-text-note':
            return NotePara()
        return self 
    def etag(self, parent, tag):
        if tag == 'div':
            return WaitForNoteDiv() 
        return self
    
class WaitForNoteDiv(ParseStrat):
    def stag(self, parent, tag, attrs):
        if tag == 'div' and parent.attr(attrs,'class') == 'note':
            return NoteDiv()
        return self 

class NotesManager(HTMLParser):
    def __init__(self):
        super().__init__()
        self._loaded = set() 
        self._notes = dict() 
        self._state = WaitForNoteDiv()

    def add_note(self, noteid, note):
        """Add a note keyed by noteid to the store"""
        if noteid in self._notes:
            raise RuntimeError(f'Duplicate noteid {noteid}!')
        self._notes[noteid] = note

    def load_notes(self, fname):
        """Load the file fname, and remember we did!"""
        if fname in self._loaded: return
        self.reset()
        self._state = WaitForNoteDiv()
        with open(fname,'r') as infile:
            self.feed(infile.read())
            self.close()
        self._loaded.add(fname)

    def get_note(self, noteid):
        return self._notes[noteid]

    def attr(self, attrs, key):
        """Get the attribute from attrs matching `key`, or None"""
        _,val = next(filter(lambda a: a[0] == key, attrs),(None,None)) 
        # RWT print(f'Attributes are {attrs}, got {val} for {key}.')
        return val

    def handle_starttag(self, tag, attrs):
        self._state = self._state.stag(self, tag, attrs) 
        # print('after start',tag,'now state is',self._state) #RWT

    def handle_endtag(self, tag):
        self._state = self._state.etag(self, tag) 
        # print('after end',tag,'now state is',self._state) #RWT

    def handle_data(self, data):
        self._state = self._state.data(self, data) 
        # print('after data',data[0:5],'now state is',self._state) #RWT

# <div class="note">
#   <p class="bible-text-note"><a href="x1genesis_1.html#note_marker_2" id="note_2">[<span class="tn-ref">1:26a</span>]</a>  Or <em>man;</em> Hebrew reads <em>adam.</em></p>
# </div>


## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Body Text ParseStrats ~~~~~~~~~~~~~~~~~~~~
class WaitForP(ParseStrat):
    """Waiting for a paragraph to appear"""
    def stag(self, parent, tag, attrs):
        if tag == 'p':
            clz = parent.attr(attrs,'class')
            # if it is not
            match clz:
                case 'subhead':
                    return SubHeading(parent)
                case 'chapter-number': return self  #skip it!
                case p if p.find('poet') >= 0:
                    return PoetryParagraph(parent, p.split('-'))
                case _: 
                    return Paragraph(parent)
        return self 

class VerseNumber(ParseStrat):
    def __init__(self, prevState):
        self._prevState = prevState
    def stag(self, parent, tag, attrs):
        raise RuntimeError(f"Should never have a start tag in VerseNumber but got <{tag}>!")
    def data(self, parent, data):
        parent.output(vnum(data))
        parent.eat_whitespace()
        return self
    def etag(self, parent, tag):
        if tag == 'span':
            return self._prevState
        raise RuntimeError(f"Should only have closing </span> in VerseNumber but got </{tag}>!")

class FakeSmallCaps(ParseStrat):
    def __init__(self, prevState):
        self._prevState = prevState
    def data(self, parent, data):
        parent.output(data.lower())
        return self
    def etag(self, parent, tag):
        if tag == 'span':
            return self._prevState
        raise RuntimeError(f"Should only have closing </span> in FakeSmallCaps but got </{tag}>!")

class SmallCaps(ParseStrat):
    def __init__(self, prevState, parent):
        self._prevState = prevState
        parent.output('{{Smallcaps|')
    def data(self, parent, data):
        parent.output(data)
        return self
    def stag(self, parent, tag, attrs):
        if tag == 'span' and parent.attr(attrs,'class') == 'cs-fake-sc':
            return FakeSmallCaps(self)
        raise RuntimeError(f"Should never have a start tag in smallcaps but got <{tag}>!")
    def etag(self, parent, tag):
        if tag == 'span':
            parent.output('}}')
            return self._prevState
        raise RuntimeError(f"Should only have closing </span> in smallcaps but got </{tag}>!")

class NoteMarker(ParseStrat):
    def __init__(self, prevState):
        self._prevState = prevState
    def data(self, parent, data):
        if data == '[*]':
           parent.output('<sup>[*]</sup>')
           return self
        raise RuntimeError(f"Should only get [*] in a note, but got <{data}>!")
    def stag(self, parent, tag, attrs):
        if tag == 'a' and (href := parent.attr(attrs,'href')):
            html_file,note_name = href.split('#',1)
            parent.add_note(html_file, note_name)
            return self
        raise RuntimeError(f"Should never have a start tag in NoteMarker but got <{tag} with attrs <{attrs}>!")
    def etag(self, parent, tag):
        match tag:
            case 'span': return self._prevState
            case 'a': return self # skip!
            case _: raise RuntimeError(f"Should only have closing </a>,</span> in NoteMarker but got </{tag}>!")

class Paragraph(ParseStrat):
    def __init__(self, parent, poetic=False):
        self._in_sup = False
        self._in_sub = False
        if poetic:
            parent.start_poetry()
        else:
            parent.end_poetry()
    def stag(self, parent, tag, attrs):
        # look for verse numbers...
        if tag == 'span': 
            match parent.attr(attrs,'class'):
                case 'vn': return VerseNumber(self)
                case 'sc' | 'subhead-sc': return SmallCaps(self, parent)
                case 'note_marker': return NoteMarker(self)
                case 'fract-den':
                    parent.output('<sub>')
                    self._in_sub = True
                    return self
                case 'fract-slash':
                    return self
        elif tag == 'a':
            if parent.attr(attrs,'id'):
                return self  # skip on purpose!
        elif tag == 'sup' and parent.attr(attrs,'class') == 'fract-num':
            parent.output('<sup>')
            self._in_sup = True
            return self
        elif tag == 'em':
            parent.output("''")
            return self
        print(f'warning...unhandled tag <{tag} {attrs}> in paragraph...')
        return self
    def data(self, parent, data):
        parent.output(data)
        return self
    def etag(self, parent, tag):
        if tag == 'p':
            parent.output('\n\n')
            return WaitForP()
        elif tag == 'sup' and self._in_sup:
            parent.output('</sup>')
            self._in_sup = False
        elif tag == 'span' and self._in_sub:
            parent.output('</sub>')
            self._in_sub = False
        elif tag == 'em':
            parent.output("''")
            return self
        return self

class SubHeading(Paragraph):
    def __init__(self,parent):
        super().__init__(parent)
        parent.output_notes()
        parent.output('== ')
    def etag(self, parent, tag):
        if tag == 'p':
            parent.output(' ==\n')
            return WaitForP()
        raise RuntimeError(f"Should only have closing </p> in SubHeading but got </{tag}>!")

class PoetryParagraph(Paragraph):
    def __init__(self, parent, parts):
        if 'sp' in parts: parent.space_poetry()  # must do this before super()
        super().__init__(parent, poetic=True)
        indent = 4  # in ems
        if 'vn' in parts: indent = indent - 1 
        if 'ext' in parts: indent = indent + 1
        if 'poet2' in parts: indent = indent + 2
        if 'poet3' in parts: indent = indent + 4
        parent.output(f'<span style="padding-left: {indent}em">')
    def etag(self, parent, tag):
        if tag == 'p':
            parent.output('</span><br/>\n')
            return WaitForP()
        return self

class ChapParser(HTMLParser):
    def __init__(self, ofile):
        super().__init__()
        self._ofile = ofile
        self._state = WaitForP() 
        self._eating_whitespace = False
        self._in_poetry = False
        self._note_q = []
        self._note_mgr = NotesManager()

    def close(self):
        super().close()
        self.output_notes()

    def attr(self, attrs, key):
        """Get the attribute from attrs matching `key`, or None"""
        _,val = next(filter(lambda a: a[0] == key, attrs),(None,None)) 
        # RWT print(f'Attributes are {attrs}, got {val} for {key}.')
        return val

    def eat_whitespace(self):
        self._eating_whitespace = True

    def start_poetry(self):
        self._in_poetry = True

    def space_poetry(self):
        """When we get a -sp class, we need to space out the poetry, if we were already in it"""
        if self._in_poetry:
            self.output('\n\n')

    def end_poetry(self):
        """If we were in poetry, end it here"""
        if self._in_poetry:
            self._in_poetry = False
            self.output('\n')

    def output(self, s):
        """Pass data to the output file"""
        if self._eating_whitespace:
            s = s.lstrip()
            self._eating_whitespace = False
        self._ofile.write(s)

    def add_note(self, fname, noteid):
        """Load all notes from fname (unless we already have) and
        queue noteid for inclusion in the text"""
        self._note_mgr.load_notes('OEBPS/' + fname)
        self._note_q.append(noteid)

    def output_notes(self):
        """Output all queued notes"""
        if len(self._note_q) == 0: return
        self.output('<div style="background: #eeeeee; border-left: 2px solid black; padding-left: 0.5em;">')
        for n in self._note_q:
            self._ofile.write(self._note_mgr.get_note(n))
            self._ofile.write('\n\n')
        self.output('</div>\n\n')
        self._note_q.clear()

    def handle_starttag(self, tag, attrs):
        self._state = self._state.stag(self, tag, attrs) 
        # print('after start',tag,'now state is',self._state) #RWT

    def handle_endtag(self, tag):
        self._state = self._state.etag(self, tag) 
        # print('after end',tag,'now state is',self._state) #RWT

    def handle_data(self, data):
        self._state = self._state.data(self, data) 
        # print('after data',data[0:5],'now state is',self._state) #RWT

def parse_chapter(cfname, ofile):
    """Parse the chapter given by `cfname`, writing wikitext to `ofile`"""
    with open('OEBPS/' + cfname,'r') as ifile:
        cp = ChapParser(ofile)
        cp.feed(ifile.read())
        cp.close()

def generate_chapter(bnum, cnum):
    """Generate a whole chapter's text"""
    with open(make_chapter_filename(bnum,cnum),'w') as ofile:
        print(generate_nav(bnum,cnum),file=ofile)
        parse_chapter(books[bnum]['chapters'][cnum]['file'],ofile)
        print(f'\n&rarr; {make_long_link(*next_chap(bnum,cnum))} &rarr;',file=ofile)
        print('[[Category:Bible Texts (NLT)]]', file=ofile)

def generate_all():
    """Go through all the books and chapters, generating text"""
    for book in range(len(books)):
        for chap in range(len(book['chapters'])):
            generate_chapter(book,chap)

