# Set MODE=release to compile the modules with optimizations
MODE = debug 
.PHONY: all clean check

ifeq ($(MODE),release)
  $(info compiling in RELEASE mode)
  CPPFLAGS := -DNDEBUG
  CFLAGS := -std=c2x -O3 -march=native
else
  $(info compiling in DEBUG mode)
  CFLAGS := -std=c2x -g -Wall
endif
LDFLAGS := -L .

PROGS := romhebrew

all: $(PROGS)

clean:
	-rm *.o *.a $(PROGS)

romheb.o: romheb.c romheb.h
	$(CC) $(CPPFLAGS) $(CFLAGS) -c romheb.c

libromanized-hebrew.a: romheb.o
	$(AR) -r $@ $^

romhebrew: driver-program.c libromanized-hebrew.a
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ driver-program.c -lromanized-hebrew

