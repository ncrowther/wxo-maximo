## WXO Maximo Demo

This repo contains a WXO asset to create python graphs for Mamimo demos.
It requires the following:

- A tool to generate Python queries on Maximo data (represented as CSV)
- An agent to invoke the tools and display the results

This code is based on the exellent work done by Lissan.  The original repo is here:

https://github.ibm.com/lissan-koirala/wxo-graph-demo/assets/516305/8d20d3e7-a646-422f-9236-0cf0908c01b6


# Installation 

### Project Structure

- `tools/` - watsonx orchestrate tools folder
- `agents/` - watsonx orchestrate agent folder 

### Prerequisites
- Python 3.13 or higher
- pip or uv package manager


## Deploy the WXO agent using the ADK 

If you have not done so already, setup the WXO ADK: 
https://developer.watson-orchestrate.ibm.com/getting_started/installing


   ```bash
   # Setup the virtual env for the tools
   pip install -r tools/requirements.txt
   ```

   ```bash
   # Get your WXO api key from WXO top right menu: user->settings->API detals->Generate API Key
   orchestrate env activate remotewxo --api-key azE6dXNyX2EyMjVhMGIyLWJjNTQtMzgxNS05OWIzLTE1ZDdlYTAyNzcyNTovaXlkM3psbURUZFlQQy95ZzJTVitQR0pLeHV0ZW93UGxKWWwyQnoyV0RnPTpXTDBq
   ```

   ```bash
   # Update tools
   orchestrate tools import -k python -f tools/custom_tools.py -r tools/requirements.txt
   ```

   ```bash
   # Update agent
   orchestrate agents import -f agents/wxo-graph-agent.yaml
   ```

### Set Image server URL

The image server is used to display charts in WXO.  To run the  image server locally download the repo:
https://github.com/ncrowther/wxo-image-server

1. Run the wxo-image-server

2. Use VSC to expose the port (8000) as public

3. Change the constant HOST_URL in ```api/main.py``` to the forwarded host address

4. Change the constant FILE_SERVER_UPLOAD in ```tools/custom_tools.py``` to the forwared host address   

## Example conversation flow with data agent

This document contains legal information on temporary repairs carried out by contractors

show pending work orders 

show number of days these work orders are breached

show this as a bar chart

Change the color according to the sla

calculate cost of WO6234 if the cost of one day breach is £100

calculate the cost of WO4534 if the cost of one hour breach is £50

## Example conversation flow with contract agent

Our maintenance contatctor has had to make a temporary fix.   How long do they have to make the fix permanent?

## More examples

show a pie chart of all work orders by status

show breached work orders with the number of days breached.  Calculate breaches by calculating the number of days between the actual fix date and target fix date

show this as a bar chart

what is the sla penalty for S3

calculate sla penalty for work order WO6322

show a bar chart with work order on the x axis and days to fix on the y axis. Label the y axis DAYS

show a chart with work order on the x axis and actual fix date and target fix date on the y axis. Label the y axis DAYS

show a chart with breached work order on the x axis and breached days on the y axis. Label the y axis "days". show breaches as positive numbers. set the title to "Breaches"

Our maintenance contractor has to make a temporary repair, according to the contract how long do they have to make the fix permanent?

set the permanent repair deadline for work order id WO4567 to 2025-10-31 00:00:00

set the actual fix date work order id WO6322 to 2025-10-31 00:00:00 and its status to COMPLETED

## Optional webchat
- Run `orchestrate channels webchat embed --agent-name=AGENT_NAME` and copy that to file `server-side/main.py` under the `chat_agent` function to get the embed webchat into the website.


## Contact

Please reach out to <ncrowther@uk.ibm.com> with any questions or issues.


