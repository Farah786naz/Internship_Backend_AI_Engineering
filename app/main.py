from email import message

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from fastapi.exceptions import HTTPException as HttpException

app = FastAPI()

class Authschema(BaseModel):
    email: EmailStr
    password: str

@app.on_event("startup")
async def startup_event():
    print("Server running and connected to Supabase")

@app.get("/")
async def root():
    return {"message": "server running connected with supabase"}

@app.post("/auth/signup", status_code=201)
async def addclient(data: Authschema):
    try:
        from app.supabase_client import supabase
        if not data.email or not data.password:
            return HttpException(status_code=400, detail="Email and password are required")
        
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })
        if response.get("error"):
            return HttpException(status_code=400, detail=response["error"]["message"])
        return {"message": "User signed up successfully", "data": response}
    except Exception as e:
        print(f"Error during signup: {e}")
        return HttpException(status_code=500, detail=str(e))

@app.post("/auth/login", status_code=200)
async def login(data: Authschema):
    try:
        from app.supabase_client import supabase
        if not data.email or not data.password:
            return HttpException(status_code=400, detail="Email and password are required")
        
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        if not response.session:
            return HttpException(status_code=401, detail="Invalid email or password")
        
        session = response.session
        access_token = response.session.access_token    # The JWT token
        refresh_token = response.session.refresh_token  # The Refresh token
        user_id = response.user.id
        
        return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user_id": user_id,
                "message": "User logged in successfully"
            }
        
        
    except Exception as e:
        print(f"Error during login: {e}")
        return HttpException(status_code=500, detail=str(e))