import requests
import json

r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/ServiceLookup",
    verify=".demo-ca.cer",
    auth=("pwd-client","07WwV7CXmt8fPmKc"),
    json={
        "name": "com.cisco.ise.config.anc"
    }
)
r.raise_for_status()
service_info=r.json()["services"][0]
node_name=service_info["nodeName"]
rest_url=service_info["properties"]["restBaseUrl"]
r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/AccessSecret",
    verify=".demo-ca.cer",
    auth=("pwd-client","07WwV7CXmt8fPmKc"),
    json={
        "peerNodeName": node_name
    }
)
r.raise_for_status()
secret=r.json()["secret"]
r=requests.post(f"{rest_url}/createPolicy",
    verify=".demo-ca.cer",
    auth=("pwd-client",secret),
    json={
        "name": "Block",
        "actions": ["QUARANTINE"]
    }
)
r.raise_for_status()
print(json.dumps(r.json(),indent=2))