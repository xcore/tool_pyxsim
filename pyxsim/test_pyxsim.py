# Copyright (c) 2011, XMOS Ltd, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from pyxsim import *

if __name__ == "__main__":
    xsi = Xsi("../app_pyxsim_example/bin/app_pyxsim_example.xe")
    loopback_plugin = XsiLoopbackPlugin(core="stdcore[0]",
                                        from_port="XS1_PORT_1A",
                                        to_port="XS1_PORT_1B")
    xsi.register_plugin(loopback_plugin)

    # Write 100 to global variable 'extra' which gets added to 'value'
    xsi.write_symbol_word('stdcore[0]', 'extra', 100)

    # Run the simulation
    xsi.run()

    # Read the global variable 'value'
    val = xsi.read_symbol_word('stdcore[0]', 'value')
    print "Testbench read symbol 'value': %d" % val

    xsi.terminate()

