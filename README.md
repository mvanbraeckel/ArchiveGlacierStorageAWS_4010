# ArchiveGlacierStorageAWS_4010
Exploration and Fun! - Archival Storage using Amazon S3 Glacier (Vaults) + Amazon SNS (Simple Notification Service) (Cloud Computing course A4)

# Info

- Name: Mitchell Van Braeckel
- Student ID: 1002297
- Course: CIS*4010 Cloud Computing
- Assignment: 4
- Brief: Exploration and Fun! - Amazon S3 Glacier (Vaults) + Amazon SNS (Simple Notification Service)
- Due: (Extended) Dec 4, 2020

## Instructions

In this class we have looked at 3 cloud platforms: AWS, Azure, and Google Cloud.  We have also looked at some of the popular functions on those platforms including storage, VM instances, serverless functions, and somePaaS offerings from AWS and Azure (image processing, AI, text processing, etc.)

For this assignment to end the assignment portion of the course, you are to explore the Cloud landscape looking for other platforms and/or other services on the three platforms studied that were not mentioned in the course

- If you are using a new platform, then you should either:
  1. adapt one of the previous assignments to work on this new platform
  2. if the system is very specialized like DWave, then take one of their tutorials or demos, get it working, and then add to it to do something interesting

- If you are using one of the three platforms covered in class, but are using a service or feature that we did not cover, then you should either:
  1. take one of their tutorials or demos, get it working, and then add to it to do something interesting
  2. use this service or feature to do something that you always wanted to do or something that fits into some other project or assignment that you are doing independently or in another course

Yes, there is a great deal of choice in this assignment and you are probably thinking, "just what does she want?" but honestly, the assignment will be graded generously if you document what you are doing and you show some imagination and/or interest in what you have chosen to do.

Trust yourself and follow your interests and explore!

- What do you need to hand in?
  - In the A4 GitLab repo, put all source code/scripts and a README file that explains how to run your code.
  - Also put a small document (text or PDF) explaining what you did, why you did it, and what you learned.
  - This report does not need to be more than 2 pages in length.

### Approach

- Using AWS, S3 Glacier Vault + SNS (Simple Notification Service)
- Will not follow any tutorials, and will do something I just wanted to try out because it piqued my curiosity. Main points:
  - Glacier is an immutable storage system because archives are immutable.
    - i.e. After you upload an archive, you cannot edit the archive or its description.
  
### How I got the Idea

- I was looking at how memory space on my laptop is slowly getting full with lots of old schoolwork stuff and was thinking about alternative cloud solutions to store all my stuff away besides just uploading to my Google Drive or One Drive or something
  - Although, I won't be using Glacier to do this, I thought it would be fun to try using it and seeing what an immutable storage system is like that's purposed for actual archives (i.e. I think of archives as super old info people will barely ever need to access, but copies still need to be kept)
    - FUN FACT: After all, "Glacier" is a very fitting name as glacier ice tens to be nearly 100 years old, with the oldest Alaskan glacier ice ever recovered is about 30,000 years old (from a basin between Mt. Bona and Mt. Churchill)
      - This also plays along with how I interrupt archives (explained above), and vaults (durable safekeeping for long periods of time where things are stored but rarely ever withdrawn)
- I figured that Glacier as an archival storage system could be used in many different ways, or rather implemented/integrated for many different things as an archival storage system for old data has passed a certain date-time threshold to become archived.
  - I was also intrigued by the AWS SNS notifications, but one of my friends had already mostly finished an A4 using this, so it didn't feel right to do the same thing.
    - By using Glacier, I still got to look into SNS and how it works since I could make life easier and design the Glacier vault email notifications are sent out when a retrieval operation finishes.
      - This was done by connecting a SNS topic to the Glacier vault and enabling notifications for both retrieval operations, then adding email subscriptions to the topic so they would receive notifications when messages are automatically published to the SNS topic when Glacier vault retrieval operation(s) complete.
