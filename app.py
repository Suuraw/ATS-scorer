import uvicorn
from fastapi import FastAPI
from controllers import parser, processing_controller, ats_score

app = FastAPI(
    title="ATS Resume Parser API",
    description="FastAPI backend for resume parsing, job description processing, and ATS score evaluation",
    version="1.0.0"
)

@app.get("/")
def say_hello():
    return {"message": "Hello from ATS Parser API"}

# Register all routers
app.include_router(parser.router, prefix="/api", tags=["Parser"])
app.include_router(processing_controller.router, prefix="/api", tags=["Processing"])
app.include_router(ats_score.router, prefix="/api", tags=["ATS Score"])

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3000, reload=True)
