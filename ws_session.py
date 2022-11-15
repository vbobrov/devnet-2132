import requests, websockets, asyncio, ssl
from base64 import b64encode
from asyncio.tasks import FIRST_COMPLETED
from websockets import ConnectionClosed

r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/ServiceLookup",
    cert=(".pxgrid-client.crt",".pxgrid-client.key"),
    verify=".demo-ca.cer",
    auth=("pxgrid-client","none"),
    json={
        "name": "com.cisco.ise.session"
    }
)
r.raise_for_status()
service_info=r.json()["services"][0]
session_topic=service_info["properties"]["sessionTopic"]
pubsub_service=service_info["properties"]["wsPubsubService"]
r=requests.post(f"https://vb-cl-ise-px1.ciscodemo.net:8910/pxgrid/control/ServiceLookup",
    cert=(".pxgrid-client.crt",".pxgrid-client.key"),
    verify=".demo-ca.cer",
    auth=("pxgrid-client","none"),
    json={
        "name": pubsub_service
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

async def futureReadMessage(future):
    global ws
    frame = await ws.recv()
    future.set_result(frame)


async def subscribeLoop():
    global ws_url,secret,node_name,ws
    ssl_context=ssl.create_default_context()
    ssl_context.load_verify_locations(cafile=".demo-ca.cer")
    ws=await websockets.connect(uri=ws_url,
        extra_headers={"Authorization": "Basic "+b64encode((f"pxgrid-client:{secret}").encode()).decode()},
        ssl=ssl_context
    )
    await ws.send(f"CONNECT\naccept-version:1.2\nhost:{node_name}\n\n\x00".encode("utf-8"))
    await ws.send(f"SUBSCRIBE\ndestination:{session_topic}\nid:python\n\n\x00".encode("utf-8"))
    while True:
        future = asyncio.Future()
        futureRead = asyncio.create_task(futureReadMessage(future))
        await asyncio.wait({futureRead},return_when=FIRST_COMPLETED)
        frame = future.result()
        print(f"Received Packet: {frame.decode()}")

loop = asyncio.new_event_loop()
subscribeTask = asyncio.ensure_future(subscribeLoop(),loop=loop)
loop.run_until_complete(subscribeTask)