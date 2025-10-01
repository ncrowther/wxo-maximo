#!/usr/bin/env bash
set -x

# orchestrate env activate local
orchestrate env activate remotewxo --api-key azE6dXNyX2EyMjVhMGIyLWJjNTQtMzgxNS05OWIzLTE1ZDdlYTAyNzcyNTovaXlkM3psbURUZFlQQy95ZzJTVitQR0pLeHV0ZW93UGxKWWwyQnoyV0RnPTpXTDBq

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

orchestrate tools import -k python -f ${SCRIPT_DIR}/tools/custom_tools.py

orchestrate knowledge-bases import -f ${SCRIPT_DIR}/knowledge_base/contract_knowledge_base.yaml

orchestrate agents import -f ${SCRIPT_DIR}/agents/wxo-graph-agent.yaml
