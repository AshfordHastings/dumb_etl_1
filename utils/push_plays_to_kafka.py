
import pandas as pd
import json
import uuid 
import time
from kafka import KafkaProducer

spotify_df = None
users_df = None

def init_song_data():
    df = pd.read_csv("../data/spotify-2023.csv", encoding='latin-1')
    df = df.sort_values(by='streams', ascending=False)
    df = df[0:1000]
    df= df.rename(columns={"artist(s)_name": "artist_name"})
    df = df.loc[:, ['track_name', 'artist_name', 'streams']]

    global spotify_df
    spotify_df = df

def get_random_song():
    if spotify_df is None:
        init_song_data()

    return spotify_df.sample(1)

def get_random_user():
    global users_df
    if users_df is None:
        users = [{"id": i } for i, _ in enumerate(range(1000))]
        users_df = pd.DataFrame(users)
    
    return users_df.sample(1)
    
def format_data(song, user):
    return {
        'id': str(uuid.uuid4()),
        "user_id": str(user['id'].values[0]),
        "track_id": str(song.index[0]),
        "track_name": song['track_name'].values[0],
        "artist_name": song['artist_name'].values[0],
        "timestamp": int(time.time() * 1000)  # Current time in milliseconds
    }

def send_to_kafka(topic, data):
    producer = KafkaProducer(bootstrap_servers=['localhost:29092'],
                             value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    producer.send(topic, key=data['id'].encode('utf-8'), value=data)
    producer.flush()
    print(f"Published record with id of {data['id']} to topic {topic}")

def stream_data_to_kafka():
    while True:
        song = get_random_song()
        user = get_random_user()

        data = format_data(song, user)
        print(f"SENDING DATA: \n{data}")

        send_to_kafka('track-events', data)


if __name__ == "__main__":
    stream_data_to_kafka()