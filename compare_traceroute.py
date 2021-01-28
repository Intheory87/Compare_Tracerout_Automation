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

from netmiko import ConnectHandler
import getpass as getpass
import re
import os
from os import path
import sys

user = input("Enter your SSH USERNAME: ")
password = getpass.getpass()
change_state = input('Is this a Traceroute being preformed Pre or Post Change? ')
print('\n')
change_state = change_state.lower()
trace_destination = input('What is the Traceroute Desination you would like to test?')

#Compile Regex Filters
ipaddressRegex = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
noresolveRegex = re.compile(r'\*  \*  \*')


#Define List of IOS Devices
all_devices = []

#Open .txt file stored in local directory and create IOS device list. 
with open('device_ip_addresses.txt') as devices:
    for ip in devices:
        all_devices.append({'device_type': 'cisco_ios','ip': ip.rstrip(), 'username': user,'password': password,})


#Check to Change_State imputed by user to see if this change is being done pre or post configuration change
if change_state == 'pre':

#Loop though all IOS Devices in List
    for devices in all_devices:
        net_connect = ConnectHandler(**devices)
        print(devices['ip']+ ' Pre-Change Traceroute Results: \n')
    #Create File for each Router and write output to file
        with open('Pre_trace_raw_' +devices['ip']+ '.txt', 'w') as change_test_raw:
            raw_output = net_connect.send_command('traceroute ' +trace_destination+ ' numeric')
            change_test_raw.write(raw_output)

        #Open Raw Traceroute Output File and write IP Addresses to new file
        with open('Pre_trace_raw_' +devices['ip']+ '.txt') as trace_test_raw:
            with open('Pre_trace_' +devices['ip']+ '_to_' +trace_destination+ '.txt', 'w') as trace_test_clean:

            #Skip First Three lines of Traceroute Raw output        
                next(trace_test_raw)
                next(trace_test_raw)
                next(trace_test_raw)

                #loop through each line of Raw Output File
                for line in trace_test_raw:
                    #Match based on IP Regex Filter, write output to trace_test_clean.txt
                    if ipaddressRegex.search(line) != None:
                        filtered_ip = ipaddressRegex.search(line)
                        print(filtered_ip.group())
                        trace_test_clean.write(filtered_ip.group() + '\n')

                    #match unresolved IP Regex Filter, write output to trace_test_clean.txt    
                    elif noresolveRegex.search(line) != None:
                        filtered_noresolve = noresolveRegex.search(line)
                        print(filtered_noresolve.group())
                        trace_test_clean.write(filtered_noresolve.group() + '\n')

        #Print Footer                
        print('\nFile Name: Pre_trace_' +devices['ip']+ '_to_' +trace_destination+ '.txt')
        print('-' * 45)
        print('\n')

        #Delete Raw output text file
        os.remove('Pre_trace_raw_' +devices['ip']+ '.txt')

