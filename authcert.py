import requests
import json
from time import sleep

while True:
    r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/AccountActivate",
        cert=(".pxgrid-client.crt",".pxgrid-client.key"),
        verify=".demo-ca.cer",
        auth=("pxgrid-client","none"),
        json={}
    )
    r.raise_for_status()
    json_response=r.json()
    print(json.dumps(json_response,indent=2))
    if json_response["accountState"]=="ENABLED":
        print("Account Approved")
        break
    sleep(60)
