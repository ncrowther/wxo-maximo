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


## Optional webchat
- Run `orchestrate channels webchat embed --agent-name=AGENT_NAME` and copy that to file `server-side/main.py` under the `chat_agent` function to get the embed webchat into the website.


## Contact

Please reach out to <ncrowther@uk.ibm.com> with any questions or issues.
