import sys
from html.parser import HTMLParser
from pprint import pprint

nlt_roots = [
    { 'tocfile': 'x1genesis.html', 'short':  'GEN', 'long':  'Genesis', 'testament': 'Old' },
    { 'tocfile': 'x2exodus.html', 'short':  'EXO', 'long':  'Exodus', 'testament': 'Old' },
    { 'tocfile': 'x3leviticus.html', 'short':  'LEV', 'long':  'Leviticus', 'testament': 'Old' },
    { 'tocfile': 'x4numbers.html', 'short':  'NUM', 'long':  'Numbers', 'testament': 'Old' },
    { 'tocfile': 'x5deuteronomy.html', 'short':  'DEU', 'long':  'Deuteronomy', 'testament': 'Old' },
    { 'tocfile': 'x6joshua.html', 'short':  'JOS', 'long':  'Joshua', 'testament': 'Old' },
    { 'tocfile': 'x7judges.html', 'short':  'JDG', 'long':  'Judges', 'testament': 'Old' },
    { 'tocfile': 'x8ruth.html', 'short':  'RUT', 'long':  'Ruth', 'testament': 'Old' },
    { 'tocfile': 'x91samuel.html', 'short':  '1SA', 'long':  '1 Samuel', 'testament': 'Old' },
    { 'tocfile': 'x102samuel.html', 'short':  '2SA', 'long':  '2 Samuel', 'testament': 'Old' },
    { 'tocfile': 'x111kings.html', 'short':  '1KI', 'long':  '1 Kings', 'testament': 'Old' },
    { 'tocfile': 'x122kings.html', 'short':  '2KI', 'long':  '2 Kings', 'testament': 'Old' },
    { 'tocfile': 'x131chronicles.html', 'short':  '1CH', 'long':  '1 Chronicles', 'testament': 'Old' },
    { 'tocfile': 'x142chronicles.html', 'short':  '2CH', 'long':  '2 Chronicles', 'testament': 'Old' },
    { 'tocfile': 'x15ezra.html', 'short':  'EZR', 'long':  'Ezra', 'testament': 'Old' },
    { 'tocfile': 'x16nehemiah.html', 'short':  'NEH', 'long':  'Nehemiah', 'testament': 'Old' },
    { 'tocfile': 'x16btobit.html', 'short':  'TOB', 'long':  'Tobit', 'testament': 'Apocrypha' },
    { 'tocfile': 'x16cjudith.html', 'short':  'JDT', 'long':  'Judith', 'testament': 'Apocrypha' },
    { 'tocfile': 'x17besther.html', 'short':  'EST', 'long':  'Esther', 'testament': 'Old' },
    { 'tocfile': 'x17c1maccabees.html', 'short':  '1MA', 'long':  '1 Maccabees', 'testament': 'Apocrypha' },
    { 'tocfile': 'x17d2maccabees.html', 'short':  '2MA', 'long':  '2 Maccabees', 'testament': 'Apocrypha' },
    { 'tocfile': 'x18job.html', 'short':  'JOB', 'long':  'Job', 'testament': 'Old' },
    { 'tocfile': 'x19psalms.html', 'short':  'PSA', 'long':  'Psalms', 'testament': 'Old' },
    { 'tocfile': 'x20proverbs.html', 'short':  'PRO', 'long':  'Proverbs', 'testament': 'Old' },
    { 'tocfile': 'x21ecclesiastes.html', 'short':  'ECC', 'long':  'Ecclesiastes', 'testament': 'Old' },
    { 'tocfile': 'x22songofsongs.html', 'short':  'SNG', 'long':  'Song of Solomon', 'testament': 'Old' },
    { 'tocfile': 'x22bwisdom.html', 'short':  'WIS', 'long':  'Wisdom', 'testament': 'Apocrypha' },
    { 'tocfile': 'x22csirachecclesiasticus.html', 'short':  'SIR', 'long':  'Sirach', 'testament': 'Apocrypha' },
    { 'tocfile': 'x23isaiah.html', 'short':  'ISA', 'long':  'Isaiah', 'testament': 'Old' },
    { 'tocfile': 'x24jeremiah.html', 'short':  'JER', 'long':  'Jeremiah', 'testament': 'Old' },
    { 'tocfile': 'x25lamentations.html', 'short':  'LAM', 'long':  'Lamentations', 'testament': 'Old' },
    { 'tocfile': 'x25bbaruch.html', 'short':  'BAR', 'long':  'Baruch', 'testament': 'Apocrypha' },
    { 'tocfile': 'x26ezekiel.html', 'short':  'EZK', 'long':  'Ezekiel', 'testament': 'Old' },
    { 'tocfile': 'x27bdaniel.html', 'short':  'DAN', 'long':  'Daniel', 'testament': 'Old' },
    { 'tocfile': 'x28hosea.html', 'short':  'HOS', 'long':  'Hosea', 'testament': 'Old' },
    { 'tocfile': 'x29joel.html', 'short':  'JOL', 'long':  'Joel', 'testament': 'Old' },
    { 'tocfile': 'x30amos.html', 'short':  'AMO', 'long':  'Amos', 'testament': 'Old' },
    { 'tocfile': 'x31obadiah.html', 'short':  'OBA', 'long':  'Obadiah', 'testament': 'Old' },
    { 'tocfile': 'x32jonah.html', 'short':  'JON', 'long':  'Jonah', 'testament': 'Old' },
    { 'tocfile': 'x33micah.html', 'short':  'MIC', 'long':  'Micah', 'testament': 'Old' },
    { 'tocfile': 'x34nahum.html', 'short':  'NAM', 'long':  'Nahum', 'testament': 'Old' },
    { 'tocfile': 'x35habakkuk.html', 'short':  'HAB', 'long':  'Habakkuk', 'testament': 'Old' },
    { 'tocfile': 'x36zephaniah.html', 'short':  'ZEP', 'long':  'Zephaniah', 'testament': 'Old' },
    { 'tocfile': 'x37haggai.html', 'short':  'HAG', 'long':  'Haggai', 'testament': 'Old' },
    { 'tocfile': 'x38zechariah.html', 'short':  'ZEC', 'long':  'Zechariah', 'testament': 'Old' },
    { 'tocfile': 'x39malachi.html', 'short':  'MAL', 'long':  'Malachi', 'testament': 'Old' },
    { 'tocfile': 'x40matthew.html', 'short':  'MAT', 'long':  'Matthew', 'testament': 'New' },
    { 'tocfile': 'x41mark.html', 'short':  'MRK', 'long':  'Mark', 'testament': 'New' },
    { 'tocfile': 'x42luke.html', 'short':  'LUK', 'long':  'Luke', 'testament': 'New' },
    { 'tocfile': 'x43john.html', 'short':  'JHN', 'long':  'John', 'testament': 'New' },
    { 'tocfile': 'x44acts.html', 'short':  'ACT', 'long':  'Acts', 'testament': 'New' },
    { 'tocfile': 'x45romans.html', 'short':  'ROM', 'long':  'Romans', 'testament': 'New' },
    { 'tocfile': 'x461corinthians.html', 'short':  '1CO', 'long':  '1 Corinthians', 'testament': 'New' },
    { 'tocfile': 'x472corinthians.html', 'short':  '2CO', 'long':  '2 Corinthians', 'testament': 'New' },
    { 'tocfile': 'x48galatians.html', 'short':  'GAL', 'long':  'Galatians', 'testament': 'New' },
    { 'tocfile': 'x49ephesians.html', 'short':  'EPH', 'long':  'Ephesians', 'testament': 'New' },
    { 'tocfile': 'x50philippians.html', 'short':  'PHP', 'long':  'Philippians', 'testament': 'New' },
    { 'tocfile': 'x51colossians.html', 'short':  'COL', 'long':  'Colossians', 'testament': 'New' },
    { 'tocfile': 'x521thessalonians.html', 'short':  '1TH', 'long':  '1 Thessalonians', 'testament': 'New' },
    { 'tocfile': 'x532thessalonians.html', 'short':  '2TH', 'long':  '2 Thessalonians', 'testament': 'New' },
    { 'tocfile': 'x541timothy.html', 'short':  '1TI', 'long':  '1 Timothy', 'testament': 'New' },
    { 'tocfile': 'x552timothy.html', 'short':  '2TI', 'long':  '2 Timothy', 'testament': 'New' },
    { 'tocfile': 'x56titus.html', 'short':  'TIT', 'long':  'Titus', 'testament': 'New' },
    { 'tocfile': 'x57philemon.html', 'short':  'PHM', 'long':  'Philemon', 'testament': 'New' },
    { 'tocfile': 'x58hebrews.html', 'short':  'HEB', 'long':  'Hebrews', 'testament': 'New' },
    { 'tocfile': 'x59james.html', 'short':  'JAS', 'long':  'James', 'testament': 'New' },
    { 'tocfile': 'x601peter.html', 'short':  '1PE', 'long':  '1 Peter', 'testament': 'New' },
    { 'tocfile': 'x612peter.html', 'short':  '2PE', 'long':  '2 Peter', 'testament': 'New' },
    { 'tocfile': 'x621john.html', 'short':  '1JN', 'long':  '1 John', 'testament': 'New' },
    { 'tocfile': 'x632john.html', 'short':  '2JN', 'long':  '2 John', 'testament': 'New' },
    { 'tocfile': 'x643john.html', 'short':  '3JN', 'long':  '3 John', 'testament': 'New' },
    { 'tocfile': 'x65jude.html', 'short':  'JUD', 'long':  'Jude', 'testament': 'New' },
    { 'tocfile': 'x66revelation.html', 'short': 'REV', 'long': 'Revelation', 'testament': 'New' }
]

