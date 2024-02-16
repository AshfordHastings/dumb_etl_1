import json
import uuid
import requests
from kafka import KafkaProducer

def get_data():
    res = requests.get("https://randomuser.me/api/")
    res = res.json()
    res = res['results'][0]
    return res

def format_data(res):
    data = {}
    location = res['location']
    data['id'] = str(uuid.uuid4())
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['address'] = f"{str(location['street']['number'])} {location['street']['name']}, " \
                      f"{location['city']}, {location['state']}, {location['country']}"
    data['post_code'] = str(location['postcode'])
    data['email'] = res['email']
    data['username'] = res['login']['username']
    #data['dob'] = res['dob']['date']
    data['registered_date'] = res['registered']['date']
    data['phone'] = res['phone']
    data['picture'] = res['picture']['medium']
    return data

def send_to_kafka(topic, data):
    producer = KafkaProducer(bootstrap_servers=['localhost:29092'],
                             value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    producer.send(topic, key=data['id'].encode('utf-8'), value=data)
    producer.flush()

if __name__ == "__main__":
    topic = 'users1'
    while True:
        raw_data = get_data()
        formatted_data = format_data(raw_data)
        print(f"Sending data: {formatted_data}")
        send_to_kafka(topic, formatted_data)

