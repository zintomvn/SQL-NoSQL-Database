from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct 
from sentence_transformers import SentenceTransformer

client = QdrantClient(host="localhost", port=6333)

client = QdrantClient(
    url="http://localhost:6333"
)

model = SentenceTransformer('all-MiniLM-L6-v2')

documents = [
    {
        "id": 1,
        "text": "Qdrant is a vector database for similarity search.",
        "source": "note_1"
    },
    {
        "id": 2,
        "text": "CLIP can embed images and text into the same vector space.",
        "source": "note_2"
    },
    {
        "id": 3,
        "text": "FastAPI is often used to build backend APIs in Python.",
        "source": "note_3"
    }
]

texts = [doc["text"] for doc in documents]
vectors = model.encode(texts).tolist()

for text, vector in zip(texts, vectors):
    print(f"Text: {text}\nVector: {vector}\n")
    print("-" * 80)

collection_name = 'text_docs'

client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE)
)

# Prepare points to be inserted into Qdrant
# points = []

# for doc, vector in zip(documents, vectors):
#     points.append(PointStruct(id=doc["id"], vector=vector, payload={"source": doc["source"]}))


# client.upsert(
#     collection_name=collection_name,
#     points=points
# )
