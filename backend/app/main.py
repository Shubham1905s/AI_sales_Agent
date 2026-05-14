from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.leads import router as leads_router

app = FastAPI(title="LeadGen AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
