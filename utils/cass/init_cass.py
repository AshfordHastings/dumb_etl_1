from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


def create_keyspace(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS user_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)

    print("Keyspace created successfully!")

def create_table(session):
    session.execute("""
    CREATE TABLE IF NOT EXISTS user_streams.users (
        id TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT);
    """)

    print("Table created successfully!")


if __name__ == "__main__":
    #auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
    cluster = Cluster(['localhost'], port=9042) # Running from outside of docker, use localhost
    session = cluster.connect()

    create_keyspace(session)
    session.set_keyspace('user_streams')

    create_table(session)

    cluster.shutdown()
    print("Cassandra setup completed!")