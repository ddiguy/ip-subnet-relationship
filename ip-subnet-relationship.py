#!/usr/local/bin/python3.6
import argparse
import ipaddress
import os
import pytricia
import sys
from itertools import groupby


"""
================================================================================
Purpose
================================================================================
Take two files as input:  (1) IPs (2) Subnets

Will match every IP to a subnet
If the IP is in a subnet, then show what subnet it is in

ip file (input file):
101.24.8.175
10.130.166.216

subnet file (input file):
101.24.8.0/24
10.130.166.0/24

output file:
Source,Destination
101.24.8.0/24,101.24.8.175
10.130.166.0/24,10.130.166.216
"""

"""
================================================================================
Variables
================================================================================
"""
file_dir = str(os.getcwd()+'/')
subnet_relationship_file = file_dir + 'ip-subnet-relationship.csv'

IPSR_DDI = set()
IP_DDI = set()
SN_DDI = set()

# Command line arguments
parser = argparse.ArgumentParser(description='Purpose of script is to create a relationship file showing what subnet every IP is in when given two input files: #1 IP and #2 Subnets')
parser.add_argument('--log', '-l', default='20', choices=['10', '20'],
    help='Used to specify the logging level.  Set logging to DEBUG when troubleshooting.  If you do not specify a logging level, the default is 20(INFO).  Valid choices are either 10 or 20.  Explanation of choices:  10(DEBUG)  20(INFO)')
parser.add_argument('--subnets', '-s',
    help='Used to specify the input file that contains all of the Subnets.')
parser.add_argument('--ips', '-i',
    help='Used to specify the input file that contains all of the IPs.')
args = parser.parse_args()

def keyfunc(s):
    """
    Sorts sets based on numbers so that IP's appear in order
    Common usage is:
    sorted(my_set, key=keyfunc)
    """
    return [int(''.join(g)) if k else ''.join(g) for k, g in groupby('\0'+s, str.isdigit)]

"""
================================================================================
Validating expected options were given and that files exist
================================================================================
"""

# If the user does not specify input file on command line
try:
    if not args.ips:
        print('\nNeed to run script again, but specify an input file that contains all of IPs that you want a relationship for.\n')
        # Stopping script so user can rerun correctly
        sys.exit()
    if not args.subnets:
        print('\nNeed to run script again, but specify an input file that contains all of Subnets that you will use to find relationship for the IPs.\n')
        # Stopping script so user can rerun correctly
        sys.exit()
except Exception as e:
    print('Unable to look for input files - '+str(e))


# If specified file does not exist in current working directory
try:
    if not os.path.isfile(file_dir+args.ips):
        print ('Expecting to find file containing list of IPs to create relationship for in ' + file_dir+'\nPut file in correct directory, then re-run script.')
        # Stopping script so user can rerun correctly
        sys.exit()
except Exception as e:
    print('Unable to look for IPs file - '+str(e))

try:
    if not os.path.isfile(file_dir+args.subnets):
        print ('Expecting to find file containing list of Subnets to create IP relationship for in ' + file_dir+'\nPut file in correct directory, then re-run script.')
        # Stopping script so user can rerun correctly
        sys.exit()
except Exception as e:
    print('Unable to look for Subnets file - '+str(e))


"""
================================================================================
Creating relationship file
================================================================================
"""

# Adding IPs to set
try:
    with open(file_dir+args.ips, 'r') as ipfile:
        for line in ipfile:
            try:
                IP_DDI.add(ipaddress.ip_address(line.strip()))
            except:
                pass
except Exception as e:
    print('Unable to add IPs to set - '+str(e))
    sys.exit()


# Adding subnets to set
try:
    with open(file_dir+args.subnets, 'r') as subfile:
        for lines in subfile:
            SN_DDI.add(ipaddress.ip_network(lines.strip()))
except Exception as e:
    print('Unable to add Subnets to set - '+str(e))
    sys.exit()


# Create Trie object
try:
    pyt = pytricia.PyTricia()
    for i in SN_DDI:
        try:
            pyt.insert(ipaddress.IPv4Network(i), ipaddress.IPv4Network(i))
        except:
            try:
                pyt.insert(ipaddress.IPv6Network(i), ipaddress.IPv6Network(i))
            except:
                pass
except Exception as e:
    print('Unable to add subnets to Trie object - '+str(e))
    sys.exit()


# Identifying the subnet for each IP
try:
    # If the set is not empty
    if len(IP_DDI) != 0:
        for i in IP_DDI:
            a = i in pyt
            if a:
                IPSR_DDI.add(pyt.get_key(i) + ',' + str(i))
            if not a:
                IPSR_DDI.add(',' + str(i))
except Exception as e:
    print('Unable to find the relationship for the Subnets and IPs - '+str(e))
    sys.exit()

# Adding data to relationship file
try:
    # If the set is not empty
    if len(IPSR_DDI) != 0:
        IPSR_DDI_SORT = sorted(IPSR_DDI, key=keyfunc)
        with open(subnet_relationship_file, "a") as f:
            f.write('Subnet,IP\n')
            for iprha in IPSR_DDI_SORT:
                f.write(iprha + '\n')
except Exception as e:
    print('Unable to find the size of the IP relationship set and write to output file - '+str(e))
    sys.exit()