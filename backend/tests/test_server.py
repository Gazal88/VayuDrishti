"""
Standalone test server for the /advisory endpoint.

Person 3 uses this to test the endpoint independently before
Person 1 integrates it into the main app.

Usage:
    1. Copy .env.example → .env and add your API key
    2. pip install -r requirements_role3.txt
    3. python test_server.py
    4. Open http://localhost:8001/docs to test via Swagger UI

Person 1 integration:
    In your main FastAPI app, just add:
        from advisory_engine import advisory_router
        app.include_router(advisory_router)
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from advisory_engine import advisory_router

app = FastAPI(
    title="VayuDrishti — Advisory Engine (Role 3 Test Server)",
    description=(
        "Standalone server for testing the AI advisory endpoint. "
        "Person 1 will integrate this router into the main backend."
    ),
    version="1.0.0",
)

# Allow frontend (Person 4) to call during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the advisory router
app.include_router(advisory_router)


@app.get("/")
async def root():
    return {
        "service": "VayuDrishti Advisory Engine",
        "role": "Role 3 — AI Explanation Lead",
        "endpoint": "POST /advisory",
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
