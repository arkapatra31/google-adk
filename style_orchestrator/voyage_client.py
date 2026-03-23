import voyageai
from dotenv import load_dotenv
import os

load_dotenv()

# Create the VoyageAI Client
voyageai_client = voyageai.Client(
    api_key=os.getenv("VOYAGE_API_KEY"),
    max_retries=3,  # max number of retries for the API call
    timeout=30,  # timeout for the API call
)


__all__ = ["voyageai_client"]