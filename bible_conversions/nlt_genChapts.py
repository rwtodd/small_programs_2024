from rwt.books import books,target_lookup
import itertools
from html.parser import HTMLParser
from io import StringIO
import re

ODIR='out'

# ~~~~~~~
def vnum(n):
    """Generate a verse number string for the text"""
    match n.split('-'):
        case [vstart,vend]:
            anchors = ''.join(f'<span id="V{x}"></span>' for x in range(int(vstart),int(vend)))
            return anchors + f'<span id="V{vend}"><sup>\'\'\'{n}\'\'\'</sup></span>&nbsp;'
        case [vnum]:
            return f'<span id="V{n}"><sup>\'\'\'{n}\'\'\'</sup></span>&nbsp;'
        case _:
            raise RuntimeError(f"vnum called on {n}!")

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

#  args: 1 = Title, 2 = ToC Link, 3 = prev link, 4 = next link
def generate_intro_nav(bnum, cnum):
    cbook = books[bnum]
    test = cbook['testament']
    if not test.startswith('Apoc'):
        test = test + ' Testament'
    prev_link = make_short_link(*prev_chap(bnum,cnum))
    next_link = make_short_link(*next_chap(bnum,cnum))
    return f'''{{{{Generic WikiBook Nav
|1={cbook['long']} ({test})
|2=[[New Living Translation (NLT)]]
|3={prev_link}
|4={next_link}
}}}}'''

def generate_nav(bnum, cnum):
    cbook = books[bnum]
    prev_link = make_short_link(*prev_chap(bnum,cnum))
    next_link = make_short_link(*next_chap(bnum,cnum))
    return f'''{{{{Bible {cbook['testament']} Nav
|1=New Living Translation (NLT)
|2={cbook['long']} {cbook['chapters'][cnum]['title']}
|3={prev_link}
|4={next_link}
}}}}'''

def make_chapter_filename(bnum,cnum):
    """Generate the correct output file name"""
    cbook = books[bnum]
    return f"{ODIR}/{cbook['long']}_{cbook['chapters'][cnum]['title']}_(NLT).wikitext".replace(' ','_')

class ParseStrat: # parser strategies...
    """ParseStrat derivatives are strategies for HTMLParsers to use. They are (mostly) stateless and always return what the
    next state should be."""
    def stag(self, parent, tag, attrs):
        return self 
    def etag(self, parent, tag):
        return self
    def data(self, parent, data):
        return self

## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Note Text-Specific ParseStrats ~~~~~~~~~~~~~~~~~~~~
class NoteDiv(ParseStrat):
    def stag(self, parent, tag, attrs):
        if tag == 'p' and parent.attr(attrs,'class') == 'bible-text-note':
            return NotePara(self, parent)
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
        self._eating_whitespace = False
        self._in_poetry = False
        self._txtbuf = []

    def add_note_from_output(self, noteid):
        """Add a note keyed by noteid to the store"""
        if not noteid:
            raise RuntimeError(f'false noteid was {noteid}!')
        if noteid in self._notes:
            raise RuntimeError(f'Duplicate noteid {noteid}!')
        self._notes[noteid] = self.get_textbuf()

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

    def eat_whitespace(self):
        self._eating_whitespace = True

    def start_poetry(self):
        self._in_poetry = True

    def space_poetry(self):
        """When we get a -sp class, we need to space out the poetry, if we were already in it"""
        if self._in_poetry:
            self.output('\n\n') # should make a total of 3 newlines for 2 blank lines

    def end_poetry(self):
        """If we were in poetry, end it here"""
        if self._in_poetry:
            self._in_poetry = False
            self.output('\n')

    def output(self, s):
        """Store data for inclusion in a note"""
        if self._eating_whitespace:
            s = s.lstrip()
            self._eating_whitespace = False
        self._txtbuf.append(s)

    def get_textbuf(self):
        """Join all the text so far added to _txtbuf, and return it. clear the _txtbuf"""
        tb = ''.join(self._txtbuf)
        self._txtbuf.clear()
        self._eating_whitespace = False
        self._in_poetry = False
        return tb

    def add_note(self, fname, noteid):
        pass

    def output_notes(self):
        """Output all queued notes"""
        pass


    def handle_starttag(self, tag, attrs):
        self._state = self._state.stag(self, tag, attrs) 
        # print('after start',tag,'now state is',self._state) #RWT

    def handle_endtag(self, tag):
        self._state = self._state.etag(self, tag) 
        # print('after end',tag,'now state is',self._state) #RWT

    def handle_data(self, data):
        self._state = self._state.data(self, data) 
        # print('after data',data[0:5],'now state is',self._state) #RWT


## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Body Text ParseStrats ~~~~~~~~~~~~~~~~~~~~
class WaitForP(ParseStrat):
    """Waiting for a paragraph to appear"""
    def __init__(self):
        self._found = False
    def stag(self, parent, tag, attrs):
        if tag == 'hr' and parent.attr(attrs,'class') == 'text-critical':
            parent.end_poetry()
            parent.output_notes()
            parent.output('----\n\n')   
            return self
        elif tag == 'p':
            self._found = True
            clz = parent.attr(attrs,'class')
            match clz:
                case None:
                    return Paragraph(self, parent)
                case 'subhead':
                    return SubHeading(self, parent)
                case 'chapter-number': 
                    self._found = False # not at the good stuff yet
                    return self  #skip it!
                case p if p.find('poet') >= 0 or p.find('list') >= 0:
                    return PoetryParagraph(self, parent, p.split('-'))
                case _: 
                    return Paragraph(self, parent)
        elif tag == 'a' and parent.attr(attrs,'href') is None:
            return self # just skip it silently
        if self._found: print(f"just ignoring tag <{tag} {attrs}> after finding a paragraph...")
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
    def __init__(self, prevState, parent, tag='span'):
        self._prevState = prevState
        self._tag = tag
        parent.output('{{Smallcaps|')
    def data(self, parent, data):
        parent.output(data)
        return self
    def stag(self, parent, tag, attrs):
        if tag == 'span' and parent.attr(attrs,'class') == 'cs-fake-sc':
            return FakeSmallCaps(self)
        raise RuntimeError(f"Should never have a start tag in smallcaps but got <{tag}>!")
    def etag(self, parent, tag):
        if tag == self._tag:
            parent.output('}}')
            return self._prevState
        raise RuntimeError(f"Should only have closing </{self._tag}> in smallcaps but got </{tag}>!")

class BoldSmallCaps(SmallCaps):
    def __init__(self, prevState, parent, tag):
        parent.output("<b>")
        super().__init__(prevState, parent, tag)
    def etag(self, parent, tag):
        rval = super().etag(parent,tag)
        if tag == self._tag:
            parent.output("</b>")
        return rval

class EmphaticSmallCaps(SmallCaps):
    def __init__(self, prevState, parent, tag):
        parent.output("<i>")
        super().__init__(prevState, parent, tag)
    def etag(self, parent, tag):
        rval = super().etag(parent,tag)
        if tag == self._tag:
            parent.output("</i>")
        return rval

class RedSmallCaps(SmallCaps):
    def __init__(self, prevState, parent):
        super().__init__(prevState, parent)
        parent.output('{{JesusText|')
    def etag(self, parent, tag):
        if super().etag(parent,tag) is self._prevState:
            parent.output('}}')
            return self._prevState
        raise RuntimeError(f"Should only have closing </span> in redsmallcaps but got </{tag}>!")

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

