import requests
import json
from time import sleep
r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/AccountCreate",
    cert=(".pxgrid-client.crt",".pxgrid-client.key"),
    verify=".demo-ca.cer",
    json={
        "nodeName": "pwd-client"
    }
)
r.raise_for_status()
password=r.json()["password"]

while True:
    r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/AccountActivate",
        verify=".demo-ca.cer",
        auth=("pwd-client",password),
        json={}
    )
    r.raise_for_status()
    json_response=r.json()
    print(json.dumps(json_response,indent=2))
    if json_response["accountState"]=="ENABLED":
        print(f"Account Approved. Password is {password}")
        break
    sleep(60)
