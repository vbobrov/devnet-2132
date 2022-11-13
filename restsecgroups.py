import requests
import json

r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/ServiceLookup",
    cert=(".pxgrid-client.crt",".pxgrid-client.key"),
    verify=".demo-ca.cer",
    auth=("pxgrid-client","none"),
    json={
        "name": "com.cisco.ise.config.trustsec"
    }
)
r.raise_for_status()
service_info=r.json()["services"][0]
node_name=service_info["nodeName"]
rest_url=service_info["properties"]["restBaseUrl"]
r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/AccessSecret",
    cert=(".pxgrid-client.crt",".pxgrid-client.key"),
    verify=".demo-ca.cer",
    auth=("pxgrid-client","none"),
    json={
        "peerNodeName": node_name
    }
)
r.raise_for_status()
secret=r.json()["secret"]
r=requests.post(f"{rest_url}/getSecurityGroups",
    verify=".demo-ca.cer",
    auth=("pxgrid-client",secret),
    json={}
)
r.raise_for_status()
print(json.dumps(r.json(),indent=2))