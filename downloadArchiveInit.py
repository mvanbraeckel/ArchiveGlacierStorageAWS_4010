'''
@author : Mitchell Van Braeckel
@id : 1002297
@date : 11/28/2020
@version : python 3.8-32 / python 3.8.5
@course : CIS*4010 Cloud Computing
@brief : A4 - Exploration and Fun!: Amazon S3 Glacier (Vaults) + Amazon SNS (Simple Notification Service); downloadArchiveInit.py

@note :
    Description: Initiates a job to retrieve an archive from the Glacier vault

    List Jobs:
    $ aws glacier list-jobs --account-id - --vault-name a4cis4010
    
    Init Job, Archive Retrieval: overkill.jpg
    $ aws glacier initiate-job --account-id - --vault-name a4cis4010 --job-parameters '{"Type": "archive-retrieval", "ArchiveId": "h8OIw_5GGHzQ4ZgHvAuk6DYbE7aSmE9QKrkyAYQ1U0S0wgijn3lHToUyL7aSAbHqnIqLpcRbPWWfYqmyCLvRTorxQrO0igLrLm292wrydyJkiJ1yKeai0gZoGvnvaAElw1I3CT5OAQ", "SNSTopic": "arn:aws:sns:us-east-1:354464113200:a4cis4010-sns", "Tier": "Expedited"}'

    Describe Job:
    $ aws glacier describe-job --vault-name a4cis4010 --account-id - --job-id JOBID
'''

############################################# IMPORTS #############################################

import boto3
import datetime
import os
import sys

############################################ CONSTANTS ############################################

USAGE_STATEMENT = "Usage: py downloadArchiveInit.py archive-id <Tier(Expedited,Standard,Bulk)|optional>"
VAULT_NAME = "a4cis4010"

# Assume SNS exists (catch and exit if not)
SNS_TOPIC_NAME = "a4cis4010-sns"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:354464113200:a4cis4010-sns"

############################## STATE VARIABLES, INITIALIZATION, MAIN ##############################

def main():
    #globals
    global glacier_client
    global glacier_resource

    # Expedited, Standard, or Bulk. Standard is default, but that's 3-5hrs, so I want to use Expedited for 1-5min instead
    # UPDATE: nvm, I would need to buy provisioned capacity, which costs $100USD/month
    archive_id_input = ""
    job_tier = "Standard" #"Expedited"

    # ========== ARGUMENTS ==========

    # Collect command line arguments when executing this python script
    argc = len(sys.argv)
    bad_usage_flag = False

    # Check args (no checking for archive ID)
    if argc >= 2:
        archive_id_input = sys.argv[1]
    if argc >= 3:
        if sys.argv[2].lower() != "expedited" and sys.argv[2].lower() != "standard" and sys.argv[2].lower() != "bulk":
            bad_usage_flag = True
            print("Error: Optional 'Tier' value must be 'Expedited', 'Standard', or 'Bulk'.")
        else:
            # Store as proper case string (maybe use .title() instead)
            job_tier = sys.argv[2].lower()
            job_tier = job_tier[1].upper() + job_tier[1:]
    if argc > 3:
        bad_usage_flag = True
        print("Error: Too many arguments.")
    
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
    
    # ========== INIT JOB RETRIEVE ARCHIVE ==========

    # Initiate an archive retrieval job
    response = retrieve_archive(VAULT_NAME, archive_id_input, job_tier)

    if response is None:
        sys.exit(f"ERROR: Archive retrieval job initiation for Glacier vault '{VAULT_NAME}' failed.")
    print(f"Successfully initiated archive retrieval job for Glacier vault '{VAULT_NAME}' - Archive Retrieval Job ID: {response['jobId']}")
    print(f"MY ARCHIVE RETRIEVAL JOB: {response}\n")

############################################ FUNCTIONS ############################################

# Initiates an Amazon Glacier archive-retrieval job
#   Returns a dict of info related to the job initiated
def retrieve_archive(vault_name, archive_id, job_tier):
    # Construct job parameters
    job_params = {
        'Type': 'archive-retrieval',
        'ArchiveId': archive_id,
        'Description': f'init archive retrieval at {datetime.datetime.now()}',
        'SNSTopic': SNS_TOPIC_ARN, #explicit just in case
        'Tier': job_tier
    }

    # Initiate the job
    try:
        response = glacier_client.initiate_job(vaultName=vault_name, jobParameters=job_params)
    except Exception as e:
        sys.exit(f"[ERROR] While initiating archive retrieval job - {e}")
    return response

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