- Plus, as I was looking at different cloud services I might be able to use for A4, Glacier stood out because it's a cool word. :D

### Takeaways

- I can definitely see how this would be useful for archival purposes
  - However, I am personally very uneasy about the large costs for expedited tier and the very long 3-5+ hours retrieval operations (inventory, archives) and that inventory updates only once a day
    - The few times one may want to withdraw something, it becomes very difficult. From my personal view, this seems like something I would use to throw things away and forget about them.
      - Until inventory updates (approximately the next day), you won't know it's present in the vault inventory unless you keep track of things added yourself
      - Also, if the user doesn't add descriptions to things, they won't even know what each archive is later on
      - Moreover, it's unlikely for someone to save all the Archive IDs, so waiting for inventory retrieval operation is required
      - In addition, JobIDs only last 24 hours, so the user would need to do a retrieval operation again if they still needed that JobID info the next day
- Overall, I mostly discovered the pain of working with immutable archives with an extremely long (multiple hours, nearing 1/4 of the day)
  - This made developing and testing kind of pointless and I was better off thoroughly researching and planning, the coding and testing at the end rather than incrementally developing and testing like how I usually do
    - So, on the bright side, I became much more resourceful in this regard and was able to figure out how to do everything on my own, especially because nobody else (none of my friends) did the same thing and there wasn't even bouncing of ideas or links/resources.
      - In addition, there was not much documentation of how to do this in python. The AWS website for Glacier stuff only had examples for Java and .NET SDKs, so I just logically learned about Glacier and how it works before diving into APIs for Boto3 Glacier and AWS CLI Glacier.
        - So I mostly just kept searching the internet and googling things to find out how todo specific things and then put everything together.
      - Although it was very interesting, I don't think I would want to deal with this kind of stuff and believe using Glacier is suited for a purely archival purpose.
- Furthermore, regarding the pain of working with Glacier and the lack of python documentation, I really want to mention AWS Console. I had taken the console for granted, when it's actually really useful and helpful.
  - I learned that I was severely under-appreciating the convenience of the AWS console while working with Glacier, since it barely has any support.
    - It can only Create and Delete vaults, manage some settings, and display a very limited amount of information.
    - In order to upload files as archives, find out what archives are actually in the vault inventory, or download archives as files, you need to use code/scripts and/or AWS CLI for Glacier:
      - First, uploaded archives don't appear until the vault inventory updates, which happens once per day and you can't force the inventory to update somehow either.
        - Also, the first uploads don't show up and you aren't able to retrieve anything until a half to a full day has passed.
      - Second, retrieving inventory or archives from the vaults requires 2 operations each: initiating a retrieval, waiting for it to finish/complete and then getting the job output; where the retrieval job takes ~3-5 hours to complete (but expedited tier retrieval operations, even if only 1-5min long, are VERY costly: $100USD/month to buy a provisioned capacity, and the use rate fee is also many times more expensive).
      - Third, you need to track Archive IDs and Job IDs yourself -- If you forget, you need to retrieve inventory again, and make another archive retrieval job, each which will take a long time to complete.
      - Fourth, you can't even see your inventory or archives unless you start an inventory retrieval job (which takes a long time), even then, you still don't really know what's in the vault (unless you have really good descriptions on everything)
        - Even if you have good descriptions, you can't actually see the archives (eg. file contents, folder contents, image previews, etc.)
    - Although, I could've just used AWS CLI only, felt like I would've been taking it to easy (even if I made something like bash scripts that used AWS CLI Glacier commands), so I used Python 3 Boto3 like in most of the other AWS Cloud assignments.
      - After dealing with multiple AWS services using Python3 Boto3, I feel pretty confident using this now (or at least much more confident in practical application compared to using other cloud services, eg. Azure, Google Cloud, etc.)
  - In summary, I really appreciate the convenience of the AWS Console, as well as the ability to use AWS CLI to just test out services and view things a little easier before developing my own scripts -- without these, it becomes a lot more difficult and frustrating when you misinterpret things and find out later on and then need to change/redo things.

