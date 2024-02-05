#include<stdint.h>
#include<stdio.h>
#include<string.h>
#include "romheb.h"

static char outbuf[162];
static char inbuf[81];

int
main(int argc, char **argv)
{
  while(fgets(inbuf,sizeof(inbuf)/sizeof(char),stdin)) {
     inbuf[strcspn(inbuf, "\r\n")] = '\0';
     if(!unromanize_hebrew_to_utf8(sizeof(outbuf)/sizeof(char), outbuf, inbuf))
     {
       fprintf(stderr, "Could not unromanize!");
       return 1;
     }
     printf("Output <%s> length <%ld>\n", outbuf, strlen(outbuf));

     /* now print out the html entities, surrounded by my wiki's template for hebrew */
     printf("{{hebrew text|");
     uint8_t *c = (uint8_t *)outbuf;
     while(*c) {
        /* read one code point */
	uint32_t code_point = *c;
	int remaining = 0;
	if((code_point & 0xE0) == 0xC0) {
          code_point &= (~0xE0);
	  remaining = 1;
        } else if((code_point & 0xF0) == 0xE0) {
          code_point &= (~0xF0);
	  remaining = 2;
        } else if((code_point & 0xF8) == 0xF0) {
          code_point &= (~0xF8);
	  remaining = 3;
	} 

	while(remaining--) {
          ++c;
	  if((*c & 0xC0) == 0x80) {
            code_point = (code_point << 6) + (*c & ~0xC0);
	  } else {
            /* bad byte... just stop here */
	    --c;
	    remaining = 0;
	  }
	}

	if(code_point <= 0x7f) {
           putchar(code_point);
	} else {
           printf("&#x%x;",code_point);
	}
	++c;
     }
     printf("}}\n");
  }
  return 0;
}
