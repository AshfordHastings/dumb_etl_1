import requests
import sqlalchemy
from sqlalchemy import text

engine = sqlalchemy.create_engine('postgresql://postgres:postgres@localhost:5432/postgres', echo=True)

def get_data():
    res = requests.get("https://randomuser.me/api/?results=1000")
    res = res.json()
    res = res['results']
    return res

def format_data(res):
    data = {}
    location = res['location']
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


def generate_data():
    api_data = get_data()
    data = [{"id": str(i), **format_data(data)} for i, data in enumerate(api_data)]
    print(data[0])
    print(len(data))
    return data

def insert_data(data):
    stmt = """
    INSERT INTO user_info (
        id,
        first_name,
        last_name,
        gender,
        address,
        post_code,
        email,
        username,
        registered_date,
        phone
    ) VALUES (
        :id,
        :first_name,
        :last_name,
        :gender,
        :address,
        :post_code,
        :email,
        :username,
        :registered_date,
        :phone
    );
    """
    with engine.connect() as conn:
        conn.execute(text(stmt), data)
    print("Data inserted successfully!")


if __name__ == "__main__":
    data = generate_data()
    insert_data(data)
