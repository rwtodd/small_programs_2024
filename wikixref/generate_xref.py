# generating xref templates for all the small tarot cards...

from enum import Enum
from typing import Tuple
import sys
import itertools
import rwt.wikiapi as wiki

Suit = Enum('Suit', ['WANDS', 'CUPS', 'SWORDS', 'PENTACLES'])
Court = Enum('Court', ['KING', 'QUEEN', 'KNIGHT', 'PAGE'])

num_words = ['Zero', 'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten' ]

def canonical_name(card: int|Court, suit: Suit) -> str:
    """Give the name to use for the title of the xref table"""
    if isinstance(card,Court):
        return f"{card.name.capitalize()} of {suit.name.capitalize()}"
    else:
        return f"{num_words[card]} of {suit.name.capitalize()}"

def bxref_contents(card: int|Court, suit: Suit) -> Tuple[str,str]:
    """Give the name of the page to generate"""
    cname = canonical_name(card, suit)
    bxref = f"BXref:{cname} (Tarot Card)"
    contents =  f"""<div class="rwtxref">
{{|
! colspan="2" | {cname} Tarot Card Cross-Reference
|-
! RWS-Like:
| {pict_key_link(card,suit)} &bull; {haindl_link(card,suit)} &bull; {wang_link(card,suit)} &bull; {degree_link(card,suit)}
|}}
</div>
"""
    return (bxref, contents)

# *********************************************************************************
def pict_key_link(card: int|Court, suit : Suit) -> str:
    # pictorial key uses:
    # [[Six of Pentacles (Pictorial Key)]] and King/Queen/Knight/Page
    if isinstance(card, Court):
        return f"[[{card.name.capitalize()} of {suit.name.capitalize()} (Pictorial Key)|Pictorial Key]]"
    else:
        return f"[[{num_words[card]} of {suit.name.capitalize()} (Pictorial Key)|Pictorial Key]]"

# *********************************************************************************
def degree_link(card: int|Court, suit : Suit) -> str:
    # 78 degress uses:
    # [[Six of Pentacles (78 Degrees)]] and King/Queen/Knight/Page
    if isinstance(card, Court):
        return f"[[{card.name.capitalize()} of {suit.name.capitalize()} (78 Degrees)|78 Degrees of Wisdom]]"
    else:
        return f"[[{num_words[card]} of {suit.name.capitalize()} (78 Degrees)|78 Degrees of Wisdom]]"

# *********************************************************************************
haindl_courts = { Court.KING: 'Father', Court.QUEEN: 'Mother', Court.KNIGHT: 'Son', Court.PAGE: 'Daughter' }
haindl_suits = { Suit.WANDS: 'Wands', Suit.CUPS: 'Cups', Suit.SWORDS: 'Swords', Suit.PENTACLES: 'Stones'}

def haindl_link(card: int|Court, suit : Suit) -> str:
    # haindl uses:
    # [[5 of Stones (Haindl Tarot)]]
    if isinstance(card, Court):
        return f"[[{haindl_courts[card]} of {haindl_suits[suit]} (Haindl Tarot)|Haindl]]"
    else:
        return f"[[{"Ace" if card == 1 else card} of {haindl_suits[suit]} (Haindl Tarot)|Haindl]]"

# *********************************************************************************
wang_cnums = { Court.KING: 2, Court.QUEEN: 3, Court.KNIGHT: 6, Court.PAGE: 10 }
wang_cnames = { Court.KING: 'King', Court.QUEEN: 'Queen', Court.KNIGHT: 'Prince', Court.PAGE: 'Princess' }
wang_pages = ['ZERO', 
    'Kether The Crown',
    'Chokmah Wisdom',
    'Binah Understanding',
    'Chesed Mercy',
    'Geburah Strength',
    'Tiphareth Beauty',
    'Netzach Victory',
    'Hod Splendor',
    'Yesod Foundation',
    'Malkuth Kingdom']

def wang_anchor_name(card: int|Court, suit: Suit) -> str:
    """Give the name to use for the anchor in the wang book"""
    if isinstance(card,Court):
        return f"{wang_cnames[card]} of {suit.name.capitalize()}"
    else:
        return f"{num_words[card]} of {suit.name.capitalize()}"

def wang_link(card: int|Court, suit: Suit) -> str:
    # wang puts the cards on a page for the sephira...
    bname = '(Qabalistic Tarot)'
    if isinstance(card,Court):
        return f"[[{wang_pages[wang_cnums[card]]} {bname}#{wang_anchor_name(card,suit)}|Qabalistic Tarot]]"
    else:
        return f"[[{wang_pages[card]} {bname}#{wang_anchor_name(card,suit)}|Qabalistic Tarot]]"


######

def check_response(response):
    if response.status_code < 200 or response.status_code >= 300:
        print("Response:", response, sep="\n", file=sys.stderr)
        raise SystemExit(f"Bad request response of {response.status_code}!")
    

# ws = wiki.WikiSession('https://kb.rwtodd.org/api.php')
# api_response = ws.login('', '')
# check_response(api_response)

# for s in Suit:
#     for c in  itertools.chain(range(1,11), Court):
#         fname, contents = bxref_contents(c, s)
#         print("Doing", fname, file=sys.stderr)
#         # print(contents, file=sys.stderr)
#         api_response = ws.edit_from_string(fname, contents, "Creating xref table")
#         check_response(api_response)

# import re
# page_extractor = re.compile(r'^\[\[(.*?)\|',re.X)
# def extract_page(link: str) -> str:
#     if m := page_extractor.match(link):
#         return m.group(1)
#     else:
#         raise SystemExit(f"Bad link format <{link}>")

# count = 0
# for s in Suit:
#     for c in  itertools.chain(range(1,11), Court):
#         # get the template name
#         fname, _ = bxref_contents(c, s)
#         contents = '{{' + fname + '}}'
#         print("Doing", contents, file=sys.stderr)
#         # now get the page name for waite's book
#         page = extract_page(pict_key_link(c,s))
#         print(page, file=sys.stderr)
#         api_response = ws.edit_from_string(page, contents, comment = "appending xref table", action = 'appendtext')
#         page = extract_page(haindl_link(c,s))
#         print(page, file=sys.stderr)
#         api_response = ws.edit_from_string(page, contents, comment = "appending xref table", action = 'appendtext')
#         check_response(api_response)
#         if count == 0:
#             input("Press Enter to continue...")
#             count = count + 1

# ws.logout()

# --- generate appropriate lists of bxref names...
for c in range(1,11):
    for s in Suit:
        fname, _ = bxref_contents(c,s)
        print('{{',fname,'}}', sep='')
    match c:
        case 2:
            for s in Suit:
                fname, _ = bxref_contents(Court.KING, s)
                print('{{',fname,'}}', sep='')
        case 3:
            for s in Suit:
                fname, _ = bxref_contents(Court.QUEEN, s)
                print('{{',fname,'}}', sep='')
        case 6:
            for s in Suit:
                fname, _ = bxref_contents(Court.KNIGHT, s)
                print('{{',fname,'}}', sep='')
        case 10:
            for s in Suit:
                fname, _ = bxref_contents(Court.PAGE, s)
                print('{{',fname,'}}', sep='')

