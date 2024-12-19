"""
This module defines API endpoints for managing questions in the QTip application.

Includes:
1. Retrieval of a question by its unique identifier (UUID).
2. Updating a question's AI-assigned topic and relevance in the database.

Schemas:
- `AiResponse`: Defines the structure for updating a question with its AI-assigned topic and relevance.

Endpoints:
- `GET /question/{question_id}`: Fetches a question by its unique identifier.
- `PUT /question/ai-response/{question_id}`: Updates the `topic` and `is_relevant` fields of a question.
"""

from fastapi import APIRouter, HTTPException
from Qtip_fapi.database import database
from pydantic import BaseModel



router = APIRouter()


@router.get("/question/{question_id}")
async def get_question_by_id(question_id: str):
    """
    Fetch a question from the database using its unique identifier (UUID).

    Args:
        question_id (str): The UUID of the question.

    Returns:
        dict: A dictionary containing the question if found.

    Raises:
        HTTPException:
            - 404: If no question is found for the given UUID.
            - 500: If an internal server error occurs.
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
    """
        Schema for updating a question with AI-assigned topic and relevance.

        Attributes:
            topic (str): The AI-assigned topic for the question.
            is_relevant (bool): Whether the question is deemed relevant by the AI.
        """

    topic: str
    is_relevant: bool

@router.put("/question/ai-response/{question_id}")
async def ai_response(payload: AiResponse, question_id: str):
    """
        Update the `topic` and `is_relevant` fields of a question in the database.

        Args:
            payload (AiResponse): The AI response containing the topic and relevance.
            question_id (str): The UUID of the question to update.

        Returns:
            dict: A success message if the update is successful.

        Raises:
            HTTPException:
                - 500: If an internal server error occurs during the update.
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