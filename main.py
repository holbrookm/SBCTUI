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
import socket

sys.path.insert(0, '/home/')  # Insert your base path here for libraries


CLD_IP = "159.134.113.212"
CLD_IP_HO = "159.134.113.216"
CLD_PRIMARY_IP = "159.134.113.213"
CLD_SECONDARY_IP = "159.134.113.214"
CLD_GATEWAY = "159.134.113.211"
SRL_IP = "159.134.113.84"
SRL_IP_HO = "159.134.113.88"
SRL_PRIMARY_IP = "159.134.113.85"
SRL_SECONDARY_IP = "159.134.113.86"
SRL_GATEWAY = "159.134.113.83"
NETMASK = "255.255.255.240"

SMTP_SERVER = "10.144.130.196"
SMTP_FROM = 'acmetemplate@ngv.eircom.net'

LOGFILE = "./.new-SBC-template-generator.log"

mail_addresses = ['SODuibhginn@eircom.ie','LKelly@eircom.ie','greglawless@eircom.ie','Carrollm@eircom.ie', 
'SMonaghan@eircom.ie','PFogarty@eircom.ie','mfais@eircom.ie']
   
session_agents_address_list = []


logger = logging_config.logger

def __readinxml__(f):
    ''' Internal method to read in XML file for use within package functions.
    '''
    #logger.debug('Method : ocip_functions.__readinxml__')

    XML = open(f,'r')
    _xml = XML.read()
    #logger.debug ('**Leaving FUNC :::: ocip_functions.__readinxml__')
    XML.close()
    return (_xml)

def get_user_choice():
    '''
        Get User Input Value
    '''
    print ('Please enter 0 to quit!')
    userChoice =int(raw_input('\n Please enter your number range contains search :'))
    if userChoice == 0 :
        sys.exit()
    return userChoice

    
def fill_srl_template(VLANID, NAME, ECID, SRL_IP, SRL_PRIMARY_IP, SRL_SECONDARY_IP, NETMASK, SRL_GATEWAY, LWRCASE_ECID ):
    '''
        Populate the template file fr SRL with the variables and return it.
    '''
    template = __readinxml__('./srl_template.tmpl').format(VLANID, NAME, ECID, SRL_IP, SRL_PRIMARY_IP, SRL_SECONDARY_IP, NETMASK, SRL_GATEWAY, LWRCASE_ECID )
    return template

def fill_cld_template(VLANID, NAME, ECID, SRL_IP, SRL_PRIMARY_IP, SRL_SECONDARY_IP, NETMASK, SRL_GATEWAY, LWRCASE_ECID ):
    '''
        Populate the template file fr SRL with the variables and return it.
    '''
    template = __readinxml__('./srl_template.tmpl').format(VLANID, NAME, ECID, SRL_IP, CLD_PRIMARY_IP, CLD_SECONDARY_IP, NETMASK, CLD_GATEWAY, LWRCASE_ECID )
    return template    

def check_ECID(ECID):
    '''
        This method just check tro see if ECID starts with X, followed by an INT.
        Return True/False
        
    '''
    exitcode = False
    if ECID.__len__():
        if ECID[0] == 'X' and ECID[1:].isdigit():
            exitcode= True
        else:
            print ('\nPlease input an ECID beginning with X followed by digits only.')
    return exitcode

def check_VLANID(VLANID):
    '''
        This method just check tro see if ECID starts with X, followed by an INT.
        Return True/False    
    '''
    exitcode = False
    if VLANID:
        if VLANID >= 500 and VLANID <= 1200:
            exitcode = True
        else:
            print ('\nPlease only enter an VLANID between 500 and 1499 inclusive.')
    return exitcode
   
def check_VIM(VIM):
    '''
        This method just check tro see if ECID starts with X, followed by an INT.
        Return True/False
        
    '''
    exitcode = False
    if VIM.__len__():
        if VIM[0:3] == 'VIM' and VIM[3:].isdigit():
            exitcode = True
        else:
            print ('\nPlease input VIM followed by digits only.')
    return exitcode

