from fastapi import FastAPI
from app.db import get_db_connection

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/hello")
def say_hello():
    return {"message": "Hello world !!"}

@app.get("/db")
def test_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    result = cur.fetchone()
    conn.close()
    return {"db": result[0]}
