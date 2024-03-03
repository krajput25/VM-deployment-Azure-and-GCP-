#
# Python script to automate the creation of VMs using Azure CLI and Google Cloud SDK
#

import sys
import subprocess
import datetime
import os
import re
import json

#
#   function to retrieve vm information from the Azure.conf file and generate the commands to be executed  
#   returns an array of Azure CLI commands
#
def generate_azure_commands(config_file):
    """
    This function allows the use of 2 additional config variables namely, 
    'public-ip-address' and 'computer-name' to create the VM creation command
    """
    commands = {}
    vm_count = 0
    command = ''

    with open(config_file, 'r') as file:
        lines = file.readlines()

        for line in lines:
            if line.startswith('['):
                vm_count += 1
                if vm_count > 10:                                               # since there can only be a maximum of 10 VMs
                    break
                if command:                                                     # add the azure cli command to the dictionary
                    command += ' --generate-ssh-keys --verbose'                 # add relevant flags to the command
                    commands[command] = win_flag                                # indicate whether windows os or not
                command = 'az vm create'                                        # reassign value of command for new VM 
            else:
                line = line.strip()
                if line:
                    parts = line.split(' = ')
                    if len(parts) == 2:
                        key, value = parts
                        if key in ['name', 'resource-group', 'image', 'location', 'public-ip-address', 'computer-name', 'admin-username']:
                            command += f' --{key} {value}'
                        if key == 'os':
                            win_flag = (value == 'windows')                     # this flag will indicate whether user is to be prompted for password or not

    if command:                                                                 # for the last command
        command += ' --generate-ssh-keys --verbose'
        commands[command] = win_flag    
    
    return commands


#
#   function to retrieve vm information from the GCP.conf file and generate the commands to be executed  
#   returns an array of GCP SDK commands
#
def generate_gcp_commands(config_file):
    commands = []
    vm_count = 0
    command = ''

    with open(config_file, 'r') as file:
        lines = file.readlines()

        for line in lines:
            if line.startswith('['):
                vm_count += 1
                if vm_count > 10:                                               # since there can only be a maximum of 10 VMs
                    break
                if command:                                                     # add the azure cli command to the dictionary
                    command += ' --subnet=default'                              # add relevant flags to the command
                    commands.append(command)
                command = 'gcloud compute instances create'                     # reassign value of command for new VM 
            else:
                line = line.strip()
                if line:
                    parts = line.split(' = ')
                    if len(parts) == 2:
                        key, value = parts
                        if key == 'name':
                            command += f' {value}'
                        if key == 'imageproject':
                            command += f' --image-project {value}'
                        if key in [ 'image', 'zone']:
                            command += f' --{key} {value}'

    if command:                                                                 # for the last command
        command += ' --subnet=default'                                          # add relevant flags to the command
        commands.append(command)   
    
    return commands


#
#   function to execute the cloud commands and print the outputs on the terminal
#
def run_cloud_command(command):
    try:
        # using the 'subprocess' module to facilitate command execution
        result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error in executing command:", e)
        return None


#
#   function to get system admin user name
#
def get_username():
    try:
        command = 'az account show --query user.name'
        result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
        return result.stdout 
    except subprocess.CalledProcessError as e:
        print("Could not execute command to retrieve user name: ", e)
        return None
    
#
#   function to write VM details to Azure VM documentation file 
#
def write_to_azuredocfile(timestamp, file_name, config_file):
    data = "Date Stamp: " + timestamp + "\nSystem Admin Name: " + get_username()

    with open(config_file, 'r') as file:
        lines = file.readlines()
        i = 0
        for line in lines:
            if line.startswith('['):
                i = i + 1
                data += '\nAzure VM ' + str(i) + '\n'
                data += '\nStatus of the VM: VM Running'
            else:
                line = line.strip()
                if line:
                    parts = line.split(' = ')
                    if len(parts) == 2:
                        key, value = parts
                        if key in ['name', 'purpose', 'team', 'os', 'resource-group', 'image', 'location']:
                            data += f'{key}: {value}\n'

    try:
        with open(file_name, 'w') as file:
            file.write(data)
        return True
    except Exception as e:
        print("Error writing to file:", e)
        return False


#
#   function to write VM details to GCP VM documentation file 
#
def write_to_gcpdocfile(timestamp, file_name, config_file):
    data = "Date Stamp: " + timestamp + "\nSystem Admin Name: " + get_username()

    with open(config_file, 'r') as file:
        lines = file.readlines()
        i = 0
        for line in lines:
            if line.startswith('['):
                i = i + 1
                data += '\nGCP VM ' + str(i) + '\n'
                data += '\nStatus of the VM: VM Running'
            else:
                line = line.strip()
                if line:
                    parts = line.split(' = ')
                    if len(parts) == 2:
                        key, value = parts
                        if key in ['name', 'project','purpose', 'team', 'os', 'image', 'zone', 'imageproject']:
                            data += f'{key}: {value}\n'

    try:
        with open(file_name, 'w') as file:
            file.write(data)
        return True
    except Exception as e:
        print("Error writing to file:", e)
        return False


#
#   function to facilitate Azure VM creation and documentation file creation
#
def create_azure_VMs(azure_commands_dict, config_file):
    print('\nMICROSOFT AZURE VM CREATION\n')
    for key, value in azure_commands_dict.items():
        print('Executing command: ', key)
        confirmation = input('Do you want to proceed with this command? (Y/N): ').strip().lower()           # asking the user to confirm command
        if confirmation == 'y':
            print('Running the command to create VM...')
            output = run_cloud_command(key)
            print(output)
        else:
            print('Skipping command...\n')

    # get the time stamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d;%H_%M_%S")
    # Define the VM documentation file name
    file_name = f"Azure_VMCreation_{timestamp}.txt"
    write_to_azuredocfile(timestamp, file_name, config_file)
    # rename the Azure.conf file 
    os.rename('Azure.conf', 'Azure_' + timestamp + '.conf')


#
#   function to facilitate GCP VM creation and documentation file creation
#
def create_gcp_VMs(gcp_commands, config_file):
    print('\nGOOGLE CLOUD PLATFORM (GCP) VM CREATION\n')
    for item in gcp_commands:
        print('Executing command: ', item)
        confirmation = input('Do you want to proceed with this command? (Y/N): ').strip().lower()           # asking the user to confirm command
        if confirmation == 'y':
            print('Running the command to create VM...')
            output = run_cloud_command(item)
            print(output)
        else:
            print('Skipping command...\n')

    # get the time stamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d;%H_%M_%S")
    # Define the VM documentation file name
    file_name = f"GCP_VMCreation_{timestamp}.txt"
    write_to_gcpdocfile(timestamp, file_name, config_file)
    # rename the GCP.conf file
    os.rename('GCP.conf', 'GCP_' + timestamp + '.conf')


#
#   function to check if Azure.conf and GCP.conf files exist
#
def files_exist(file1, file2):
    if file1 == 'Azure.conf' and file2 == 'GCP.conf':
            return True
    else:
        return False



# function to check whether a Azure reource group exists or not
def check_resource_group_exists(resource_group):
    # command = 'az group show --name ' +  resource_group
    command = 'az group show --name imagesblah'
     # Execute the command
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Check the exit code of the command
    if process.returncode == 0:
        print(f"Resource group '{resource_group}' exists.")
        return True
    else:
        print(f"Resource group '{resource_group}' does not exist or there was an error.")
        print("Error message:", stderr.decode())
        return False

#
# function to check for presence of required and correct variables in the Azure config file 
#
def valid_azure_config(config_file):
    config = {}
    current_vm = None
    with open(config_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_vm = line[1:-1]
                config[current_vm] = {}
            elif line:
                key, value = line.split(' = ')
                config[current_vm][key.strip()] = value.strip()
    
    # based on mandatory variables required by the Azure CLI to create a VM
    required_fields = ['name', 'resource-group', 'image', 'location', 'admin-username']

    for vm_instance in config:
        for field in required_fields:
            if field not in config[vm_instance]:
                print('Error - Required Variable in Azure config missing.')
                return False
            
    
    # Check if the resource group exists
    # if not check_resource_group_exists(config[vm_instance]['resource-group']):
    #     print(f'\nError - Resource group "{config[vm_instance]["resource-group"]}" does not exist.')
    #     print('Please create the resource group using the Azure CLI before proceeding.')
    #     return False

    return True

#
# function to check for presence of required and correct variables in the GCP config file 
#
def valid_gcp_config(config_file):
    config = {}
    current_vm = None
    with open(config_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_vm = line[1:-1]
                config[current_vm] = {}
            elif line:
                key, value = line.split(' = ')
                config[current_vm][key.strip()] = value.strip()

    # based on mandatory variables required by the GCP SDK to create a VM
    required_fields = ['name', 'image', 'imageproject', 'zone']                 

    for vm_instance in config:
        for field in required_fields:
            if field not in config[vm_instance]:
                print('Error - Required Variable in GCP config missing.')
                return False
            
    # Check if name consists only of lowercase letters and numbers
        if not re.match('^[a-z0-9]+$', config[vm_instance]['name']):
            print('\nError - Name variable in GCP config should consist only of lowercase letters and numbers.')
            return False

    return True


#
#   function to create the Azure_VMCreation_<date_stamp>.txt and GCP_VMCreation_<date_stamp>.txt documentation files, after VM creation
#
def create_documentation_files(file1, file2):
    print('documentation file created')

#
#   main function to run script
#
if __name__ == "__main__":
    # Check if both conf files have been provided
    if len(sys.argv) != 3:
        print("\nError - Expected command format - python automate.py Azure.conf GCP.conf")
        sys.exit()
    else:       
         # check if both files with correct names exist 
        if (files_exist(sys.argv[1], sys.argv[2]) == False):                            
            print('\nError - One or both config files could not be found or do not exist. Exiting program ...')
            sys.exit()
        # check if the config files have valid and required variables 
        elif (valid_azure_config(sys.argv[1]) == False or valid_gcp_config(sys.argv[2]) == False):
            print('\nError - Please include the minimum required variables and the specifications for their values, for VM creation, in the config files and try again.')
            sys.exit()
        # if all preliminary checks pass, create the VMs
        else:
            azure_commands_dict = generate_azure_commands(sys.argv[1])
            create_azure_VMs(azure_commands_dict, sys.argv[1])                                         # create the Azure VMs
            gcp_commands = generate_gcp_commands(sys.argv[2])
            create_gcp_VMs(gcp_commands, sys.argv[2])                                                               # create the GCP VMs