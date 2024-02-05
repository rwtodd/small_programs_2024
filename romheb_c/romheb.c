#include<stdio.h>
#include<stdint.h>
#include<string.h>
#include "romheb.h"

/* H == Hebrew letter, HF == Possibly-final letter, empty == a non-letter placeholder */
#define H(ltr, ln, name,code) { .code_point = code, .srclen = ln, .has_final = false }
#define HF(ltr,ln, name,code) { .code_point = code, .srclen = ln, .has_final = true }
#define empty(ltr) { }

static struct hebrew_s {
  uint16_t code_point;
  uint8_t srclen;
  bool    has_final; /* if true, the final form will be at code-point minus 1 */
} hebrew_chars[] = {
  H(A,1,alef, 0x5d0),
  H(B,1,bet, 0x5d1),
  empty(C), 
  H(D,1,dalet, 0x5d3),
  empty(E),
  empty(F),
  H(G,1,gimel, 0x5d2),
  H(H,1,heh, 0x5d4),
  H(I,1,yod, 0x5d9),
  empty(J),
  HF(K,1,kaph, 0x5db),
  H(L,1,lamed, 0x5dc),
  HF(M,1,mem, 0x5de),
  HF(N,1,nun, 0x5e0),
  H(O,1,ayin, 0x5e2),
  HF(P,1,peh, 0x5e4),
  H(Q,1,qof, 0x5e7),
  H(R,1,resh, 0x5e8),
  H(S,1,samech, 0x5e1),
  H(T,1,teth, 0x5d8),
  empty(U),
  H(V,1,vav, 0x5d5),
  empty(W),
  empty(X),
  empty(Y),
  H(Z,1,zain, 0x5d6),
  H(Ch,2,cheth, 0x5d7), /* 26 */
  H(Ki,2,kaf initial, 0x5d9), /* 27 */
  H(Kf,2,kaf final, 0x5d8), /* 28 */
  H(Mi,2,mem initial, 0x5de), /* 29 */
  H(Mf,2,mem final, 0x5dd), /* 30 */
  H(Ni,2,nun initial, 0x5e0), /* 31 */
  H(Nf,2,nun final, 0x5df), /* 32 */
  H(Pi,2,peh initial, 0x5e4),/* 33 */
  H(Pf,2,peh final, 0x5e3), /* 34 */
  H(Sh,2,shin, 0x5e9), /* 35 */
  H(Th,2,tav, 0x5ea), /* 36 */
  HF(Tz,2,tzaddi, 0x5e6), /* 37 */
  H(Tzi,3,tzaddi initial, 0x5e6), /* 38 */
  H(Tzf,3,tzaddi final, 0x5e5), /* 39 */
  H(Vv,2,vav-vav ligature, 0x5f0), /* 40 */
  H(Vi,2,vav-yod ligature, 0x5f1), /* 41 */
  H(Ii,2,yod-yod ligature, 0x5f2), /* 42 */
  /* ~~~ start of niqqud ~~~ */
  H(;,1,Sh''va, 0x5b0), /* 43 */
  H(;3,2,Reduced Segol, 0x5b1), /* 44 */
  H(;_,2,Reduced Patach, 0x5b2), /* 45 */
  H(;7,2,Reduced Kamatz, 0x5b3), /* 46 */
  H(1,1,Hiriq, 0x5b4), /* 47 */
  H(2,1,Zeire, 0x5b5), /* 48 */
  H(3,1,Segol, 0x5b6), /* 49 */
  H(_,1,Patach, 0x5b7), /* 50 */
  H(7,1,Kamatz, 0x5b8), /* 51 */
  H(*,1,Dagesh,0x5bc), /* 52 */
  H(\,1,Kubutz, 0x5bb), /* 53 */
  H(`,1,Holam, 0x5b9), /* 54 */
  H(l,1,Dot Left, 0x5c2), /* 55 */
  H(r,1,Dot Right, 0x5c1) /* 56 */
};
#undef H
#undef HF
#undef empty

/* some helper macros for the parse_* functions. just to pretty-up the code */
#define is_hebrew(n) return &hebrew_chars[n]
#define followed_by(l,n) if(*src == l) is_hebrew(n)
#define initial_or_final(n1,n2) if(*src == 'i') is_hebrew(n1); \
     if(*src == 'f') is_hebrew(n2)

/* Parse looking for the next hebrew letter */
static struct hebrew_s *
parse_letter(const char src[static 2])
{
  char ch = *src++;
  switch(ch) {
  case 'C': followed_by('h',26); break;
  case 'I': followed_by('i',42); break;
  case 'K': initial_or_final(27,28); break;
  case 'M': initial_or_final(29,30); break;
  case 'N': initial_or_final(31,32); break;
  case 'P': initial_or_final(33,34); break;
  case 'S': followed_by('h',35); break;
  case 'T':
     followed_by('h',36);
     if(*src == 'z') {
       ++src;
       initial_or_final(38,39);
       is_hebrew(37);
     }
     break;
  case 'V': followed_by('v',40); followed_by('i',41); break;
  }
  if( (ch >= 'A') && (ch <= 'Z') ) {
    is_hebrew(ch - 'A');
  }
  return nullptr;
}

/* Parse looking for a niqqud, if there is one */
static struct hebrew_s *
parse_niqqud(const char src[static 2])
{
  char ch = *src++;
  switch(ch) {
  case ';': 
    followed_by('3',44);
    followed_by('_',45);
    followed_by('7',46);
    is_hebrew(43);
  case '1': is_hebrew(47);
  case '2': is_hebrew(48);
  case '3': is_hebrew(49);
  case '7': is_hebrew(51);
  case '_': is_hebrew(50);
  case '*': is_hebrew(52);
  case '\\': is_hebrew(53);
  case '`': is_hebrew(54);
  case 'l': is_hebrew(55);
  case 'r': is_hebrew(56);
  }
  return nullptr;
}
#undef followed_by
#undef initial_or_final
#undef is_hebrew

