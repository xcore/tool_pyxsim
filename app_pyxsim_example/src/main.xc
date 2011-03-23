// Copyright (c) 2011, XMOS Ltd, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include <print.h>
#include <platform.h>

on stdcore[0]: port p = XS1_PORT_1A;
on stdcore[0]: port q = XS1_PORT_1B;

int value = 5;
int extra = 10;

void wait(int ticks) {
  timer tmr;
  int t;
  tmr :> t;
  tmr when timerafter(t+ticks) :> void;
  return;
}

int main() {
  par {
    on stdcore[0]: {
      int x;
      value = value + extra;
      printstr("Hello world\n");
      p <: 1;
      wait(100);
      q :> x;
      printintln(x);
      p <: 0;
      wait(100);
      q :> x;
      printintln(x);
    }
  }
  return 0;
}
