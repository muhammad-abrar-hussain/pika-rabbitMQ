from fastapi import APIRouter, HTTPException
from Qtip_fapi.database import database
from pydantic import BaseModel



router = APIRouter()


@router.get("/question/{question_id}")
async def get_question_by_id(question_id: str):
    """
    Fetch a question from the database using its primary key (uuid).
    """
    try:
        query = """
        SELECT 
             question
        FROM 
            QTip_Api_presentationoriginalquestions 
        WHERE 
            uuid = REPLACE(:uuid, '-', '')
        """
        row = await database.fetch_one(query, {"uuid": question_id})

        if not row:
            raise HTTPException(status_code=404, detail="No Question found for the given Question ID.")
        return row

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


class AiResponse(BaseModel):
    topic: str
    is_relevant: bool

@router.put("/question/ai-response/{question_id}")
async def ai_response(payload: AiResponse, question_id: str):
    """
    Updates the `topic` and `is_relevant` fields in the `QTip_Api_presentationoriginalquestions` table.
    """
    try:
        query = """
            UPDATE QTip_Api_presentationoriginalquestions
            SET topic = :topic, is_relevant = :is_relevant
            WHERE uuid = REPLACE(:question_id, '-', '')
        """
        values = {
            "topic": payload.topic,
            "is_relevant": 1 if payload.is_relevant else 0,
            "question_id": question_id,
        }

        await database.execute(query=query, values=values)

        return {"message": "AI Response successfully updated in the database"}

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to update data in the database.")