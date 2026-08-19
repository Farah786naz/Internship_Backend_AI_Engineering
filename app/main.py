from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Server running and connected to Supabase")

@app.get("/")
async def root():
    return {"message": "server running connected with supabase"}