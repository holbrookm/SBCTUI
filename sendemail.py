#!/usr/bin/python
"""
    # Project: SBC Template generator for SIP Voice
    # This module address the sending fo the emails to the designated users.
    # 0851742253
    # <mholbrook@eircom.ie>
"""
from __future__ import print_function
import sys
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders


def selectaddr():
    '''
        Select recipient from list of addresses
        return email address
    '''
    d = {}
    d['1'] = 'SODuibhginn@eircom.ie'
    d['2'] = 'LKelly@eircom.ie'
    d['3'] = 'greglawless@eircom.ie'
    d['4'] = 'Carrollm@eircom.ie'
    d['5'] = 'SMonaghan@eircom.ie'
    d['6'] = 'PFogarty@eircom.ie'
    d['7'] = 'mfais@eircom.ie'
    d['8'] = 'mholbrook@eircom.ie'
    
    print('Select the email address from the list: \n')
    l = d.keys()
    l.sort()
    for key in l:
        print (key + '  :  ' + d[key])
    while True:
        recipient = raw_input('Enter your choice :  ')
        if recipient in d.keys():
            break
        else:
            print ('\nPlease enter only a number indicating an email recipient above. ')
    
    return (d[recipient])
    
    

def sendmail(filenamelist, emailaddr, _dict):
    """
        Function: Send email and attachments to designated recipient.
    """
    marker = "AUNIQUEMARKER"
    sender = 'acmetemplate@ngv.eircom.net'
    host = "10.144.130.196";
    
    
    if _dict['full_provisioning']:
        ptype = 'FULL'
    elif _dict['ho_provisioning']:
        ptype ='HO'
    else:
        ptype = 'PARTIAL'
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = emailaddr
    msg['Subject'] = 'SBC Templates for {0} - {1} - {2} provisioning'.format(_dict['ECID'], _dict['VIM'], ptype)
    

    body = """
    MAIL GENERATED FROM THE SBC TEMPLATE GENERATOR

    This mail contains the template configurations for customer {0} - {1} - {2}


    Customer details:

    NAME: {0}
    ICID: {3}
    VIM: {1}
    VLAN ID: {4}
    IP addresses for session agents: {5}

    TYPE OF PROVISIONING: {2}

    There are two files attached to this mail:

    1) {3}-{1}-CLD-{2}.txt --> template file for the CLD SBC
    2) {3}-{1}-SRL-{2}.txt --> template file for the SRL SBC

    In order to implement the configuration in each SBC, please use the SBC-config-loader.pl script and then:

    1) Copy and paste the template into the SBC CLI
    2) Look at the output to determine if there have been any errors in the implementation

    Please note the implementation might fail if the configuration for a specific customer has already been
    implemented in the SBC.

    For FULL PROVISIONING, make sure no configuration for the customer {0} is currently implemented BEFORE
    copying and pasting the one attached to this mail.

    For PARTIAL PROVISIONING, make sure the configuration for the customer has already been completed AND the 
    VIM circuit ID for this site is DIFFERENT from the ones used for previous sites. --> THIS IS VERY 
    IMPORTANT AS OTHERWISE EXISTING CUSTOMER DATA WILL BE OVERWRITTEN <--


    For any issues with the template, please contact Voice Services:
    Liam O'Toole
    Marco Fais
    Gerry Flaherty


    """.format(_dict['NAME'], _dict['VIM'], ptype, _dict['ECID'], _dict['VLANID'], _dict['session_agents_address_list'])

    msg.attach(MIMEText(body, 'plain'))
   
    
    # Read a file and encode it into base64 format
    for filename in filenamelist:
        fo = open(filename, 'r')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((fo).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename={0}'.format(filename))
        msg.attach(part)
        fo.close()
   
   
    try:
       server = smtplib.SMTP(host)
       message = msg.as_string()
       server.sendmail(sender, emailaddr, message)
       server.quit()
       print ("Successfully sent email")
    except smtplib.SMTPException as e:
       print ("Error: unable to send email")
       print (e)
       
    return 
