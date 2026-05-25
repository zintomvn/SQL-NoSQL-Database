from fastapi import FastAPI, HTTPException
from .schemas import Post
from app.database import create_db_and_tables, get_async_session, PostModel
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield



app = FastAPI(lifespan=lifespan)

text_posts = {
    "1": {
        "title": "New Post",
        "content": "Cool test post"
    },
    "2": {
        "title": "Learning FastAPI",
        "content": "FastAPI is a modern web framework for building APIs with Python."
    },
    "3": {
        "title": "Python Basics",
        "content": "Python is easy to read and widely used in data science and backend development."
    },
    "4": {
        "title": "Machine Learning Intro",
        "content": "Machine learning allows computers to learn patterns from data."
    },
    "5": {
        "title": "Data Cleaning",
        "content": "Data cleaning is an important step before training machine learning models."
    },
    "6": {
        "title": "Vector Database",
        "content": "A vector database stores embeddings for fast similarity search."
    },
    "7": {
        "title": "Recommendation System",
        "content": "Recommendation systems suggest items based on user behavior and preferences."
    },
    "8": {
        "title": "Fraud Detection",
        "content": "Fraud detection systems help identify suspicious transactions."
    },
    "9": {
        "title": "API Endpoint",
        "content": "An endpoint is a URL path where clients can send requests to an API."
    },
    "10": {
        "title": "Postman Testing",
        "content": "Postman is commonly used to test API requests and responses."
    },
    "11": {
        "title": "Database Design",
        "content": "Good database design helps applications store and retrieve data efficiently."
    },
    "12": {
        "title": "Authentication",
        "content": "Authentication verifies the identity of a user."
    },
    "13": {
        "title": "Authorization",
        "content": "Authorization controls what actions a user is allowed to perform."
    },
    "14": {
        "title": "Docker Introduction",
        "content": "Docker helps package applications and dependencies into containers."
    },
    "15": {
        "title": "Git Version Control",
        "content": "Git is used to track changes in source code during software development."
    },
    "16": {
        "title": "GitHub Portfolio",
        "content": "GitHub can be used to showcase programming projects for employers."
    },
    "17": {
        "title": "EDA Process",
        "content": "Exploratory Data Analysis helps understand patterns, missing values, and distributions."
    },
    "18": {
        "title": "Model Training",
        "content": "Model training is the process of fitting an algorithm to data."
    },
    "19": {
        "title": "Model Evaluation",
        "content": "Model evaluation measures how well a model performs on unseen data."
    },
    "20": {
        "title": "Deployment",
        "content": "Deployment makes an application available for users to access."
    }
}

# @app.get("/posts")
# def get_posts():
#     return text_posts


@app.get("/posts")
def get_list_posts(limit: int):
    if limit: 
        return list(text_posts.values())[:limit]
    return list(text_posts.values())

@app.get("/posts/{post_id}")
def get_post(post_id: str):
    if post_id in text_posts:
        return text_posts[post_id]
    else:
        raise HTTPException(status_code=404, detail="Post not found")

@app.post("/posts")
def create_post(post: Post) -> Post:
    post_id = str(len(text_posts) + 1)
    text_posts[post_id] = post.dict()
    new_post = {"id": post_id, **post.dict()}
    return new_post