/* macros to encode the 1st and 2nd byte of a 2-byte utf-8 sequence, which
 * covers all of the hebrew code-points. */
#define utf8_b1(n) (char)( ((n) >> 6) | 0xC0 )
#define utf8_b2(n) (char)( ((n) & 0x3F) | 0x80 )

/* we are either looking for a letter or niqqud, so encode that state as an enum */
enum parse_state { LETTER, NIQQUD };

bool
unromanize_hebrew_to_utf8(size_t dest_len, char dest[dest_len], const char src[static 1]) 
{
  bool retval = true;
  char *potential_final = nullptr;
  enum parse_state state = LETTER;

  struct hebrew_s *hebrew = nullptr; 
  while(*src)
    {
      hebrew = (state == LETTER) ? parse_letter(src) : parse_niqqud(src);
      if(hebrew && hebrew->code_point)
        {
          if(state == LETTER) 
            potential_final = hebrew->has_final ? dest : nullptr;
          if(dest_len > 2) {
            *dest++ = utf8_b1(hebrew->code_point);
            *dest++ = utf8_b2(hebrew->code_point);
            dest_len -= 2;
            src += hebrew->srclen;
          } else {
             retval = false;
             goto done;
          }
          state = NIQQUD; /* always look for niqqud after a successful match */
        }
      else
        {
          if(state == LETTER) {
            /* we had a non-hebew-letter... possibly fix-up a final? */
            if(potential_final) {
              (*(potential_final + 1))--;
              potential_final = nullptr;
            }
            if(dest_len > 1) {
              *dest++ = *src++;
              dest_len -= 1;
            } else {
               retval = false;
               goto done;
            }
          } else { /* state == NIQQUD */
            state = LETTER; /* no niqqud... look for letter */
          }
        }
    }
    /* out of input... did we end on a potential final ? */
    if(potential_final) {
       (*(potential_final + 1))--;
    }
done:
  *dest = '\0';
  return retval;
}
#undef utf8_b1
#undef utf8_b2
