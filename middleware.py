from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.supabase_client import supabase

app = FastAPI()
security = HTTPBearer()

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required"
        )
    
    token = credentials.credentials.strip()
    
    try:
        # Call Supabase to fetch the user
        user_response = supabase.auth.get_user(token)
        
        # Ensure user object exists
        user = getattr(user_response, "user", None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
            
        return {
            "user": user,
            "token": token
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"\n--- AUTH FAILURE LOG ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print("-------------------------\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, malformed, or expired access token"
        )