from fastapi import FastAPI

app = FastAPI(title="User Service")

@app.get("/")
def read_root():
    return {"message": "Welcome to the User Service"}
