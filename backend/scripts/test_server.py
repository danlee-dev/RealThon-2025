#!/usr/bin/env python
"""최소한의 테스트 서버 - FastAPI가 작동하는지 확인"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Server is working!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/test")
async def test(data: dict):
    return {"received": data}

if __name__ == "__main__":
    print("Starting test server on http://0.0.0.0:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
