import requests
import json
from time import sleep

pxgrid_node="vb-cl-ise-px1.ciscodemo.net"
username="pwd-client"
rootca_file=".demo-ca.cer"
pxgrid_url=f"https://{pxgrid_node}:8910/pxgrid/control"

r=requests.post(f"{pxgrid_url}/AccountCreate",
    verify=rootca_file,
    json={
        "nodeName": username
    }
)
r.raise_for_status()
password=r.json()["password"]

while True:
    r=requests.post(f"{pxgrid_url}/AccountActivate",
        verify=rootca_file,
        auth=(username,password),
        json={}
    )
    r.raise_for_status()
    json_response=r.json()
    print(json.dumps(json_response,indent=2))
    if json_response["accountState"]=="ENABLED":
        print(f"Account Approved. Password is {password}")
        break
    sleep(60)