class TextSpan(ParseStrat):
    """Read a span just like a paragraph, just remember to end on span"""
    def __init__(self, prevState, parent, tag):
        self._prevState = prevState
        self._tag = tag
        self.open_action(parent)
    def open_action(self, parent):
        """What to do when we see the opening tag"""
        pass
    def close_action(self, parent):
        """What to do when we see the closing tag"""
        pass
    def stag(self, parent, tag, attrs):
        # look for verse numbers...
        if tag == 'span': 
            match parent.attr(attrs,'class'):
                case 'vn': 
                    return VerseNumber(self)
                case 'sc' | 'subhead-sc' | 'tn-sc' | 'psa-book-sc' | 'psa-title-sc': 
                    return SmallCaps(self, parent)
                case 'tn-ref-bold-sc':
                    return BoldSmallCaps(self, parent, tag)
                case 'red-sc': 
                    return RedSmallCaps(self,parent)
                case 'note_marker': 
                    return NoteMarker(self)
                case 'red':
                    return RedText(self,parent,tag)
                case 'text-critical-ital':
                    return EmphasisTag(self,parent,tag)
                case 'tn-ref':
                    return StrongTag(self,parent,tag)
        elif tag == 'a':
            if parent.attr(attrs,'id'):
                return self  # skip on purpose!
            if href := parent.attr(attrs,'href'):
                return HRefLink(self, parent, href)
        elif tag == 'sup':
            match parent.attr(attrs,'class'):
                case 'fract-num' | 'tn-fract-num':
                    return InlineFraction(self, parent, tag)
                case 'tn-fract-ital-num':
                    return ItalicFraction(self, parent, tag)
                case _:
                    return BareSupTag(self, parent, tag)
        elif tag == 'em' or tag == 'i':
            if parent.attr(attrs,'class') == 'tn-sc-ital':
                return EmphaticSmallCaps(self,parent,tag)
            return EmphasisTag(self, parent, tag)
        elif tag == 'strong' or tag == 'b':
            return StrongTag(self, parent, tag)
        print(f'warning...unhandled tag <{tag} {attrs}> in text span...')
        return self
    def data(self, parent, data):
        parent.output(data)
        return self
    def etag(self, parent, tag):
        """Go back to the previous state once we see the closing tag"""
        if tag == self._tag:
            self.close_action(parent)
            return self._prevState
        return self

two_nums = re.compile(r'^[^_]+_\d+_(\d+)$') #anchors should end in two numbers
class HRefLink(TextSpan):
    """Handle a href= links to verses"""
    def __init__(self, prevState, parent, href):
        self._href = href
        super().__init__(prevState, parent, 'a')
    def open_action(self, parent):
        match self._href.split('#',1):
            case [tfile,anchor]:
                if m := two_nums.match(anchor):
                    vnum = m.group(1)
                    parent.output(f"[[{target_lookup[tfile]}#V{vnum}|")
                else:
                    raise RuntimeError(f"Bad a href target anchor {anchor} to file {tfile}!")
            case [tfile]:
                parent.output(f"[[{target_lookup[tfile]}|")
    def close_action(self, parent):
        parent.output(']]')

class RedText(TextSpan):
    def open_action(self,parent):
        parent.output('{{JesusText|')
    def close_action(self,parent):
        parent.output('}}')

class InlineFraction(ParseStrat):
    # Phases...
    NUM = 0
    SLASH = 1
    DENOM = 2

    def __init__(self, prevState, parent, tag):
        self._tag = tag
        self._prevState = prevState
        parent.output('{{InlineFraction|')
        self._phase = self.NUM
        self._need_s_tag = False
    def ending(self,parent):
        parent.output('}}')
    def stag(self, parent, tag, attrs):
        if not self._need_s_tag:
            raise RuntimeError(f"found tag <{tag}> inside a fractional component!")
        self._need_s_tag = False # now we are inside a tag
        self._tag = tag # remember the opening tag type

        clz = parent.attr(attrs,'class')
        if self._phase == self.SLASH:
            match clz:
                case 'fract-slash' | 'tn-fract-slash' | 'tn-fract-ital-slash':
                    return self
                case _:
                    raise RuntimeError(f"Got tag <{tag} {attrs}> when looking for a fraction flash type!")
        elif self._phase == self.DENOM:
            match clz:
                case 'fract-den' | 'tn-fract-den' | 'tn-fract-ital-den':
                    return self
                case _:
                    raise RuntimeError(f"Got tag <{tag} {attrs}> when looking for a fraction denominator type!")
    def etag(self, parent, tag):
        if tag != self._tag:
            raise RuntimeError(f"parsing fraction, got tag </{tag}> when expecting </{self._tag}>")
        self._need_s_tag = True # now look for an s tag next
        if self._phase == self.NUM:
            parent.output('|')
            self._phase = self.SLASH
        elif self._phase == self.SLASH:
            self._phase = self.DENOM
        elif self._phase == self.DENOM:
            self.ending(parent)
            return self._prevState 
        return self
    def data(self, parent, data):
        if self._phase == self.SLASH:
            if data.strip() != '/':
                raise RuntimeError(f"parsing fraction, got tag '{data}' when expecting only a slash!")
        else:
            parent.output(data)
        return self