def valid_ip(addr):
    '''
      Determine if addr given is valid.
    '''
    try:
        socket.inet_aton(addr)
        return True
    except:
        return False
    
def populate_address_list(num):
    '''
    Valiate that the IP Addr given is in the correct format and that they are unique.
    '''
    for i in range((num)):
        while True:
            addr = raw_input('\n Insert IP address for SA number {0} :         '.format(i+1))
            if valid_ip(addr):
                if addr in session_agents_address_list: # Check for uniqueness.
                    print (' You entered this address already. Please enter a unique address : ' )
                else:
                    session_agents_address_list.append(addr)
                    break
            else:
                print ('You entered {0}. Please enter a valid IP Address.'.format(addr))
    
    return            
    
    
def ask_questions():
    '''
        Text IVR.
        Ask the user questions for SBC configuration.
    '''
    VIM = ''
    VLANID = 0
    ECID = ''
    LWRCASE_ECID = ''
    NAME = ''
    logger.debug('ENTER: main.ask_questions ()')
    print('SBC Template Generator')
    while not check_ECID(ECID):
        ECID = str(raw_input('\n Please enter ICID (example: X1223):  '))
        
    LWRCASE_ECID = ECID.lower()
    while not check_VLANID(VLANID):
        VLANID = int(raw_input("Enter VLAN ID [500-1499] (example: 600): "))
    while not check_VIM(VIM):
        VIM = str(raw_input("Enter VIM (example: VIM8812345): "))
    
    NAME = str(raw_input("Enteprise NAME (example: Irish Distillers):" ))
    
    while True:
        ho_provisioning = str(raw_input('\n\n Hosted Office Provisioning (select n for SIP Trunking)? [y/n/]  '))
        if ho_provisioning == 'y':
            print ('Hosted Office provisioning selected...\n')
            ho_provisioning = True
            break
        elif ho_provisioning == 'n':
            print ('SIP Trunking provisioning selected...\n')
            ho_provisioning = False
            break
        else:
            print ('Please enter y or n..')
            pass
    
    if not (ho_provisioning):
        while True:
            session_agents_choice = str(raw_input("\n\nDo you want to configure the session-agents? [y/n] "))
            if (session_agents_choice == 'y'):
                while True:
                    clustered =  raw_input('Is it a clustered PBX? (more than one session agent) [y/n] ')
                    if clustered == 'y':
                        while True:
                            num_session_agents =  raw_input('How many session-agents do you want to configure? (max 10) ')
                            if not num_session_agents.isdigit():
                                print('\n Please enter a number between 2 and 10 inclusive!')
                                pass
                            else:
                                num_session_agents =  int(num_session_agents)
                                if (num_session_agents >=2 and num_session_agents <=10):
                                    populate_address_list(num_session_agents)
                                    break
                                else:
                                    print('\n Please enter a number between 2 and 10 inclusive!')
                                    pass
                        break
                    elif clustered =='n':
                        num_session_agents = 1
                        populate_address_list(num_session_agents)
                        break
                    else:
                        print('\n Please enter y or n only.')
                        pass
                    break
                    
            elif(session_agents_choice == 'n'):
                num_session_agents = 0
                break
            else:
                print ('Please enter y or n..')
                pass
            break
    while True: # Check for Full provisioning or not.
        full_provisioning = raw_input ('\n\nFull provisioning (select n for site only)? [y/n] ')
        if full_provisioning = 'y':
            full_provisioning = True
        elif full_provisioning = 'n':
            full_provisioning = False
        else:
            print ('Please enter y or n..')
            pass
        
    
    logger.debug('EXIT: main.ask_questions ()')
    return full_provisioning, ho_provisioning, session_agents_address_list
    
def main():
    '''
        Main function of program
    '''
    VIM = ''
    VLANID = ''
    ECID = ''
    LWRCASE_ECID = ''
    NAME = ''
    answers = {}
    
     a,b,c = ask_questions()
    
    # END 
    return

if __name__ == "__main__":
#    print ('Start')
    main() 

