from minio import Minio


def init_minio():
    client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadminsecret",
        secure=False
    )

    bucket_name = "track-streams"

    found = client.bucket_exists(bucket_name)

    if not found:
        client.make_bucket(bucket_name)
        print(f"Bucket {bucket_name} created successfully!")
    else:
        print(f"Bucket {bucket_name} already exists!")

if __name__ == "__main__":
    init_minio()
    print("Minio setup completed!")