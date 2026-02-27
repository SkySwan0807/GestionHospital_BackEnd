
from fastapi import FastAPI, HTTPException, status
from schemas import PostCreate, PostResponse

app = FastAPI()


posts:list[dict] = [
  {
    "id":1,
    "name":"JavaScript",
    "description":"JS is awesome"

  },
  {
    "id":2,
    "name":"Python",
    "description":"build fast APIs with Python"
  }

]

@app.get('/')
def home():
  return "Hello from fastapi"

@app.get("/api/post", response_model=list[PostResponse])
def get_posts():
  return posts

@app.post("/api/post", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
  new_id = max(p["id"] for p in posts) + 1 if posts else 1
  new_post = {
    "id": new_id,
    "author":post.author,
    "type":post.type,
    "description":post.description,
    "status": "accepted",
    "startDate": post.startDate,
    "endDay": post.endDay
  }
  posts.append(new_post)
  return new_post

@app.get("/api/post/{post_id}", response_model=PostResponse)
def get_posts(post_id:int):
  for post in posts:
    if post.get("id") == post_id:
      return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
