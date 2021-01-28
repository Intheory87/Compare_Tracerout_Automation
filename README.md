# Compare_Traceroute_Automation
In Theory Networks, Network Automation Projects

###############################################################################################
#Uses Netmiko to Connect to a list of Cisco IOS Device (device_ip_addresses.txt) 
#and compares a Traceroute taken before a network change to a Traceroute take after the change. 
###############################################################################################

###############################################################################################
#Requirements: -SSH Access to Cisco IOS Devices listed in device_ip_addresses.txt
#              -Python modules netmiko, getpass, re, os, sys
#              -Network access to Traceroute Destination
###############################################################################################

###############################################################################################
#Usage: 1) Populate device_ip_addresses.txt with list of IOS devices you would like to run Traceroute tests from
#       2) Run Python Script prior to making network change, select 'Pre' Change State option at the begining of the script.
#       3) Make Desired Network Changes
#       4) Run Python Script after making your network change, select 'Post' Change State option at the begining of the script.
###############################################################################################
