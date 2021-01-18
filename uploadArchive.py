'''
@author : Mitchell Van Braeckel
@id : 1002297
@date : 11/28/2020
@version : python 3.8-32 / python 3.8.5
@course : CIS*4010 Cloud Computing
@brief : A4 - Exploration and Fun!: Amazon S3 Glacier (Vaults) + Amazon SNS (Simple Notification Service); uploadArchive.py

@note :
    Description: Uploads a given filename to the Glacier vault

    List Vaults:
    $ aws glacier list-vaults --account-id -

    Upload Archive:
    $ aws glacier upload-archive --account-id - --vault-name a4cis4010 --body nstemp.jpg
'''

############################################# IMPORTS #############################################

import boto3
import datetime
import os
import sys

############################################ CONSTANTS ############################################

USAGE_STATEMENT = "Usage: py uploadArchive.py filenameToUpload"
VAULT_NAME = "a4cis4010"

# Assume SNS exists (catch and exit if not)
SNS_TOPIC_NAME = "a4cis4010-sns"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:354464113200:a4cis4010-sns"

############################## STATE VARIABLES, INITIALIZATION, MAIN ##############################

def main():
    #globals
    global glacier_client
    global glacier_resource

    # ========== ARGUMENTS ==========

    # Collect command line arguments when executing this python script
    argc = len(sys.argv)
    bad_usage_flag = False
    filename = ""

    # Check args
    if argc != 2:
        bad_usage_flag = True
        print("Error: Incorrect number of arguments.")
    elif not os.path.isfile(sys.argv[1]):
        bad_usage_flag = True
        print(f"Error: Invalid file name '{sys.argv[1]}' - file does not exist.")
    
    # Exit with usage statement if flag has been triggered for any reason
    if bad_usage_flag:
        sys.exit(USAGE_STATEMENT)
    filename = sys.argv[1] #valid filename

    # ========== GLACIER ==========
    glacier_client = boto3.client("glacier")
    glacier_resource = boto3.resource("glacier")

    # Validate AWS credentials (by testing if 'describe_instances()' works)
    try:
        glacier_client.list_vaults()
    except Exception as e:
        print("Error: Invalid or expired credentials (or insufficient permissions to call 'list_vaults()')")
        sys.exit(f"[ERROR] {e}")

    # ========== VAULTS ==========

    # Get all vaults for this account, and check if vault exists first
    vault_list = list_glacier_vaults()
    my_vault, vault_exists_flag = verify_vault_exists(vault_list, VAULT_NAME)

    if vault_exists_flag :
        # Display vault info
        print(f"MY VAULT:\n{my_vault}\n")
    else:
        sys.exit(f"ERROR: Vault '{VAULT_NAME}' does not exist - Terminating program.")
    
    # ========== UPLOAD ==========

    # Upload the filename and print the result if successful (otherwise an err msg)
    archive = upload_archive_to_vault(VAULT_NAME, filename)
    if archive is None:
        sys.exit(f"ERROR: File '{filename}' upload to Glacier vault '{VAULT_NAME}' failed.")
    print(f"File '{filename}' successfully uploaded and added to Glacier vault '{VAULT_NAME}' as an archive - Archive ID: {archive['archiveId']}")
    print(f"MY ARCHIVE: {archive}\n")

############################################ FUNCTIONS ############################################

# Uploads/Adds the designated file as an archive to the Glacier vault (synchronously)
#   Returns a dict of archive info from the upload_archive() operation
def upload_archive_to_vault(vault_name, filename):
    # Prep file to upload
    try:
        object_data = open(filename, 'rb')
    except Exception as e: # possible FileNotFoundError/IOError exception, etc
        sys.exit(f"[ERROR] While reading from file '{filename}': {e}")
        return None

    # Upload the file object data, and close the open file before leaving
    try:
        archive = glacier_client.upload_archive(vaultName=vault_name, archiveDescription=f'upload file {filename} at {datetime.datetime.now()}', body=object_data)
        object_data.close()
    except Exception as e:
        object_data.close()
        sys.exit(f"[ERROR] While uploading archive - {e}")
    return archive # Return dict of archive information

############################################# HELPERS #############################################

# Get info list for all vaults for this account
# NOTE: iter_marker used when there are more vaults to retrieve still (default 10 vaults), where it marks start of next batch of vaults to retrieve
def get_glacier_vaults_list_info(max_vaults=10, iter_marker=None):
    # Check if there's a starting value for vault retrieval
    if iter_marker is None:
        vaults = glacier_client.list_vaults(limit=str(max_vaults))
    else:
        vaults = glacier_client.list_vaults(limit=str(max_vaults), marker=iter_marker)
    
    # Returns a list of dictionaries containing vault information, and the marker (none if no more vaults to retrieve)
    marker = vaults.get('Marker')
    return vaults['VaultList'], marker

# Create a list of all glacier vaults for this account
def list_glacier_vaults():
    # List the vaults
    vault_list = []
    vaults, marker = get_glacier_vaults_list_info()

    print("--Getting all vaults...")
    while True:
        # Add info about retrieved vaults
        print(f"- VaultName\tNumberOfArchives\tSizeInBytes")
        for vault in vaults:
            print(f"-{vault['VaultName']}\t{vault['NumberOfArchives']}\t\t\t{vault['SizeInBytes']}\t")
            vault_list.append(vault)

        # Exit if no more vaults, otherwise retrieve the next batch
        if marker is None:
            break
        try:
            vaults, marker = get_glacier_vaults_list_info(iter_marker=marker)
        except Exception as e:
            sys.exit(f"[ERROR] While getting list of Glacier vaults: {e}")
    print("...Done getting all vaults--\n")
    return vault_list

# Returns true if the vault exists in the list of vaults for this account
# Returns the vault dictionary of the given vault name if it exists, otherwise None
def verify_vault_exists(vault_list, vault_name):
    my_vault = None
    vault_exists_flag = False
    # Check if vault name exists for this account
    for vault in vault_list:
        if vault['VaultName'] == vault_name:
            vault_exists_flag = True
            my_vault = vault
            break
    return my_vault, vault_exists_flag

###################################################################################################

main()
