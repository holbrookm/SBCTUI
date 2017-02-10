#!/usr/bin/python
""" # SBC Template generator for SIP Voice
    # Supports single sites and clustered PBXs
    # Standard configuration can be amended using Net-Net Central if needed
    # Hosted Provisioning added
    # 0851742253
    # <mholbrook@eircom.ie>
"""
from __future__ import print_function
import sys
import logging_config
import telnetlib

"""
username: acme
password: packet
LAB-IP-1: 10.144.134.140
LAB-IP-2: 10.144.134.141
CLD-IP-1: 10.144.102.142
CLD-IP-2: 10.144.102.143
SRL-IP-1: 10.144.70.142
SRL-IP-2: 10.144.70.143

"""

class SBC (object):
    
    
    def __init__(self, host, pw1, pw2):
        '''
            Initialise SBC class
        '''
        self.host = host
        self.pw1 = pw1
        self.enablepw = pw2
        self.conn = None
        self.hostdict = {}
        self.hostdict['10.144.134.140'] = 'LAB_SBC_01'
    
    def set_string(self):
        return self.hostdict[self.host]
        
    def connect(self):
        '''
            Connect to designated SBC
        '''
        error = -1
        
        self.conn = telnetlib.Telnet(self.host)
        str = self.conn.read_until('Password: ', 2)
        hoststring = self.set_string()
        if not(str.find('Password: ') == error):
            self.conn.write(self.pw1)
            self.conn.write('\n')
            str1 = self.conn.read_until('\r\n{0}> '.format(hoststring), 2)
                       
            if not(str1.find(hoststring) == error):
                exit_code = True
            else:
                print('Password submitted but not accepted. ' + str1)
                exit_code = False
        else:
            print('Issue with initial Login: ' + str)
            exit_code = False
       
        return exit_code
       
    def enable(self):
        '''
            Enter Priviliged Mode
        '''
        error = -1
        hoststring = self.set_string()
        self.conn.write('en \n')
        str1 = self.conn.read_until('Password: ', 2)
        if not (str1.find('Password: ') == error):
            self.conn.write(self.enablepw)
            self.conn.write('\n')
            str2 = self.conn.read_until('{0}# '.format(hoststring), 2)
            if not( str2.find('{0}# '.format(hoststring)) == error):
                print('Priviliged: ' + str2)
                return True
            else:
                print ('Error with enable pw: ' + str2)
        else:
            print ('Password Issue' +str1)
            return False
       
    def read(self):
        print (self.conn.read_until('***', 2))
        return
        
    def close(self):
        ''' 
            Close SBC connection
        '''
        self.conn.close()
        return