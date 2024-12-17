from fastapi import APIRouter, HTTPException
from Qtip_ai.database import database

router = APIRouter(prefix="/knowledgebase", tags=["Knowledge Base"])

@router.get("/{presentation_id}")
async def get_files_by_presentation(presentation_id: int):
    query = """
    SELECT * FROM QTip_Api_presentationknowledgebase 
    WHERE presentation = :presentation_id
    """
    rows = await database.fetch_all(query, {"presentation_id": presentation_id})
    if not rows:
        raise HTTPException(status_code=404, detail="No files found for the given presentation ID")
    return rows