class ItalicFraction(InlineFraction):
    def __init__(self, prevState, parent, tag):
        parent.output('<i>')
        super().__init__(prevState, parent, tag)
    def ending(self,parent):
        super().ending(parent)
        parent.output('</i>')

class StrongTag(TextSpan):
    def open_action(self,parent):
        parent.output("<b>")
    def close_action(self,parent):
        parent.output("</b>")

class BareSupTag(TextSpan):
    def open_action(self,parent):
        parent.output("<sup>")
    def close_action(self,parent):
        parent.output("</sup>")

class EmphasisTag(TextSpan):
    def open_action(self,parent):
        parent.output("<i>")
    def close_action(self,parent):
        parent.output("</i>")

class NotePara(TextSpan):
    def __init__(self, prevState, parent):
        super().__init__(prevState, parent, 'p')
        self._id = None
    def open_action(self, parent):
        self._id = None
    def close_action(self, parent):
        parent.add_note_from_output(self._id)
    def stag(self, parent, tag, attrs):
        if tag == 'a':
            self._id = parent.attr(attrs,'id')
            if not self._id:
                raise RuntimeError('note paragraph with no id!')
        return super().stag(parent, tag, attrs)

class Paragraph(TextSpan):
    """A text span on <p> that might or might not be poetry"""
    def __init__(self, prevState, parent, poetic=False):
        if poetic:
            parent.start_poetry()
        else:
            parent.end_poetry()
        super().__init__(prevState, parent, 'p')
    def close_action(self, parent):
        parent.output('\n\n')

class SubHeading(Paragraph):
    def open_action(self, parent):
        parent.output_notes()
        parent.output('== ')
    def close_action(self, parent):
        parent.output(' ==\n')

class PoetryParagraph(Paragraph):
    def __init__(self, prevState, parent, parts):
        if 'sp' in parts: parent.space_poetry()  # must do this before super()
        super().__init__(prevState, parent, poetic=True)
        indent = 4  # in ems
        if 'vn' in parts: indent = indent - 1 
        if 'ext' in parts: indent = indent + 1
        if 'poet2' in parts: indent = indent + 2
        if 'poet3' in parts: indent = indent + 4
        parent.output(f'<span style="padding-left: {indent}em">')
    def close_action(self, parent):
        parent.output('</span><br/>\n')

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
        self.end_poetry()
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
            self.output('\n\n') # should make a total of 3 newlines for 2 blank lines

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
        self.output('<div style="background: #eeeeee; border-left: 2px solid black; padding: 0.5em;">')
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

# ~~~~~~~~~~~~~~~~ Parsing Intros ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class DTSpan(TextSpan):
    def open_action(self,parent):
        parent.output(';')
    def close_action(self,parent):
        parent.output('\n')

class DDSpan(TextSpan):
    def open_action(self,parent):
        parent.output(':')
    def close_action(self,parent):
        parent.output('\n')

class TDSpan(TextSpan):
    def open_action(self, parent):
        parent.output('|')
    def close_action(self,parent):
        parent.output('\n')

class OutlineTable(ParseStrat):
    """Just output the <p>'s two by two"""
    def __init__(self, prevState, parent):
        self._prevState = prevState
        parent.output('\n{| class="wikitable"\n')
        self._tdCount = 0
    def stag(self, parent, tag, attrs):
        if tag == 'p':
            self._tdCount += 1
            if self._tdCount == 3:
                parent.output('|-\n')
                self._tdCount = 1
            return TDSpan(self, parent, tag)
        else:
            return self
    def etag(self,parent,tag):
       if tag == 'table':
           parent.output('|}\n\n')
           return self._prevState
       else:
           return self