def intro_pname(root):
    """determine the intro page name from the root"""
    return f"{root['long']} Intro (NLT)"

def add_chapter(root, fname, cname):
    """Add a chapter to the root with filename `fname` and chapter number `cname`.
    Note that the cname isn't always just a number (e.g., Esther chapter F)."""
    chap = { 'file': fname, 'title': cname }
    clist = root.get('chapters',[])
    if not clist:
        root['chapters'] = clist
    clist.append(chap)

class TOCInfoParser(HTMLParser):
    # states
    WAITING = 0  # waiting to find a paragraph of links
    LOOKING = 1  # accepting links now
    IN_LINK = 2  # in a link
    def __init__(self, root):
        super().__init__()
        self._root = root
        self._curlink = ['','']
        self._state = self.WAITING

    def _attr(self, attrs, key):
        """Get the attribute from attrs matching `key`, or None"""
        _,val = next(filter(lambda a: a[0] == key, attrs),(None,None)) 
        # RWT print(f'Attributes are {attrs}, got {val} for {key}.')
        return val

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and self._state == self.LOOKING:
            if href := self._attr(attrs,'href'):
                self._curlink[0] = href
                self._state = self.IN_LINK
        elif tag == 'p' and self._state == self.WAITING and self._attr(attrs,'class') == 'oy-month-nav':
            self._state = self.LOOKING

    def handle_endtag(self, tag):
        if tag == 'p': self._state = self.WAITING
        elif tag == 'a' and self._state == self.IN_LINK: 
            add_chapter(self._root, *self._curlink)
            self._curlink = ['','']
            self._state = self.LOOKING

    def handle_data(self, data):
        if self._state == self.IN_LINK:
            self._curlink[1] = data.strip()

def collect_tocinfo(roots=nlt_roots):
    """Pull the nlt roots in, parsing out the TOC data"""
    for root in roots:
        with open('OEBPS/' + root['tocfile'],'r') as infile:
            parser = TOCInfoParser(root)
            parser.feed(infile.read())

if __name__ == "__main__":
    collect_tocinfo()
    pprint(nlt_roots)

