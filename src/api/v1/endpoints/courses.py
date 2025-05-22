from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.get("/")
def read_users():
    pass