class WaitForIntroP(ParseStrat):
    """Waiting for a paragraph to appear in the intro html"""
    def __init__(self):
        self._found = False
    def stag(self, parent, tag, attrs):
        if tag == 'hr' and parent.attr(attrs,'class') == 'text-critical':
            parent.end_poetry()
            parent.output_notes()
            parent.output('----\n\n')   
            return self
        elif tag == 'p':
            self._found = True
            clz = parent.attr(attrs,'class')
            match clz:
                case 'Intro-title': 
                    self._found = False # not at the good stuff yet
                    return self  #skip it!
                case 'Intro-text':
                    return Paragraph(self, parent, tag)
                case 'Intro-note':
                    return Paragraph(self, parent, tag)
                case 'Stats-head':
                    return DTSpan(self, parent, tag)
                case 'Stats-text':
                    return DDSpan(self, parent, tag)
                case 'Outline-head':
                    return SubHeading(self, parent, tag)
                case _: 
                    raise RuntimeError(f"unknown <p {attrs}> with unexpected class!")
        elif tag == 'a' and parent.attr(attrs,'href') is None:
            return self # just skip it silently
        elif tag == 'table':
            match parent.attr(attrs,'class'):
                case 'ebook-as-is' | 'ebooks-as-is':
                    return OutlineTable(self, parent)
                case _:
                    print(f'Unknown table class {clz}')
        if self._found: print(f"intro just ignoring tag <{tag} {attrs}> after finding a paragraph...")
        return self 

class IntroParser(HTMLParser):
    def __init__(self, ofile):
        super().__init__()
        self._ofile = ofile
        self._state = WaitForIntroP() 
        self._eating_whitespace = False
        self._in_poetry = False
        self._note_q = []
        self._note_mgr = NotesManager()

    def close(self):
        super().close()
        self.end_poetry()
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
            self.output('\n\n') # should make a total of 3 newlines for 2 blank lines

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
        self.output('<div style="background: #eeeeee; border-left: 2px solid black; padding: 0.5em;">')
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

def parse_intro(cfname, ofile):
    """Parse the book intro given by `cfname`, writing wikitext to `ofile`"""
    with open('OEBPS/' + cfname,'r') as ifile:
        ip = IntroParser(ofile)
        ip.feed(ifile.read())
        ip.close()

bs_and_is = re.compile(r'</i><i>|</b><b>',re.I)
num_and_frac = re.compile(r'(\d+){{InlineFraction')

def fixup_wikitext(wt):
    """Take some rough wikitext, and bash it into shape!"""
    wt = bs_and_is.sub('',wt)
    wt = num_and_frac.sub(r'{{InlineFraction|wn=\1',wt)
    return wt

def generate_chapter(bnum, cnum):
    """Generate a whole chapter's text"""
    with StringIO() as chap_buff, open(make_chapter_filename(bnum,cnum),'w') as ofile:
        if cnum == 0:
            print(generate_intro_nav(bnum,cnum),file=chap_buff)
            parse_intro(books[bnum]['chapters'][cnum]['file'],chap_buff)
        else:
            print(generate_nav(bnum,cnum),file=chap_buff)
            parse_chapter(books[bnum]['chapters'][cnum]['file'],chap_buff)
        print(f'&rarr; {make_long_link(*next_chap(bnum,cnum))} &rarr;',file=chap_buff)
        print('[[Category:Bible Texts (NLT)]]', file=chap_buff)
        contents = fixup_wikitext(chap_buff.getvalue())
        ofile.write(contents)

def generate_all():
    """Go through all the books and chapters, generating text"""
    for book in range(len(books)):
        print(books[book]['long'])
        for chap in range(len(books[book]['chapters'])):
            print('...',books[book]['chapters'][chap]['title'])
            generate_chapter(book,chap)

def generate_intros():
    """Go through all the books and chapters, generating text"""
    for book in range(len(books)):
        print(books[book]['long'], books[book]['chapters'][0]['file'])
        generate_chapter(book,0)

