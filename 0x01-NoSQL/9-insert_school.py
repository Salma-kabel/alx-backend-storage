#!/usr/bin/env python3
"""function that inserts a new document in a collection"""


def insert_school(mongo_collection, **kwargs):
    """ inserts a new document in a collection based on kwargs"""
    new_documents = mongo_collection.insert_one(kwargs)
    return new_documents.inserted_id
