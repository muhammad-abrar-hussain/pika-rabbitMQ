from fastapi import APIRouter, HTTPException
from Qtip_fapi.database import database
router = APIRouter()

@router.get("/knowledgebase/{presentation_id}")
async def get_files_by_presentation(presentation_id: str):
    try:
        query = """
        SELECT filepath 
        FROM QTip_Api_presentationknowledgebase 
        WHERE presentation_id = :presentation_id
        """
        rows = await database.fetch_all(query, {"presentation_id": presentation_id})
        if not rows:
            raise HTTPException(status_code=404, detail="No files found for the given presentation ID.")

        files = [dict(row) for row in rows]
        return {"files": files}

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
