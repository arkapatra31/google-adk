from dotenv import load_dotenv
from style_orchestrator.voyage_client import voyageai_client
from bson import Binary
import certifi
import PIL
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection

load_dotenv()

DESCRIPTIONS = [
    "This is a sports shoes",
    "This is a formal shoe",
    "This is a casual T shirt",
    "This is business T shirt",
    "This is traditional wear called Sherwani",
]

IMAGE_FILES = [
    "sports_shoe.png",
    "formal_shoe.png",
    "casual_tee.png",
    "business_tee.png",
    "sherwani.png",
]


def embed_images(image_folder: str):
    try:
        inputs = [
            [desc, PIL.Image.open(os.path.join(image_folder, img))]
            for desc, img in zip(DESCRIPTIONS, IMAGE_FILES)
        ]

        result = voyageai_client.multimodal_embed(
            inputs,
            model=os.getenv("VOYAGE_MULTI_MODAL_MODEL"),
        )

        mongo_client = MongoClient(
            os.getenv("MONGO_CONNECTION_STRING"),
            server_api=ServerApi("1"),
            tlsCAFile=certifi.where(),
        )
        db = mongo_client.get_database(os.getenv("MONGO_DATABASE_NAME"))
        collection: Collection = db[os.getenv("MONGO_COLLECTION_NAME")]

        documents = []
        for desc, img, emb in zip(DESCRIPTIONS, IMAGE_FILES, result.embeddings):
            img_path = os.path.join(image_folder, img)
            with open(img_path, "rb") as f:
                image_data = Binary(f.read())
            documents.append({
                "desc": desc,
                "image": image_data,
                "image_name": img,
                "embedding": emb,
            })
        collection.insert_many(documents)
        print(f"Inserted {len(documents)} embeddings successfully")
        return result.embeddings
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None


if __name__ == "__main__":
    try:
        embed_images(image_folder="style_orchestrator/images")
    except Exception as e:
        print(f"Error: {e}")
        raise e