## Cloud System: AWS

- Name & Location of Amazon S3 Glacier Vault: `a4cis4010` on Amazon S3 Glacier (typically referred to as just Glacier)
- Name & Location of Amazon SNS Topic where the 'Archive' & 'Vault Inventory' Retrieval Job Complete notification messages are published: `a4cis4010-sns` on Amazon SNS
- Programming language used: Python 3

### Brief description of how it was set up

The following can be done via the AWS Console:

1. Precondition - Create Glacier Vault & SNS Topic:

   - `a4cis4010` as Glacier vault for archives
   - `a4cis4010-sns` as SNS topic to publish messages

2. Precondition - Subscribe some emails to the SNS topic:

   - Use protocol `EMAIL`:
     - mvanbrae@uoguelph.ca
     - some other emails to show works for multiple (eg. personal Gmail, etc.)

### Brief File Usage

Sincere there is no AWS Console support for archive operations (eg. upload, download, deletion), the following must be done using the AWS CLI or scripts/code:

1. **Upload Archives** via Python 3 script (`uploadArchive.py`) for at least 2 files :

   - An archive file is any object, such as a photo, video, or document -- I will be using images for convenience:
     - Ensure the image being uploaded is in the same directory location as the script (ideally file size is smaller)

2. **Download Archives** via Python 3 script (`uploadArchive.py`):

   - The downloaded archive file object will be stored in the same directory location as the script (as both a `.bin` and `.jpg`)

