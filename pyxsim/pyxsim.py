# Copyright (c) 2011, XMOS Ltd, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import os, re
from ctypes import cdll, byref, c_void_p, c_char_p, c_int, create_string_buffer

xsi_lib_path = os.path.abspath(os.environ['XCC_EXEC_PREFIX'] + '../lib/libxsidevice.so')

xsi_lib = cdll.LoadLibrary(xsi_lib_path)

def xsi_is_valid_port(port):
  return (re.match('XS1_PORT_\d+\w', port) != None)

def xsi_get_port_width(port):
  if not xsi_is_valid_port(port):
    return None
  else:
    return int(re.match('^XS1_PORT_(\d+)\w', port).groups(0)[0])

class EnumExceptionSet:
  
    def __init__(self, enum_list, valid_list=[]):
        self.enum_list = enum_list
        self.valid_list = valid_list

    def __getattr__(self, name):
        if name in self.enum_list:
            return self.enum_list.index(name)
        raise AttributeErr

    def is_valid(self, value):
      if value < len(self.enum_list):
        enum = self.enum_list[value]
        return (enum in self.valid_list)

    def error_if_not_valid(self, value):
        if value < len(self.enum_list):
            enum = self.enum_list[value]
            if not enum in self.valid_list:
                raise type('XSI_ERROR_' + enum,(Exception,),{})
            
    def error(self, value):
      if value < len(self.enum_list):
        enum = self.enum_list[value]
        raise type('XSI_ERROR_' + enum,(Exception,),{})


XsiStatus = EnumExceptionSet(['OK', 
                              'DONE',
                              'TIMEOUT',
                              'INVALID_FILE',
                              'INVALID_INSTANCE',     
                              'INVALID_CORE',        
                              'INVALID_PACKAGE',
                              'INVALID_PIN',          
                              'INVALID_PORT',         
                              'MEMORY_ERROR',         
                              'PSWITCH_ERROR',        
                              'INVALID_ARGS',         
                              'NULL_ARG',             
                              'INCOMPATIBLE_VERSION'],
                             valid_list = ['OK','DONE'])


class Xsi(object):
    def __init__(self, xe_path):  
        self.xsim = c_void_p()
        args = c_char_p(xe_path)    
        status = xsi_lib.xsi_create(byref(self.xsim), args)
        self._plugins = []
        
    def register_plugin(self, plugin):
      self._plugins.append(plugin)
        
    def clock(self):
        status = xsi_lib.xsi_clock(self.xsim)            
        if XsiStatus.is_valid(status):
          for plugin in self._plugins:
            plugin.clock(self)
        return status
        
    def run(self):
        status = XsiStatus.OK
        while (status != XsiStatus.DONE):
            status = self.clock()    
            XsiStatus.error_if_not_valid(status)

    def terminate(self):
        status = xsi_lib.xsi_terminate(self.xsim)
        XsiStatus.error_if_not_valid(status)

    def sample_pin(self, package, pin):
      c_package = c_char_p(package)    
      c_pin = c_char_p(pin)    
      c_value = c_int()
      status = xsi_lib.xsi_sample_pin(self.xsim, c_package, c_pin, 
                                      byref(c_value))
      XsiStatus.error_if_not_valid(status)
      return c_value.value    

    def sample_port_pins(self, core, port, mask):
      c_core = c_char_p(core)    
      c_port = c_char_p(port)    
      c_mask = c_int(mask)
      c_value = c_int()
      status = xsi_lib.xsi_sample_port_pins(self.xsim, c_core, c_port, 
                                            c_mask, byref(c_value))
      XsiStatus.error_if_not_valid(status)
      return c_value.value    

    def drive_pin(self, package, pin, value):
      c_package = c_char_p(package)    
      c_pin = c_char_p(pin)    
      c_value = c_int(value)
      status = xsi_lib.xsi_drive_pin(self.xsim, c_package, c_pin, 
                                     c_value)
      XsiStatus.error_if_not_valid(status)

    def drive_port_pins(self, core, port, mask, value):
      c_core = c_char_p(core)    
      c_port = c_char_p(port)    
      c_mask = c_int(mask)
      c_value = c_int(value)
      status = xsi_lib.xsi_drive_port_pins(self.xsim, c_core, c_port, 
                                            c_mask, c_value)
      XsiStatus.error_if_not_valid(status)

    def is_pin_driving(self, package, pin):
      c_package = c_char_p(package)    
      c_pin = c_char_p(pin)    
      c_value = c_int()
      status = xsi_lib.xsi_is_pin_driving(self.xsim, c_package, c_pin, 
                                          byref(c_value))
      XsiStatus.error_if_not_valid(status)
      return c_value.value    

    def is_port_pins_driving(self, core, port, mask):
      c_core = c_char_p(core)    
      c_port = c_char_p(port)    
      c_mask = c_int(mask)
      c_value = c_int()
      status = xsi_lib.xsi_is_port_pins_driving(self.xsim, c_core, c_port, 
                                                c_mask, byref(c_value))
      XsiStatus.error_if_not_valid(status)
      return c_value.value    

    def read_mem(core, address, num_bytes):
      c_core = c_char_p(core)    
      c_address = c_int(address)
      c_num_bytes = c_int(num_bytes)
      buf = create_string_buffer(num_bytes)
      status = xsi_lib.xsi_read_mem(self.xsim, c_core, c_address,
                                    c_num_bytes, buf)
      XsiStatus.error_if_not_valid(status)      
      return buf.value

    def write_mem(core, address, num_bytes, data):
      c_core = c_char_p(core)    
      c_address = c_int(address)
      c_num_bytes = c_int(num_bytes)
      buf = create_string_buffer(data)
      status = xsi_lib.xsi_write_mem(self.xsim, c_core, c_address,
                                    c_num_bytes, buf)
      XsiStatus.error_if_not_valid(status)      
    
    def read_pswitch_reg(core, reg_num):
      c_core = c_char_p(core)    
      c_reg_num = c_int(reg_num)
      c_value = c_int()
      status = xsi_lib.xsi_read_pswitch_reg(self.xsim, c_core, c_reg_num,
                                            byref(c_value))      
      XsiStatus.error_if_not_valid(status)      
      return c_value.value


    def write_pswitch_reg(core, reg_num, value):
      c_core = c_char_p(core)    
      c_reg_num = c_int(reg_num)
      c_value = c_int(value)
      status = xsi_lib.xsi_write_pswitch_reg(self.xsim, c_core, c_reg_num,
                                            c_value)      
      XsiStatus.error_if_not_valid(status)      


class XsiPlugin(object):    
    def clock(self, xsi):
      pass

class XsiLoopbackPlugin(XsiPlugin):
    def __init__(self, 
                 core="stdcore[0]", 
                 from_port='XS1_PORT_1A', 
                 to_port='XS1_PORT_1B', 
                 from_mask=None,
                 to_mask=None):
        self.from_port = from_port
        self.to_port = to_port
        self.core = core
        if from_mask == None:
          self.from_mask = (1 << (xsi_get_port_width(from_port)))-1
        else:
          self.from_mask = from_mask
        if to_mask == None:
          self.to_mask = (1 << (xsi_get_port_width(from_port)))-1
        else:
          self.to_mask = to_mask

    def clock(self, xsi):
        value = xsi.sample_port_pins(self.core, self.from_port, self.from_mask) 
        xsi.drive_port_pins(self.core, self.to_port, self.to_mask, value)



