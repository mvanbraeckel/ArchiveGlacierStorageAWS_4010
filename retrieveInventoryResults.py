'''
@author : Mitchell Van Braeckel
@id : 1002297
@date : 11/28/2020
@version : python 3.8-32 / python 3.8.5
@course : CIS*4010 Cloud Computing
@brief : A4 - Exploration and Fun!: Amazon S3 Glacier (Vaults) + Amazon SNS (Simple Notification Service); retrieveInventoryResults.py

@note :
    Description: Gets the results of a retrieve inventory job from the Glacier vault

    List Jobs:
    $ aws glacier list-jobs --account-id - --vault-name a4cis4010

    Describe Job:
    $ aws glacier describe-job --vault-name a4cis4010 --account-id - --job-id FmchQBRqlZUk2kSdkXJSRUhh6EliWwqZhnvsEmaoocZQuKQ3QXn_oZG_LBn7VsYXdY4kQZdoK8G63xV1VwCiC6-NumVW

    Get Job Output, Inventory:
    $ aws glacier get-job-output --account-id - --vault-name a4cis4010 --job-id FmchQBRqlZUk2kSdkXJSRUhh6EliWwqZhnvsEmaoocZQuKQ3QXn_oZG_LBn7VsYXdY4kQZdoK8G63xV1VwCiC6-NumVW output.json
'''

############################################# IMPORTS #############################################

import boto3
import json
import os
import sys

############################################ CONSTANTS ############################################

USAGE_STATEMENT = "Usage: py retrieveInventoryResults.py inventory-retrieval-job-id"
VAULT_NAME = "a4cis4010"

# Assume SNS exists (catch and exit if not)
SNS_TOPIC_NAME = "a4cis4010-sns"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:354464113200:a4cis4010-sns"

############################## STATE VARIABLES, INITIALIZATION, MAIN ##############################

def main():
    #globals
    global glacier_client
    global glacier_resource
    global job_tier

    # Expedited, Standard, or Bulk. Standard is default, bt that's 3-5hrs, so I want to muse Expedited for 1-5min instead
    job_tier = "Expedited"

    # ========== ARGUMENTS ==========

    # Collect command line arguments when executing this python script
    argc = len(sys.argv)
    bad_usage_flag = False
    job_id_input = ""

    # Check args (no checking for job ID)
    if argc != 2:
        bad_usage_flag = True
        print("Error: Incorrect number of arguments.")
    else:
        job_id_input = sys.argv[1]
    
    # Exit with usage statement if flag has been triggered for any reason
    if bad_usage_flag:
        sys.exit(USAGE_STATEMENT)

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
    
    # ========== RETRIEVE INVENTORY JOB RESULTS ==========

    # Retrieve the job results
    inventory = retrieve_inventory_results(VAULT_NAME, job_id_input)

    if inventory is None:
        sys.exit(f"ERROR: Inventory retrieval job results for Glacier vault '{VAULT_NAME}' job ID '{job_id_input}' failed.")
    print(f"Successfully retrieved inventory job results for Glacier vault '{VAULT_NAME}' - Job ID Input: {job_id_input}")
    print(f"Vault ARN: {inventory['VaultARN']}")
    for archive in inventory['ArchiveList']:
        print(f'  Size: {archive["Size"]:6d}  ', f'Archive ID: {archive["ArchiveId"]}')
    print(f"MY INVENTORY RESULTS: {inventory}\n")

############################################ FUNCTIONS ############################################

# Gets the results of an inventory retrieval job
#   Returns a dict of the inventory retrieval job results
def retrieve_inventory_results(vault_name, job_id):
    # Retrieve the job results
    try:
        response = glacier_client.get_job_output(vaultName=vault_name, jobId=job_id)
    except Exception as e:
        sys.exit(f"[ERROR] While getting inventory retrieval job results: {e}")

    # Read the streaming results into a dictionary
    return json.loads(response['body'].read())

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
