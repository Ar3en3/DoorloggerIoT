from google.cloud import storage

def list_buckets():
    client = storage.Client()
    buckets = list(client.list_buckets())
    print("Buckets:")
    for bucket in buckets:
        print(bucket.name)

if __name__ == "__main__":
    list_buckets()

