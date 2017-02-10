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
import sendemail

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

    
def fill_ho_template(VLANID, NAME, ECID, _IP, _PRIMARY_IP, _SECONDARY_IP, NETMASK, _GATEWAY, _IP_HO):
    '''
        Populate the template file fr SRL with the variables and return it.
    '''
    template = __readinxml__('./HO_template.tmpl').format(VLANID, NAME, ECID, _IP, _PRIMARY_IP, _SECONDARY_IP, NETMASK, _GATEWAY, _IP_HO )
    return template

def fill_rollback_template( ECID):
    '''
        Populate the initial rolback template file  with the variables and return it.
    '''
    template = __readinxml__('./HO_rollback_template.tmpl').format(ECID )
    return template 
    
    
def fill_srl_template(VLANID, NAME, ECID, SRL_IP, SRL_PRIMARY_IP, SRL_SECONDARY_IP, NETMASK, SRL_GATEWAY, LWRCASE_ECID ):
    '''
        Populate the template file fr SRL with the variables and return it.
    '''
    template = __readinxml__('./full_template.tmpl').format(VLANID, NAME, ECID, SRL_IP, SRL_PRIMARY_IP, SRL_SECONDARY_IP, NETMASK, SRL_GATEWAY, LWRCASE_ECID )
    return template

def fill_cld_template(VLANID, NAME, ECID, SRL_IP, CLD_PRIMARY_IP, CLD_SECONDARY_IP, NETMASK, CLD_GATEWAY, LWRCASE_ECID ):
    '''
        Populate the template file fr SRL with the variables and return it.
    '''
    template = __readinxml__('./full_template.tmpl').format(VLANID, NAME, ECID, SRL_IP, CLD_PRIMARY_IP, CLD_SECONDARY_IP, NETMASK, CLD_GATEWAY, LWRCASE_ECID )
    return template    

def fill_sa_template(ECID, VIM, count, addr, NAME):
    '''
        Populate the template file fr SRL with the variables and return it.
    '''
    template = __readinxml__('./sa_template.tmpl').format(ECID, VIM, count, addr, NAME )
    return template    

def fill_rollback_template( ECID):
    '''
        Populate the initial rolback template file  with the variables and return it.
    '''
    template = __readinxml__('./rollback_template.tmpl').format(ECID )
    return template    
 
def fill_sa_rollback_template(ECID, VIM, count):
    '''
        Populate the initial rolback template file  with the variables and return it.
    '''
    template = __readinxml__('./rollback_sa_template.tmpl').format( ECID, VIM, count)
    return template 

def fill_media_rollback_template(ECID, VLANID, IPaddr):
    '''
        Populate the initial rolback template file  with the variables and return it.
    '''
    template = __readinxml__('./rollback_media_template.tmpl').format( ECID, VLANID, IPaddr)
    return template 
    
def fill_exit_template():
    '''
        Populate the initial rolback template file  with the variables and return it.
    '''
    template = __readinxml__('./exit.tmpl')
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
    
def populate_address_list(session_agents_address_list, num):
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
    
    return session_agents_address_list        
    
    
def ask_questions(config_dict):
    '''
        Text IVR.
        Ask the user questions for SBC configuration.
    '''
    session_agents_address_list = []
    
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

    # Fill Confuguration Dictionary
    config_dict['ECID'] = ECID    
    config_dict['LWRCASE_ECID'] = LWRCASE_ECID
    config_dict['VLANID'] = VLANID
    config_dict['VIM'] = VIM
    config_dict['NAME'] = NAME
    config_dict['ho_provisioning'] = False #  Default
    config_dict['full_provisioning'] = True # Default
    config_dict['session_agents_address_list'] = [] # Empty session agent list in case its carried back from initial read if mistake.
    
    
    while True:
        ho_provisioning = str(raw_input('\n\n Hosted Office Provisioning (select n for SIP Trunking)? [y/n/]  '))
        if ho_provisioning == 'y':
            print ('Hosted Office provisioning selected...\n')
            config_dict['ho_provisioning'] = True
            config_dict['full_provisioning'] = False
            break
        elif ho_provisioning == 'n':
            print ('SIP Trunking provisioning selected...\n')
            break
        else:
            print ('Please enter y or n..')
            pass
    
    if not (config_dict['ho_provisioning']):
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
                                    session_agents_address_list  = populate_address_list(session_agents_address_list, num_session_agents)
                                    break
                                else:
                                    print('\n Please enter a number between 2 and 10 inclusive!')
                                    pass
                        break
                    elif clustered =='n':
                        num_session_agents = 1
                        session_agents_address_list = populate_address_list(session_agents_address_list, num_session_agents)
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
            #Another entry to conf dict    
            config_dict['session_agents_address_list'] = session_agents_address_list
            break
            
        while True: # Check for Full provisioning or not.
            full_provisioning = raw_input ('\n\nFull provisioning (select n for site only)? [y/n] ')
            if full_provisioning == 'y':
                break
            elif full_provisioning == 'n':
                #Modify Config dict here
                config_dict['full_provisioning'] = False
                break
            else:
                print ('Please enter y or n..')
                pass
                
            
    
    logger.debug('EXIT: main.ask_questions ()')
    return config_dict

