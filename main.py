from fastapi import FastAPI

app = FastAPI(title="No-AI REST Service")


@app.get("/health")
def health_check():
    return {"status": "healthy"}