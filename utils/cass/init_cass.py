from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


def create_keyspace(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS track_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)

    print("Keyspace created successfully!")

def create_table(session):
    session.execute("""
    CREATE TABLE IF NOT EXISTS track_streams.track_events (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        track_id TEXT,
        track_name TEXT,
        artist_name TEXT);
    """)

    print("Table created successfully!")

def create_enriched_track_events_table(session):
    session.execute("""
    CREATE TABLE IF NOT EXISTS track_streams.enriched_track_events (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        track_id TEXT,
        track_name TEXT,
        artist_name TEXT,
        first_name TEXT,
        last_name TEXT,
        gender TEXT,
        address TEXT,
        post_code TEXT,
        email TEXT,
        username TEXT,
        registered_date TEXT,
        phone TEXT);
    """)

    print("Table created successfully!")

def create_metrics_table(session):
    session.execute("""
    CREATE TABLE IF NOT EXISTS track_streams.user_metrics (
        user_id TEXT PRIMARY KEY,
        track_events_count INT);
    """)

    print("Table created successfully!")

if __name__ == "__main__":
    #auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
    cluster = Cluster(['localhost'], port=9042) # Running from outside of docker, use localhost
    session = cluster.connect()

    create_keyspace(session)
    session.set_keyspace('track_streams')

    #create_table(session)
    create_metrics_table(session)

    cluster.shutdown()
    print("Cassandra setup completed!")