def readback_input(config_dict):
    '''
        Display on screen the config inputs.
    '''
    print (str(' ECID : {0}'.format(config_dict['ECID'])))
    print (' VIM : {0}'.format(config_dict['VIM']))
    print (' VLANID : {0}'.format(config_dict['VLANID']))
    print (' NAME : {0}'.format(config_dict['NAME']))
    count = 0
    for v in config_dict['session_agents_address_list']:
        count +=1
        print ('Session Agent {0} : IP Address :  {1}'.format(count, v))
    if (config_dict['ho_provisioning']):
        print ('Set for Hosted Office Provisioning')
    else:
        print ('Set for SIP Trunking Provisioning')
    if config_dict['full_provisioning']:
        print ('Set for Full Provisioning.')
    else:
        print ('Set for Partial Provisioning.')
    while True: # Are the deails correct? Return answer to proceed?
        proceed = raw_input('\n\nThese are the details for SBC configuration. Do you wish to proceed? [y/n] ')
        if proceed =='y':
            _proceed = True
            break
        elif proceed == 'n':
            _proceed =  False
            #Default set to False
            break
        else:
            print ('Please enter y or n only.')
            
    return _proceed
  
def prepare_script_CLD(d):
    '''
        Take input data and prepare the config files for CLD only.
        Input is dict with config details called d.
    '''
    print (d)
    if d['ho_provisioning']:
        ptype = 'HO'        
    elif d['full_provisioning']:
        ptype = 'FULL'
    else:
        ptype = 'PARTIAL'
    filename = '{0}-{1}-CLD-{2}.txt'.format(d['ECID'], d['VIM'], ptype) # Filename for output config change
    rollback = '{0}-{1}-CLD-rollback-{2}.txt'.format(d['ECID'], d['VIM'], ptype) # Rollback filename
    try:
        os.remove(filename)
        os.remove(rollback)
    except:
        pass
    try :
        f = open(filename, 'wb')
        r = open (rollback, 'wb')
        if d['ho_provisioning']:
            full_text = fill_ho_template(d['VLANID'], d['NAME'], d['ECID'], CLD_IP, CLD_PRIMARY_IP, CLD_SECONDARY_IP, NETMASK, CLD_GATEWAY, CLD_IP_HO )
            roll_full_text = fill_rollback_template(d['ECID'])
            f.write(full_text)
            r.write(roll_full_text)
            
        if d['full_provisioning']:
            full_text = fill_cld_template(d['VLANID'], d['NAME'], d['ECID'], CLD_IP, CLD_PRIMARY_IP, CLD_SECONDARY_IP, NETMASK, CLD_GATEWAY, d['LWRCASE_ECID'] )
            roll_full_text = fill_rollback_template(d['ECID'])
            r.write(roll_full_text) # Write inital rollback command for full provisioning
            f.write(full_text) # Write initial text for full provisioning
            
        if d['session_agents_address_list'].__len__():
            sa_text = ('\n\nconf ter\nsession-router\n')
            f.write(sa_text) # Open SA text 
            
            count = 1
            for addr in d['session_agents_address_list']:
                session_agent_text = fill_sa_template(d['ECID'], d['VIM'], count, addr, d['NAME'])
                rollback_sa_text =  fill_sa_rollback_template(d['ECID'], d['VIM'], count)
                r.write (rollback_sa_text)
                f.write(session_agent_text) # write to file for each SA
                count +=1 # set count, required in config files.
            exit_text = fill_exit_template()
            f.write(exit_text) # Finish off file
        if d['full_provisioning']: # Marcos template puts this last.. hence the repeat of the full_provisioning check
            pre_media_rollback = fill_media_rollback_template(d['ECID'], d['VLANID'], CLD_IP)
            r.write(pre_media_rollback)# Write rollback for media
        r.close()
        f.close()
        
    except IOError as e:
        print (e)
    return(filename, rollback)
    
