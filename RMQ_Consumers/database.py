from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.sql import text

DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/qtip"

# Create a synchronous engine
engine = create_engine(DATABASE_URL)
metadata = MetaData()


def db_fetch_files(presentation_id):
    """
    Fetch file paths associated with a specific presentation ID.

    Args:
        presentation_id (str): The ID of the presentation to fetch files for.

    Returns:
        list: A list of file paths.

    Raises:
        Exception: If no files are found for the given presentation ID.
    """
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT path
                FROM knowledge_base
                WHERE presentation_id = :presentation_id
            """)

            # Execute the query and get the result as a mapping of column names to values
            result = conn.execute(query, {"presentation_id": presentation_id}).mappings()
            rows = result.all()

            if not rows:
                raise Exception("No files found for the given presentation ID.")

            # Now you can access columns by their names, e.g., row["filepath"]
            print()
            return [{"filepath": row["path"]} for row in rows]

    except Exception as e:
        return {"error": str(e)}


def db_save_topics(topic, presentation_id):
    """
    Save AI-generated topics into the database.

    Args:
        topic (dict): Dictionary containing topic details (presenter_id, title, summary, open_ai_request_completion_id).
        presentation_id (str): The ID of the presentation to associate with the topic.

    Returns:
        dict: Response message indicating success or error.
    """
    try:
        with engine.begin() as conn:
            query = text("""
                INSERT INTO ai_generated_topics
                (id, presenter_id, presentation_id, title, summary, open_ai_request_completion_id)
                VALUES (
                    :presenter_id,
                    :presentation_id,
                    :title,
                    :summary,
                    :open_ai_request_completion_id
                )
            """)
            conn.execute(query, {
                "presenter_id": topic["presenter_id"],
                "presentation_id": presentation_id,
                "title": topic["title"],
                "summary": topic["summary"],
                "open_ai_request_completion_id": topic["open_ai_request_completion_id"],
            })

            return {"message": "AI-generated topic successfully created."}
    except Exception as e:
        return {"error": str(e)}

def db_fetch_question(question_id: int):
    """
    Fetch a question from the database using its unique identifier (ID).

    Args:
        question_id (int): The ID of the question (bigint unsigned).

    Returns:
        dict: A dictionary containing the question details if found.

    Raises:
        Exception: If no question is found or an error occurs.
    """
    try:
        with engine.connect() as conn:
            # Original query adjusted to use the integer ID
            query = text("""
            SELECT title
            FROM original_questions
            WHERE id = :id
            """)
            # Execute the query with parameters
            result = conn.execute(query, {"id": question_id}).fetchone()

            if not result:
                raise Exception("No Question found for the given Question ID.")

            # Return the fetched question as a dictionary
            return {"question": result[0]}
    except Exception as e:
        raise Exception(f"Database error: {e}")

def db_save_question_detail(topic_id: int, is_relevant: bool, question_id: int):
    """
    Update the `topic_id` and `is_relevant` fields of a question in the database.

    Args:
        topic_id (int): The AI-assigned topic ID for the question.
        is_relevant (bool): Whether the question is deemed relevant by the AI.
        question_id (int): The ID of the question to update.

    Returns:
        dict: A success message if the update is successful.

    Raises:
        Exception: If an error occurs during the update.
    """
    try:
        with engine.begin() as conn:  # Start a transaction and commit automatically
            query = text("""
                UPDATE original_questions
                SET topic_id = :topic_id, is_relevant = :is_relevant, updated_at = NOW()
                WHERE id = :id
            """)

            result = conn.execute(
                query,
                {
                    "topic_id": topic_id,
                    "is_relevant": int(is_relevant),
                    "id": question_id,
                },
            )

            # Check if a row was affected
            if result.rowcount == 0:
                raise Exception(f"No rows updated. Verify that question ID {question_id} exists.")

            return {"message": "AI Response successfully updated in the database"}
    except Exception as e:
        raise Exception(f"Database error: {e}")

