"""MCP server exposing NexQA tools."""

import os
from typing import Optional, Dict, Any

from mcp.server.fastmcp import FastMCP

from models import (
    process_file_path,
    process_url,
    add_to_vector_collection,
    list_vector_sources,
    query_collection,
)
from rag_service import run_rag_query


mcp = FastMCP(os.environ.get("MCP_SERVER_NAME", "NexQA MCP"))


def _resolve_user_id(user_id: Optional[str]) -> str:
    return user_id or os.environ.get("MCP_DEFAULT_USER_ID", "mcp_user")


@mcp.tool()
def ingest_document_path(file_path: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Ingest a local document (PDF/TXT/XLSX/XLS) by file path."""
    resolved_user_id = _resolve_user_id(user_id)
    splits = process_file_path(file_path)
    if not splits:
        return {"status": "error", "message": "No content extracted", "file_path": file_path}

    file_name = os.path.basename(file_path)
    collection_info = add_to_vector_collection(splits, file_name, resolved_user_id)

    return {
        "status": "success",
        "message": "Document ingested successfully",
        "file_name": file_name,
        "chunks": len(splits),
        "user_id": resolved_user_id,
        "collection": collection_info,
    }


@mcp.tool()
def add_url_source(url: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Ingest a web page as a knowledge source."""
    resolved_user_id = _resolve_user_id(user_id)
    splits = process_url(url)
    if not splits:
        return {"status": "error", "message": "No content extracted", "url": url}

    collection_info = add_to_vector_collection(splits, url, resolved_user_id)
    return {
        "status": "success",
        "message": "URL ingested successfully",
        "url": url,
        "chunks": len(splits),
        "user_id": resolved_user_id,
        "collection": collection_info,
    }


@mcp.tool()
def list_documents(user_id: Optional[str] = None) -> Dict[str, Any]:
    """List all ingested documents for a user."""
    resolved_user_id = _resolve_user_id(user_id)
    sources = list_vector_sources(resolved_user_id)
    return {"documents": sources, "user_id": resolved_user_id}


@mcp.tool()
def search_documents(query: str, user_id: Optional[str] = None, top_k: int = 5) -> Dict[str, Any]:
    """Semantic search over the vector store."""
    resolved_user_id = _resolve_user_id(user_id)
    results = query_collection(query, resolved_user_id, n_results=top_k)
    return {"results": results, "query": query, "count": len(results)}


@mcp.tool()
def rag_query(
    query: str,
    user_id: Optional[str] = None,
    top_k: int = 5,
    use_reranking: bool = True,
    force_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Run a RAG query using the NexQA pipeline."""
    resolved_user_id = _resolve_user_id(user_id)
    return run_rag_query(
        query_text=query,
        user_id=resolved_user_id,
        force_type=force_type,
        top_k=top_k,
        use_reranking=use_reranking,
    )


if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    port = int(os.environ.get("MCP_PORT", "8001"))

    if transport == "sse":
        mcp.run(transport="sse", host=host, port=port)
    else:
        mcp.run()
