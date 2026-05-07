import ujson
from umqtt.simple import MQTTClient


def connect_mqtt(broker_ip, response_topic, callback, client_id, port=21883):
    client = MQTTClient(client_id=client_id, server=broker_ip, port=port)
    client.set_callback(callback)
    client.connect(clean_session=True)
    client.subscribe(response_topic)
    print("Connected to MQTT broker")
    print("Subscribed to topic:", response_topic)
    return client


def send_mqtt_message(client, topic, message):
    try:
        client.publish(topic, message)
        print("Sent to MQTT:", topic)
        return True
    except Exception as e:
        print("Failed to send MQTT message:", e)
        return False


def parse_json_message(msg):
    return ujson.loads(msg)
