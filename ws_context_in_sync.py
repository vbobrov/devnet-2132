import requests, websocket, ssl, json
from base64 import b64encode

r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/ServiceRegister",
    cert=(".pxgrid-client.crt",".pxgrid-client.key"),
    verify=".demo-ca.cer",
    auth=("pxgrid-client","none"),
    json={
        "name": "com.cisco.endpoint.asset",
        "properties": {
            "wsPubsubService": "com.cisco.ise.pubsub",
            "assetTopic":"/topic/com.cisco.endpoint.asset"
        }
    }
)
r.raise_for_status()
r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/ServiceLookup",
    cert=(".pxgrid-client.crt",".pxgrid-client.key"),
    verify=".demo-ca.cer",
    auth=("pxgrid-client","none"),
    json={
        "name": "com.cisco.ise.pubsub"
    }
)
r.raise_for_status()
service_info=r.json()["services"][0]
node_name=service_info["nodeName"]
ws_url=service_info["properties"]["wsUrl"]
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
ssl_context=ssl.create_default_context()
ssl_context.load_verify_locations(cafile=".demo-ca.cer")
ws=websocket.create_connection(ws_url, #"ws://websocket-echo.com",
    sslopt={"context": ssl_context},
    header={"Authorization": "Basic "+b64encode((f"pxgrid-client:{secret}").encode()).decode()}
)
with open("endpoint.json","r") as f:
    endpoint=json.dumps(json.loads(f.read()))
ws.send(f"CONNECT\naccept-version:1.2\nhost:{node_name}\n\n\x00",websocket.ABNF.OPCODE_BINARY)
ws.send(f"SEND\ndestination:/topic/com.cisco.endpoint.asset\ncontent-length:{len(endpoint)}\n\n{endpoint}\x00".encode("utf-8"),websocket.ABNF.OPCODE_BINARY)
ws.close()