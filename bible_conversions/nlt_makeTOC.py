from rwt.books import books
import itertools

def chap_link(book, chap):
    """Convert a chapter to a link..."""
    return f"[[{book['long']} {chap['title']} (NLT)|{chap['title']}]]"

def print_toc(ofile):
    for book in books:
        match book['short']:
            case 'GEN': ofile.write('== Old Testament ==\n')
            case 'MAT': ofile.write('== New Testament ==\n')
        print(';',book['long'],file=ofile)
        chaps = book['chapters']
        # print 'introduction' and 9 others.
        print(':',' &bull; '.join(chap_link(book,ch) for ch in chaps[:10]), file=ofile)
        # now print the rest in groups of 10... 
        for group in itertools.batched(chaps[10:],10):
            print(':',' &bull; '.join(chap_link(book,ch) for ch in group), file=ofile)
          
if __name__ == "__main__":
    with open('out/New_Living_Translation_(NLT).wikitext','w') as ofile:
        ofile.write("[[File:NLT Bible Catholic Reader Edition Cover.jpg|right|thumb|cover]]\n")
        print_toc(ofile)
        ofile.write("[[Category:Bibles]]\n")