3. **Delete Archive** via AWS CLI (reference: https://docs.aws.amazon.com/amazonglacier/latest/dev/getting-started-delete-archive-cli.html):

- NOTE: Here, I will use the vault name `awsexamplevault` with account ID `111122223333` instead of my vault name and account ID.
- NOTE: `*** varName ***` are template holders meant to be filler with a proper value when actually being used, where this data is gathered from another command or operation.
- NOTE: This is a full step-by-step if no IDs have been saved, so it also shows a few other AWS CLI Glacier commands that are useful to us.

   1. Use the `initiate-job` command to start an inventory retrieval job:

        ```bash
        $ aws glacier initiate-job --vault-name awsexamplevault --account-id 111122223333 --job-parameters '{"Type": "inventory-retrieval"}'
        ```

    - Expected output:
  
        ```json
        {
            "location": "/111122223333/vaults/awsexamplevault/jobs/*** jobid ***", 
            "jobId": "*** jobid ***"
        }
        ```

   2. Use the `describe-job` command to check status of the previous retrieval job.

        ```bash
        $ aws glacier describe-job --vault-name awsexamplevault --account-id 111122223333 --job-id *** jobid ***
        ```

    - Expected output:

        ```json
        {
            "InventoryRetrievalParameters": {
                "Format": "JSON"
            }, 
            "VaultARN": "*** vault arn ***", 
            "Completed": false, 
            "JobId": "*** jobid ***", 
            "Action": "InventoryRetrieval", 
            "CreationDate": "*** job creation date ***", 
            "StatusCode": "InProgress"
        }
        ```

   3. Wait for the job to complete -- we have already set up SNS for our vault:

   - You must wait until the job output is ready for you to download. If you set a notification configuration on the vault or specified an Amazon Simple Notification Service (Amazon SNS) topic when you initiated the job, S3 Glacier sends a message to the topic after it completes the job.

   - You can set notification configuration for specific events on the vault. For more information, see Configuring Vault Notifications in Amazon S3 Glacier. S3 Glacier sends a message to the specified SNS topic anytime the specific event occurs.

   4. When it's complete, use the `get-job-output` command to download the retrieval job to the file `output.json`.

        ```bash
        $ aws glacier get-job-output --vault-name awsexamplevault --account-id 111122223333 --job-id *** jobid *** output.json
        ```

    - Expected output - This command produces a file with the following fields:

        ```json
        {
        "VaultARN":"arn:aws:glacier:region:111122223333:vaults/awsexamplevault",
        "InventoryDate":"*** job completion date ***",
        "ArchiveList":[
            {
            "ArchiveId":"*** archiveid ***",
            "ArchiveDescription":*** archive description (if set) ***,
            "CreationDate":"*** archive creation date ***",
            "Size":"*** archive size (in bytes) ***",
            "SHA256TreeHash":"*** archive hash ***"
            },
            {
            "ArchiveId": ...etc...
            },
            {...etc...}
        ]
        }
        ```

   5. Use the `delete-archive` command to delete an archive from a vault using its archive-id that we retrieved.

        ```bash
        $ aws glacier delete-archive --vault-name awsexamplevault --account-id 111122223333 --archive-id *** archiveid ***
        ```

### Overall Usage

- NOTE: `retrieveInventoryInit.py` and `retrieveInventoryResults.py` aren't really necessary, but are just alternatives to AWS CLI
  - Technically, I could've done everything purely through the CLI, but decided it would be fun if I actually coded more and looked through Boto3 docs to figure stuff out(the guidelines on AWS were only for Java and .NET SDKs)
  - We will ignore these scripts for the purpose of a more streamlined usage
    - These are only if you forget Job IDs or Archive IDs required for `downloadArchiveInit.py` and `downloadArchiveResult.py`
      - However, the scripts I made output/log necessary info, including these IDs
      - Job IDs usually last ~24 hours
    - Archives are immutable. After you upload an archive, you cannot edit the archive or its description.
  - For good measure:
    - Retrieve vault inventory: `"Usage: py retrieveInventoryInit.py"` (approx 3-5 hours)
      - Take not of the **Inventory Retrieval Job ID** created
    - Wait until this job finishes
      - Will get an email notification from Amazon SNS system when complete (we already set this up)
      - Alternatively can use AWS CLI commands to check when job status is complete:
        - List Jobs: `$ aws glacier list-jobs --account-id - --vault-name a4cis4010` (look for the entry of the noted Job ID)
        - Describe Job: `$ aws glacier describe-job --vault-name a4cis4010 --account-id - --job-id JOBID`
    - Get the output of the inventory retrieval job, i.e. download/get the inventory of the vault as a JSON response: `"Usage: py retrieveInventoryResults.py inventory-retrieval-job-id"`

### Overall Usage Steps

- Upload a file: `"Usage: py uploadArchive.py filenameToUpload"`
  - Take note of the **Archive ID** created
- Initiate a job to retrieve an archive: `"Usage: py downloadArchiveInit.py archive-id <Tier(Expedited,Standard,Bulk)|optional>"`
  - Default to "Expedited" tier because it takes 1-5min even if it costs a bit more
    - Whereas the normal "Standard" tier is cheap, but takes 3-5 hours
    - For our purposes, we don't need to bother using "Bulk" and we should not unless different preconditions are set up
    - ***UPDATE: nvm, I would need to buy provisioned capacity, which costs $100USD/month -- SO, I will be using "Standard" as default***
      - Note: expedited won't work without purchasing provisioned capacity
  - Take note of the **Archive Retrieval Job ID** created
- Wait until this job finishes
  - Will get an email notification from Amazon SNS system when complete (we already set this up)
  - Alternatively can use AWS CLI commands to check when job status is complete:
    - List Jobs: `$ aws glacier list-jobs --account-id - --vault-name a4cis4010` (look for the entry of the noted Job ID)
    - Describe Job: `$ aws glacier describe-job --vault-name a4cis4010 --account-id - --job-id JOBID`
- Get the output of the archive retrieval job, i.e. download/get the archive (file, image, etc.): `"Usage: py downloadArchiveResult.py archive-retrieval-job-id"`
  - New files created for the downloaded archive" a `.bin` and `.jpg` file with filename corresponding to the current date-time stamp
  - View the newfile `.jpg` to see the downloaded image archive