#Check if user selected Post as the change_state
if change_state == 'post':
    
    
    #Loop though all IOS Devices in List
    for devices in all_devices:
        net_connect = ConnectHandler(**devices)
        print('\n########################################################')
        print(devices['ip']+ ' Post-Change Traceroute Results:')
        print('########################################################\n')
        
        #Error Check to See if Pre-Change Test File Exists
        if path.exists('Pre_trace_' +devices['ip']+  '_to_' +trace_destination+ '.txt') == False:
            print('Error!!! File: Pre_trace_' +devices['ip']+  '_to_' +trace_destination+ '.txt is Missing!')
            print('Resolution: A Pre-Change Test to ' +trace_destination+ ' has not been yet from device ' +devices['ip']+ '.\nPlease re-run the Pre-Change Test or Double Check the IP Source and Destination')

    #Create File for each Router and write output to file
        else:
            with open('Post_trace_raw_' +devices['ip']+ '.txt', 'w') as change_test_raw:
                raw_output = net_connect.send_command('traceroute ' +trace_destination+ ' numeric')
                change_test_raw.write(raw_output)

            #Open Raw Traceroute Output File and write IP Addresses to new file
            with open('Post_trace_raw_' +devices['ip']+ '.txt') as trace_test_raw:            
                with open('Post_trace_' +devices['ip']+ '.txt', 'w') as trace_test_clean:

                #Skip First Three lines of Traceroute Raw output        
                    next(trace_test_raw)
                    next(trace_test_raw)
                    next(trace_test_raw)

                    #loop through each line of Raw Output File
                    for line in trace_test_raw:

                        #Match based on IP Regex Filter, write output to trace_test_clean.txt
                        if ipaddressRegex.search(line) != None:
                            filtered_ip = ipaddressRegex.search(line)
                            trace_test_clean.write(filtered_ip.group() + '\n')

                        #Match unresolved IP Regex Filter, write output to trace_test_clean.txt    
                        elif noresolveRegex.search(line) != None:
                            filtered_noresolve = noresolveRegex.search(line)
                            trace_test_clean.write(filtered_noresolve.group() + '\n')
            
            #Open Pre_Trace File to Prep for Compared Output
            with open('Pre_trace_' +devices['ip']+  '_to_' +trace_destination+ '.txt') as pre_trace_clean:
                pre_trace_hop_list = pre_trace_clean.readlines()
                
                pre_trace_hop_list_striped = []

                for ip in pre_trace_hop_list:
                    pre_trace_hop_list_striped.append(ip.rstrip())

            #Open Post Trace File and Prepare for Compared Output
            with open('Post_trace_' +devices['ip']+ '.txt') as post_trace_clean:
                post_trace_hop_list = post_trace_clean.readlines()

                post_trace_hop_list_striped = []

                for ip in post_trace_hop_list:
                    post_trace_hop_list_striped.append(ip.rstrip())

            #Check to see if Hop Count has changed between Pre and Post change tests, if match results are printed
            if len(pre_trace_hop_list_striped) != len(post_trace_hop_list_striped):
                print('Attention: Change in Hop Count Detected!!!')
                print('Pre-Change Hop Count: ' +str(len(pre_trace_hop_list_striped)))
                print('Post-Change Hop Count: ' +str(len(post_trace_hop_list_striped)))

              
                print('\nPre_Change Trace Route Results:')
                for ip in range(len(pre_trace_hop_list_striped)):
                    print(str(ip + 1)+ ' ' +pre_trace_hop_list_striped[ip])   
                
                print('\nPost_Change Trace Route Results:')
                for ip in range(len(post_trace_hop_list_striped)):
                    print(str(ip + 1)+ ' ' +post_trace_hop_list_striped[ip])

            #Check if Route Patch has changed between Pre and Post change tests, if match results are printed
            if len(pre_trace_hop_list_striped) == len(post_trace_hop_list_striped) and pre_trace_hop_list_striped != post_trace_hop_list_striped:
                print('Attention: Same Hop Count But A Route Change Detected!!! \n')
                
                hop_count = 1
                trace_hop_list_combined = zip(pre_trace_hop_list_striped, post_trace_hop_list_striped)

                for ip in range(len(pre_trace_hop_list_striped)):
                    if pre_trace_hop_list_striped[ip] == post_trace_hop_list_striped[ip]:
                        hop_count += 1

                    elif pre_trace_hop_list_striped[ip] != post_trace_hop_list_striped[ip]:
                        print('Route Change Detected at Hop Count: ' +str(hop_count))
                        print('Pre-Change Hop ' +str(hop_count)+ ' IP Address: ' +pre_trace_hop_list_striped[ip])
                        print('Post-Change Hop ' +str(hop_count)+ ' IP Address: ' +post_trace_hop_list_striped[ip])
                        print('\n-----------------------------')
                        print('Final Traceroute Results')
                        print("('Pre-Change', 'Post-Change')")
                        print('-----------------------------')
                        for ip in trace_hop_list_combined:
                            print(ip)

            #Check if Pre and Post change tests are identical, if matched the results are printed
            elif pre_trace_hop_list_striped == post_trace_hop_list_striped:
                print('Success!!! No Change Detected')
            
            #Removes trace test files from local directory
            os.remove('Pre_trace_' +devices['ip']+ '_to_' +trace_destination+ '.txt')
            os.remove('Post_trace_raw_' +devices['ip']+ '.txt')
            os.remove('Post_trace_' +devices['ip']+ '.txt')
    