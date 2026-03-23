from __future__ import annotations

import base64
import os

import certifi
from dotenv import load_dotenv
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from style_orchestrator.voyage_client import voyageai_client

load_dotenv()

_pending_images: list[dict] = []


def suggest_image(query: str, num_results: int = 3) -> list[dict]:
    """Suggest images based on a text query using vector search."""
    global _pending_images

    query_embedding = voyageai_client.multimodal_embed(
        inputs=[[query]],
        model=os.getenv("VOYAGE_MULTI_MODAL_MODEL"),
    ).embeddings[0]

    mongo_client = MongoClient(
        os.getenv("MONGO_CONNECTION_STRING"),
        server_api=ServerApi("1"),
        tlsCAFile=certifi.where(),
    )
    db = mongo_client.get_database(os.getenv("MONGO_DATABASE_NAME"))
    collection: Collection = db[os.getenv("MONGO_COLLECTION_NAME")]

    pipeline = [
        {
            "$vectorSearch": {
                "index": "image_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": num_results * 10,
                "limit": num_results,
            }
        },
        {
            "$project": {
                "_id": 0,
                "desc": 1,
                "image": 1,
                "image_name": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    results = list(collection.aggregate(pipeline))

    _pending_images = []
    text_results = []
    for result in results:
        text_results.append({
            "desc": result.get("desc", ""),
            "image_name": result.get("image_name", ""),
            "score": result.get("score", 0),
        })
        if result.get("image"):
            _pending_images.append({
                "data": base64.b64encode(result["image"]).decode("utf-8"),
                "mime_type": "image/png",
                "name": result.get("image_name", "image"),
                "desc": result.get("desc", ""),
            })

    return text_results


def take_pending_images() -> list[dict]:
    """Retrieve and clear the pending images from the last suggest_image call."""
    global _pending_images
    images = _pending_images
    _pending_images = []
    return images


__all__ = ["suggest_image", "take_pending_images"]

if __name__ == "__main__":
    query = "I need a office shoe"
    print(f"Query: '{query}'\n")
    results = suggest_image(query)
    for rank, result in enumerate(results, 1):
        print(f"{rank}. {result['desc']} ({result.get('image_name')})")
        print(f"   Score: {result['score']:.4f}\n")
    if not results:
        print("No results returned from $vectorSearch")
