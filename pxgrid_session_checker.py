import requests
import websocket
import ssl
import signal
import logging
from base64 import b64encode

def handler(signum, frame):
    print("Timed out!")
    raise Exception("Timeout")

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)-8s %(message)s')
pxgrid_nodes=["vb-cl-ise-px1.ciscodemo.net","vb-cl-ise-px2.ciscodemo.net"]
username="pwd-client"
password="07WwV7CXmt8fPmKc"
rootca_file=".demo-ca.cer"
for pxgrid_node in pxgrid_nodes:
    logging.info(f"Checking {pxgrid_node}")
    pxgrid_url=f"https://{pxgrid_node}:8910/pxgrid/control"
    logging.info("ServiceLookup for com.cisco.ise.session")
    try:
        r=requests.post(f"{pxgrid_url}/ServiceLookup",
            verify=rootca_file,
            auth=(username,password),
            json={
                "name": "com.cisco.ise.session"
            }
        )
        r.raise_for_status()
        service_info=r.json()["services"][0]
        session_topic=service_info["properties"]["sessionTopic"]
        pubsub_service=service_info["properties"]["wsPubsubService"]
        rest_url=service_info["properties"]["restBaseUrl"]
        node_name=service_info["nodeName"]
        logging.info("Success")
    except Exception as e:
        logging.error(f"Error occured: {e}")
        continue
    logging.info("AccessSecret for node_name")
    try:
        r=requests.post(f"{pxgrid_url}/AccessSecret",
            verify=rootca_file,
            auth=(username,password),
            json={
                "peerNodeName": node_name
            }
        )
        r.raise_for_status()
        secret=r.json()["secret"]
        logging.info("Success")
    except Exception as e:
        logging.error(f"Error occured: {e}")
        continue

    logging.info("getSessionByIpAddress for 10.20.30.40")
    try:
        r=requests.post(f"{rest_url}/getSessionByIpAddress",
            verify=rootca_file,
            auth=(username,secret),
            json={
                "ipAddress": "10.20.30.40"
            }
        )
        r.raise_for_status()
        logging.info("Success")
    except:
        logging.error(f"Error occured: {e}")
        continue
    logging.info(f"ServiceLookup for {pubsub_service}")
    try:
        r=requests.post(f"{pxgrid_url}/ServiceLookup",
            verify=rootca_file,
            auth=(username,password),
            json={
                "name": pubsub_service
            }
        )
        r.raise_for_status()
        service_info=r.json()["services"][0]
        node_name=service_info["nodeName"]
        ws_url=service_info["properties"]["wsUrl"]
        logging.info("Success")
    except:
        logging.error(f"Error occured: {e}")
        continue
    logging.info(f"AccessSecret for {node_name}")
    try:
        r=requests.post(f"{pxgrid_url}/AccessSecret",
            verify=rootca_file,
            auth=(username,password),
            json={
                "peerNodeName": node_name
            }
        )
        r.raise_for_status()
        secret=r.json()["secret"]
        logging.info("Success")
    except:
        logging.error(f"Error occured: {e}")
        continue

    logging.info(f"Connecting websocket to {ws_url}")
    ssl_context=ssl.create_default_context()
    ssl_context.load_verify_locations(cafile=rootca_file)

    try:
        ws=websocket.create_connection(ws_url,
            sslopt={"context": ssl_context},
            header={"Authorization": "Basic "+b64encode((f"{username}:{secret}").encode()).decode()}
        )
        logging.info("Success")
    except:
        logging.error(f"Error occured: {e}")
        continue    
    logging.info(f"Sending CONNECT {node_name} and SUBSCRIBE {session_topic}")
    try:
        ws.send(f"CONNECT\naccept-version:1.2\nhost:{node_name}\n\n\x00",websocket.ABNF.OPCODE_BINARY)
        ws.send(f"SUBSCRIBE\ndestination:{session_topic}\nid:python\n\n\x00",websocket.ABNF.OPCODE_BINARY)
    except:
        logging.error(f"Error occured: {e}")
        continue    

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(60)
    logging.info("Waiting 60 seconds to receive 5 sessions")
    for i in range(5):
        try:
            msg=ws.recv()
            logging.debug(msg.decode())
        except:
            logging.error("Failed to receive sessions")
            break

    ws.close()
    signal.alarm(0)