def prepare_script_SRL(d):
    '''
        Take input data nd prepare the config files.
    '''
    if d['ho_provisioning']:
        ptype = 'HO'        
    elif d['full_provisioning']:
        ptype = 'FULL'
    else:
        ptype = 'PARTIAL'
    filename = '{0}-{1}-SRL-{2}.txt'.format(d['ECID'], d['VIM'], ptype) # Filename for output config change
    rollback = '{0}-{1}-SRL-rollback-{2}.txt'.format(d['ECID'], d['VIM'], ptype) # Rollback filename
    try:
        os.remove(filename)
        os.remove(rollback)
    except:
        pass
    try :
        f = open(filename, 'wb')
        r = open (rollback, 'wb')
        if d['ho_provisioning']:
            full_text = fill_ho_template(d['VLANID'], d['NAME'], d['ECID'], SRL_IP, SRL_PRIMARY_IP, SRL_SECONDARY_IP, NETMASK, SRL_GATEWAY, SRL_IP_HO )
            roll_full_text = fill_rollback_template(d['ECID'])
            f.write(full_text)
            r.write(roll_full_text)
            
        if d['full_provisioning']:
            full_text = fill_cld_template(d['VLANID'], d['NAME'], d['ECID'], SRL_IP, SRL_PRIMARY_IP, SRL_SECONDARY_IP, NETMASK, SRL_GATEWAY, d['LWRCASE_ECID'] )
            roll_full_text = fill_rollback_template(d['ECID'])
            r.write(roll_full_text) # Write inital rollback command for full provisioning
            f.write(full_text) # Write initial text for full provisioning
        if d['session_agents_address_list'].__len__():
            sa_text = ('\n\nconf ter\nsession-router\n')
            f.write(sa_text) # Open SA text 
            
            count = 1
            for addr in d['session_agents_address_list']:
                session_agent_text = fill_sa_template(d['ECID'], d['VIM'], count, addr, d['NAME'])
                rollback_sa_text =  fill_sa_rollback_template(d['ECID'], d['VIM'], count)
                r.write (rollback_sa_text)
                f.write(session_agent_text) # write to file for each SA
                count +=1 # set count, required in config files.
            exit_text = fill_exit_template()
            f.write(exit_text) # Finish off file
        if d['full_provisioning']: # Marcos template puts this last.. hence the repeat of the full_provisioning check
            pre_media_rollback = fill_media_rollback_template(d['ECID'], d['VLANID'], CLD_IP)
            r.write(pre_media_rollback)# Write rollback for media
        r.close()
        f.close()
        
    except IOError as e:
        print (e)
    return(filename, rollback)
    


"""
    if d['ho_provisioning']:
        ptype = 'HO'
        filename = '{0}-{1}-SRL-{2}.txt'.format(d['ECID'], d['VIM'], ptype) # Filename for output config change
        rollback = '{0}-{1}-SRL-rollback-{2}.txt'.format(d['ECID'], d['VIM'], ptype) # Rollback filename
        try:
            os.remove(filename)
            os.remove(rollback)
        except:
            pass
        try :
            f = open(filename, 'wb')
            r = open (rollback, 'wb')
            full_text = fill_ho_template(d['VLANID'], d['NAME'], d['ECID'], SRL_IP, SRL_PRIMARY_IP, SRL_SECONDARY_IP, NETMASK, SRL_GATEWAY )
            roll_full_text = fill_rollback_template(d['ECID'])
            f.write(full_text)
            r.write(roll_full_text)
            f.close()
            r.close()
        except IOError as e:
            print (e)
            
    elif d['full_provisioning']:
            ptype = 'FULL'
        else:
            ptype = 'PARTIAL'
        filename = '{0}-{1}-SRL-{2}.txt'.format(d['ECID'], d['VIM'], ptype) # Output filename for config changes
        rollback = '{0}-{1}-SRL-rollback-{2}.txt'.format(d['ECID'], d['VIM'], ptype) # Rollback filename
        try :
            f = open(filename, 'wb')
            r = open (rollback, 'wb')
            if d['full_provisioning']:
                full_text = fill_cld_template(d['VLANID'], d['NAME'], d['ECID'], SRL_IP, SRL_PRIMARY_IP, SRL_SECONDARY_IP, NETMASK, SRL_GATEWAY, d['LWRCASE_ECID'] )
                roll_full_text = fill_rollback_template(d['ECID'])
                r.write(roll_full_text) # Write inital rollback command for full provisioning
                f.write(full_text) # Write initial text for full provisioning
            if d['session_agents_address_list'].__len__():
                sa_text = ('\nconf ter\nsession-router\n')
                f.write(sa_text) # Open SA text 
                #r.write(sa_text) #Not needed for rollback
                count = 1 # set count, required in config files.
                for addr in d['session_agents_address_list']:
                    session_agent_text = fill_sa_template(d['ECID'], d['VIM'], count, addr, d['NAME'])
                    rollback_sa_text =  fill_sa_rollback_template(d['ECID'], d['VIM'], count)
                    r.write (rollback_sa_text)
                    f.write(session_agent_text) # write to file for each SA
                    count +=1
                exit_text = fill_exit_template()
                f.write(exit_text) # Finish off file
                
            if d['full_provisioning']: # Marcos template puts this last.. hence the repeat of the full_provisioning check
                pre_media_rollback = fill_media_rollback_template(d['ECID'], d['VLANID'], SRL_IP)
                r.write(pre_media_rollback)# Write rollback for media
            r.close()
            f.close()
        
        except IOError as e:
            print (e)

    return (filename, rollback)
""" 
    
    
def main():
    '''
        Main function of program
    '''
    config_dict = {}
    
    proceed = False
    while not proceed: # Get SBC config details
        config_dict = ask_questions(config_dict) 
        proceed = readback_input(config_dict)
    
    print('Preparing Files....')
    
    f1, r1 = prepare_script_CLD(config_dict)#Write files to disk for CLD
    f2, r2 = prepare_script_SRL(config_dict)#Write files to disk for SRL
    emailaddr = sendemail.selectaddr()
    
   
    l1 = [f1,f2,r1,r2] 
    sendemail.sendmail(l1, emailaddr, config_dict)

    # END 
    return

if __name__ == "__main__":
#    print ('Start')
    main() 

