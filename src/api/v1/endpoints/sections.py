from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/sections", tags=["sections"])

@router.get("/")
def get_sections():
    pass

@router.get("/{section_id}")
def get_section_by_id(section_id):
    pass

@router.post("/")
def add_section():
    pass

@router.delete("/")
def delete_section():
    pass

@router.put("/{section_id}")
def update_section():
    pass
