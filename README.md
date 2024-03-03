## Purpose of this project
* The script developed through this project helps automate the creation and deployment of Virtual Machines on Microsoft Azure and Google Cloud Platforms through their respective CLI/SDKs

## Files and Dependencies 
* This directory contains the `automate.py` script which initiates the Azure and GCP commands for VM creation, by reading in the configuration details from the `Azure.conf` and `GCP.conf` files. 
* Please review the `Documentation.pdf` file to view testing screenshots for the script.

## Preparing to run the script
* Please ensure you have an Active Microsoft Azure account
* Ensure you have the Azure CLI installed by running the command `az --version`
* Run the command `az login` to login to your Azure account through the Azure CLI
* Ensure relevant permissions have been granted to your account
* For GCP, ensure you have the SDK installed by running the command `gcloud --version`
* Run the command `gcloud auth login` to login to your GCP account through the GCP SDK
* For GCP, you need to ensure that a project has been set before any further operations. To do this, you can use the command `gcloud config set project PROJECT_ID`
* Alternatively, use the command `gcloud init` and follow the initiation procedures to set up your account and project


## How to run the script
* Depending on the python version you use, type in the following command in your terminal - 
```
python automate.py Azure.conf GCP.conf
```
* Please ensure you enter the conf files in this order only, and that they are present in the directory before you run the script.
* Please ensure the conf files are named `Azure.conf` and `GCP.conf`
* As of now, the configuration files consist of 2 Azure VM instances and 2 GCP VM instances, and hence the script will be using these config files to create 4 VM creation commands - 2 for each platform, given the specifications for each instance
* The script executed Azure CLI VM commands first followed by GCP SDK VM commands. 
* Once the script is run, you will be displayed the commands created one by one and asked to confirm whether you would like to proceed with their execution or not. 
* Please enter `Y` if you want to proceed or `N` if something doesn't look right. 
* On entering `Y` the script will proceed to execute that particular command and display the status of the VM as well as the output on the terminal. 
* On entering `N`, the script will skip the execution of this command, and move on to the next one. 
* The script guides and provides detailed messages on success/error to help the user understand the flow of the program. 
* The user should expect to give a couple minutes for each command's execution.
* Succesful output after creating an Azure VM could look like - 

```
{
  "fqdns": "",
  "id": "/subscriptions/9a74ec19-26a6-48ab-b4b2-cc822a266d82/resourceGroups/images/providers/Microsoft.Compute/virtualMachines/linuxServer01",
  "location": "canadacentral",
  "macAddress": "60-45-BD-5C-85-A4",
  "powerState": "VM running",
  "privateIpAddress": "10.0.0.4",
  "publicIpAddress": "20.151.227.78",
  "resourceGroup": "images",
  "zones": ""
}
```
* Succesful output after creating an GCP VM could look like - 
```
NAME           ZONE                       MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP    STATUS 
linuxserver01  northamerica-northeast2-a  n1-standard-1               10.188.0.6   34.130.207.35  RUNNING
```

## Program Flow
* Upon the successful creation of the VMs, the script generates documentation files with the date stamps.
* 2 files are created for the 2 separate platforms containing information about the VMs on those specific platforms.
* These files are named - `Azure_VMCreation_<date_stamp>.txt` and `GCP_VMCreation_<date_stamp>.txt`
* The program proceeds to rename the config files as `Azure_<date_stamp>.conf` and `GCP_<date_stamp>.conf` to mark the creation of VMs with the specified details. 
* The documentation files include all relevant VM information including date stamps, VM status, and other config details, for each instance 


## Notes for the TA - Additional Program Information and Testing Info
* For Azure VMs on Windows OS, the script will prompt the user to enter their Admin password and then confirm it before proceeding to create the VM.
* Please ensure the password is at least 12 characters long and has 3 of the following - 1 lowercase character, 1 uppercase character, 1 number, and 1 special character.
* The script has checks in place to validate the configuration files for the presence of the minimum required variables for both Azure and GCP platforms, and their correct names as well. 
* For GCP platforms, the script checks to see if the `name` of the VM instance has only lowercase characters and numbers, as per the specifications.  
* For Azure platforms, the script checks to see if the resource group mentioned exists or not, and if not, it asks the user to create the group through helpful messages.  
# Timestamp naming issue - 
* Windows environment does not allow ':' characters in file names and hence while adding timestamps to file names, I have used the characters ';' and '_' for differentiation. 
* When creating the 2nd VM instance in the Azure.conf file, I have used the location `canadacentral` instead of the Prof's example (westus3) as I kept getting permission errors to create the VM in that location. 


## Additional COnfiguration Variable Support Added for Azure 
* The program supports 2 additional configuration variables for Azure platform
* These are `public-ip-address` and `computer-name`
* The Azure.conf file includes these and the script incorporates these variables and their values when creating the commands for VM creation. 
* A sample command created could look like - 
```
az vm create --name linuxServer01 --resource-group images --image Ubuntu2204 --location canadacentral --admin-username azureuser --me MyAzureComputer --public-ip-address true --generate-ssh-keys --verbose 
```
* The command will successfully function without these added variables too. 
