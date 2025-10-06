from crewai.tools import tool
import sys
import os
import vecs

# Add the root directory to the path to import from root level modules

from file_processor import FileProcessor


@tool("VectorSearchTool")
def vector_search(query: str, agent_id: str, limit: int = 5) -> str:
    """
    Performs a vector similarity search in the knowledge base.
    Returns relevant chunks of text that can help answer customer queries.
    args: query is str and the query you want to search against, agent_id is provided by user, limit is the number of chunks you want
    """
    try:
        vx = vecs.create_client(os.getenv("DB_CONNECTION"))
        docs = vx.get_or_create_collection(name="embeddings", dimension=1024)

        # Initialize file processor to generate query embedding
        file_processor = FileProcessor()

        # Generate embedding for the query
        query_embedding = file_processor.generate_embeddings([query])[0]

        # Query the vector collection
        results = docs.query(
            data=query_embedding,
            limit=limit,
            filters={"agentId": {"$eq": agent_id}},
            measure="cosine_distance",
            include_value=True,
            include_metadata=True
        )

        vx.disconnect()

        if not results:
            return "No relevant context found."

        # Format results
        formatted = "\n".join(
            f"- {result[2]['text']} (score: {float(result[1]):.4f})"
            for result in results
        )
        return f"Relevant context:\n{formatted}"

    except Exception as e:
        return f"Error during vector search: {str(e)}"
