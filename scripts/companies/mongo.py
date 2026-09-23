from pymongo import MongoClient
from pprint import pprint

from config import (
    MONGO_HOST,
    MONGO_PORT,
    MONGO_USER,
    MONGO_PASSWORD,
    MONGO_DB,
)


def get_top_companies():

    client = MongoClient(
        host=MONGO_HOST,
        port=MONGO_PORT,
        username=MONGO_USER,
        password=MONGO_PASSWORD,
        authSource=MONGO_DB,
    )

    collection = client[MONGO_DB]["offers"]

    pipeline = [
        {
            "$match": {
                "locationDepartment": "34",
                "company": {
                    "$type": "string",
                    "$ne": "",
                },
            }
        },

        {
            "$group": {
                "_id": {
                    "$toLower": {
                        "$trim": {
                            "input": "$company"
                        }
                    }
                },
                "name": {
                    "$first": "$company"
                },
                "offer_count": {
                    "$sum": 1
                },
            }
        },

        {
            "$sort": {
                "offer_count": -1
            }
        },

        {
            "$limit": 25
        },
    ]

    companies = list(
        collection.aggregate(pipeline)
    )

    client.close()

    return companies

if __name__ == "__main__":
    companies = get_top_companies()
    pprint(companies)