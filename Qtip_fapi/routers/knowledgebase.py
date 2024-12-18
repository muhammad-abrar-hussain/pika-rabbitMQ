from fastapi import APIRouter, HTTPException
from Qtip_fapi.database import database
from pydantic import BaseModel, UUID4

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




class AiGeneratedTopicCreate(BaseModel):
    presenter_id: UUID4
    presentation_id: UUID4
    title: str
    summary: str
    open_ai_request_completion_id: str

@router.post("/knowledgebase/ai-response")
async def ai_response(topic: AiGeneratedTopicCreate):
    try:
        # Insert query to add data into the database
        # query = """
        #     INSERT INTO QTip_Api_aigeneratedtopic(uuid, presenter_id, presentation_id, title, summary, open_ai_request_completion_id)
        #     VALUES (UUID(), :presenter_id, :presentation_id, :title, :summary, :open_ai_request_completion_id)
        #     """
        query = """
                    INSERT INTO QTip_Api_aigeneratedtopic 
                    (uuid, presenter_id, presentation_id, title, summary, open_ai_request_completion_id)
                    VALUES (
                        REPLACE(UUID(), '-', ''), 
                        REPLACE(:presenter_id, '-', ''), 
                        REPLACE(:presentation_id, '-', ''), 
                        :title, 
                        :summary, 
                        :open_ai_request_completion_id
                    )
                """
        values = {
            "presenter_id": str(topic.presenter_id),
            "presentation_id": str(topic.presentation_id),
            "title": topic.title,
            "summary": topic.summary,
            "open_ai_request_completion_id": topic.open_ai_request_completion_id,
        }
        await database.execute(query=query, values=values)

        return {"message": "AI-generated topic successfully created."}

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to create AI-generated topic.")
