#!/usr/bin/env python3
"""Improve 12-log_stats.py by adding the top 10 of
the most present IPs in the collection"""


from pymongo import MongoClient


def log():
    """adding the top 10 of the most present IPs
    in the collection nginx of the database logs"""
    client = MongoClient('mongodb://127.0.0.1:27017')
    collection = client.logs.nginx
    total = collection.count_documents({})
    get = collection.count_documents({"method": "GET"})
    post = collection.count_documents({"method": "POST"})
    put = collection.count_documents({"method": "PUT"})
    patch = collection.count_documents({"method": "PATCH"})
    delete = collection.count_documents({"method": "DELETE"})
    path = collection.count_documents(
        {"method": "GET", "path": "/status"})
    print(f"{total} logs")
    print("Methods:")
    print(f"\tmethod GET: {get}")
    print(f"\tmethod POST: {post}")
    print(f"\tmethod PUT: {put}")
    print(f"\tmethod PATCH: {patch}")
    print(f"\tmethod DELETE: {delete}")
    print(f"{path} status check")
    print("IPs:")
    ips = collection.aggregate(
        [{"$group": {"_id": "$ip", "count": {"$sum": 1}}},
         {"$sort": {"count": -1}}])
    ip = 0
    for i in ips:
        if ip == 10:
            break
        print(f"\t{s.get('_id')}: {s.get('count')}")
        ip += 1


if __name__ == "__main__":
    log()
