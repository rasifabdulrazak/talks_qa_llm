from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from .deps import get_db
from app.core import security
from app.core.config import settings
from app.schema.user import UserCreate, User, Token,LoginRequest
from app.models.user import User as UserModel

router = APIRouter()

@router.post("/register/", response_model=User, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    try:
        check_email = user_in.email.strip().lower()
        user = db.query(UserModel).filter(UserModel.email == check_email).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists"
            )
        
        hashed_password = security.get_password_hash(user_in.password) 
        db_user = UserModel(
            email=check_email,
            name=user_in.name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )
        
        
        

@router.post("/login/", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Validate login and provide tokens
    """
    try:
        user = db.query(UserModel).filter(UserModel.email == request.email).first()
        
        if not user or not security.verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User with this credential doesnot exist",
            )
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
        access_token = security.create_access_token(
            user_id=user.id, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )
        
        
@router.post("/logout/")
def logout(request: Request):
    """
    Blacklist token and logout
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Missing or invalid Authorization header"
                )

        token = auth_header.split(" ")[1]
        security.blacklist_token(token,3600)
        return {"message": "Successfully logged out. Token has been blacklisted."}
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )