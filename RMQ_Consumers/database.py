from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import text
from datetime import datetime

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
    Save AI-generated topics into the database with timestamps.

    Args:
        topic (dict): Dictionary containing topic details (title, summary, request_completion_id).
        presentation_id (str): The ID of the presentation to associate with the topic.

    Returns:
        dict: Response message indicating success or error.
    """
    try:
        # Get the current time for created_at and updated_at
        current_time = datetime.utcnow()  # Use UTC for consistency

        # Fetch the presenter_id from the presentations table based on the presentation_id
        with engine.begin() as conn:
            query = text("""
                SELECT presenter_id
                FROM presentations
                WHERE id = :presentation_id
            """)
            result = conn.execute(query, {"presentation_id": presentation_id}).fetchone()

            # Check if the presenter_id was found
            if result is None:
                return {"error": f"No presenter found for presentation_id: {presentation_id}"}
            presenter_id = result["presenter_id"]

            # Insert the topic into ai_generated_topics table
            insert_query = text("""
                INSERT INTO ai_generated_topics
                (presenter_id, presentation_id, title, summary, request_completion_id, created_at, updated_at)
                VALUES (
                    :presenter_id,
                    :presentation_id,
                    :title,
                    :summary,
                    :request_completion_id,
                    :created_at,
                    :updated_at
                )
            """)
            conn.execute(insert_query, {
                "presenter_id": presenter_id,
                "presentation_id": presentation_id,
                "title": topic["title"],
                "summary": topic["summary"],
                "request_completion_id": topic["request_completion_id"],
                "created_at": current_time,
                "updated_at": current_time,
            })

            return {"message": "AI-generated topic successfully created."}
    except Exception as e:
        return {"error": str(e)}


def db_save_topics(topic, presentation_id):
    """
    Save AI-generated topics into the database with timestamps.

    Args:
        topic (dict): Dictionary containing topic details (title, summary, request_completion_id).
        presentation_id (str): The ID of the presentation to associate with the topic.

    Returns:
        dict: Response message indicating success or error.
    """
    try:

        current_time = datetime.utcnow()

        with engine.begin() as conn:
            query = text("""
                SELECT presenter_id
                FROM presentations
                WHERE id = :presentation_id
            """)
            result = conn.execute(query, {"presentation_id": presentation_id}).fetchone()

            if result is None:
                return {"error": f"No presenter found for presentation_id: {presentation_id}"}
            presenter_id = result[0]

            insert_query = text("""
                INSERT INTO ai_generated_topics
                (presenter_id, presentation_id, title, summary, request_completion_id, created_at, updated_at)
                VALUES (
                    :presenter_id,
                    :presentation_id,
                    :title,
                    :summary,
                    :request_completion_id,
                    :created_at,
                    :updated_at
                )
            """)
            conn.execute(insert_query, {
                "presenter_id": presenter_id,
                "presentation_id": presentation_id,
                "title": topic["title"],
                "summary": topic["summary"],
                "request_completion_id": topic["request_completion_id"],
                "created_at": current_time,
                "updated_at": current_time,
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

            return result[0]
    except Exception as e:
        raise Exception(f"Database error: {e}")

def db_save_question_detail(topic_id: int = None, is_relevant: bool = False, question_id: int = None):
    """
    Update the `topic_id` and `is_relevant` fields of a question in the database.
    If `topic_id` is not provided, it will use the default value from the database.

    Args:
        topic_id (int, optional): The AI-assigned topic ID for the question. Defaults to None.
        is_relevant (bool): Whether the question is deemed relevant by the AI.
        question_id (int): The ID of the question to update.

    Returns:
        dict: A success message if the update is successful.

    Raises:
        Exception: If an error occurs during the update.
    """
    try:
        # Default value for topic_id if not provided
        if topic_id is None:
            topic_id = 0  # Replace with the default value from your database, if needed

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


def get_topics_with_summary(question_id: int):
    """
    Fetch presentation ID corresponding to the question ID, and retrieve AI-generated topics
    (titles and summaries) for the given presentation.

    Args:
        question_id (int): The ID of the question.

    Returns:
        dict: JSON-formatted response containing presentation ID and a list of topics.
    """
    try:
        with engine.connect() as conn:
            query_presentation_id = text("""
                SELECT presentation_id
                FROM original_questions
                WHERE id = :question_id
            """)
            result = conn.execute(query_presentation_id, {"question_id": question_id}).fetchone()

            if not result:
                return {"error": "No question found with the given ID."}

            presentation_id = result[0]

            query_topics = text("""
                SELECT title, summary
                FROM ai_generated_topics
                WHERE presentation_id = :presentation_id
            """)
            topics = conn.execute(query_topics, {"presentation_id": presentation_id}).fetchall()
            if not topics:
                return {"error": "No topics found for the given presentation ID."}

            formatted_topics = [{"title": topic[0], "summary": topic[1]} for topic in topics]

            return formatted_topics

    except Exception as e:
        return {"error": str(e)}

def find_topic_id_from_db(topic: str):
    """
    Find the topic ID for a given topic title from the ai_generated_topics table.

    Args:
        topic (str): The title of the topic to search for.

    Returns:
        int: The topic ID if found.

    Raises:
        Exception: If the topic is not found or a database error occurs.
    """
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT id
                FROM ai_generated_topics
                WHERE title = :topic
            """)

            result = conn.execute(query, {"topic": topic}).fetchone()

            if not result:
                raise Exception(f"No topic found with the title '{topic}'.")

            return result[0]
    except Exception as e:
        raise Exception(f"Database error: {e}")
