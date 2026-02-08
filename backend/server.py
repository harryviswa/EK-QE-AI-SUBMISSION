"""
NexQA.ai Backend API - Flask-based REST API for RAG operations
"""
import os
import io
import uuid
from datetime import datetime
from functools import wraps

import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.serving import WSGIRequestHandler

from models import (
    active_model,
    offline_models,
    process_document,
    process_url,
    get_vector_collection,
    add_to_vector_collection,
    query_collection,
    call_llm,
    determine_action,
    re_rank_cross_encoders,
    list_vector_sources,
)
from prompts import (
    qa_testcase_prompt,
    qa_prompt,
    qa_strategy_prompt,
    qa_testcase_validate_prompt,
    qa_risk_prompt,
)
from utils import generate_pdf
from swagger_generator import create_api_automation_script

load_dotenv()

app = Flask(__name__)
CORS(app)

# Increase timeout for long-running LLM operations (especially on Windows)
WSGIRequestHandler.timeout = 300  # 5 minutes

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "txt", "xlsx", "xls"}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user_id():
    """Extract or create user ID from request."""
    user_id = "harry"#request.headers.get("X-User-ID")
    # if not user_id:
    #     user_id = str(uuid.uuid4())
    return user_id


# ==================== HEALTH & INFO ====================


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


@app.route("/api/info", methods=["GET"])
def info():
    """Get API information and available models."""
    return jsonify(
        {
            "name": "NexQA.ai Backend",
            "version": "1.0.0",
            "available_models": offline_models,
            "active_model": active_model,
        }
    )


# ==================== DOCUMENT MANAGEMENT ====================


@app.route("/api/documents/upload", methods=["POST"])
def upload_document():
    """Upload and ingest a document."""
    try:
        user_id = get_user_id()

        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                    }
                ),
                400,
            )

        print(f"Processing file: {file.filename}")

        # Process document
        splits = process_document(file)

        if not splits:
            return jsonify({"error": "Failed to process document"}), 500

        print(f"Document processed: {len(splits)} chunks extracted")

        # Add to vector store
        collection_info = add_to_vector_collection(splits, file.filename, user_id)
        print(f"Document added to collection: {collection_info}")

        return jsonify(
            {
                "message": "Document uploaded successfully",
                "filename": file.filename,
                "chunks": len(splits),
                "user_id": user_id,
            }
        )

    except Exception as e:
        print(f"Error uploading document: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/add-url", methods=["POST"])
def add_url():
    """Add a web page as a knowledge source."""
    try:
        user_id = get_user_id()
        data = request.get_json()

        if not data or "url" not in data:
            return jsonify({"error": "URL not provided"}), 400

        url = data["url"]
        print(f"Processing URL: {url}")

        # Process URL
        splits = process_url(url)

        if not splits:
            return jsonify({"error": "Failed to process URL"}), 500

        print(f"URL processed: {len(splits)} chunks extracted")

        # Add to vector store
        result = add_to_vector_collection(splits, url, user_id)
        print(f"URL added to collection: {result}")

        return jsonify(
            {
                "message": "URL added successfully",
                "url": url,
                "chunks": len(splits),
                "user_id": user_id,
            }
        )

    except Exception as e:
        print(f"Error adding URL: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/list", methods=["GET"])
def list_documents():
    """List all ingested documents for user."""
    try:
        user_id = get_user_id()
        sources = list_vector_sources(user_id)

        return jsonify({"documents": sources, "user_id": user_id})

    except Exception as e:
        print(f"Error listing documents: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ==================== API AUTOMATION ====================


@app.route("/api/automation/generate-from-swagger", methods=["POST"])
def generate_api_automation():
    """Generate Python API automation script from Swagger/OpenAPI URL."""
    try:
        user_id = get_user_id()
        data = request.get_json()

        if not data or "swagger_url" not in data:
            return jsonify({"error": "Swagger URL not provided"}), 400

        swagger_url = data["swagger_url"]

        print(f"Generating API automation script from: {swagger_url}")

        # Generate the script
        script_content, filename = create_api_automation_script(swagger_url)

        return jsonify(
            {
                "message": "API automation script generated successfully",
                "filename": filename,
                "script": script_content,
                "swagger_url": swagger_url,
                "user_id": user_id,
                "status": "completed"
            }
        )

    except ValueError as e:
        print(f"Validation error in generate_api_automation: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error in generate_api_automation: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "status": "failed"}), 500


@app.route("/api/validate/testcases", methods=["POST"])
def validate_testcases():
    """Validate existing test cases from uploaded Excel file."""
    try:
        user_id = get_user_id()

        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({"error": "Only Excel files (.xlsx, .xls) are supported"}), 400

        print(f"Processing file: {file.filename}")
        # Process the Excel file to extract test cases
        splits = process_document(file)

        if not splits:
            return jsonify({"error": "Failed to process Excel file or file is empty"}), 500

        # Extract test case content
        testcases_content = "\n".join([split.page_content for split in splits])
        print(f"Extracted {len(splits)} chunks from test cases")

        # Retrieve knowledge base context
        context_results = query_collection(testcases_content, user_id, n_results=5)
        print(f"Found {len(context_results) if context_results else 0} context results")

        if not context_results:
            # Still provide validation without context
            context = ""
        else:
            context_docs = [result["content"] for result in context_results]
            context = "\n\n".join(context_docs[:3])

        # Call LLM to validate test cases with extended timeout
        try:
            # Ensure we don't timeout on Windows during long LLM calls
            response = call_llm(
                context=context,
                sysprompt=qa_prompt,
                prompt=testcases_content,
                spl_prompt=qa_testcase_validate_prompt,
                mode="offline",
                client=None
            )
            print(f"Validation completed successfully")
        except Exception as llm_error:
            print(f"LLM validation error: {str(llm_error)}")
            import traceback
            traceback.print_exc()
            # Return partial result instead of failing completely
            response = f"Validation result: Test cases were processed but detailed validation could not be completed. Error: {str(llm_error)}"
        return jsonify(
            {
                "message": "Test cases validated successfully",
                "filename": file.filename,
                "validation_result": response,
                "context_chunks_used": len(context_results) if context_results else 0,
                "user_id": user_id,
                "status": "completed"
            }
        )

    except Exception as e:
        print(f"Error in validate_testcases: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "status": "failed"}), 500


@app.route("/api/validate/testcases/quick", methods=["POST"])
def validate_testcases_quick():
    """Quick validation of test cases (just process the file without LLM analysis)."""
    try:
        user_id = get_user_id()

        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({"error": "Only Excel files (.xlsx, .xls) are supported"}), 400

        print(f"Quick validation of file: {file.filename}")
        splits = process_document(file)

        if not splits:
            return jsonify({"error": "Failed to process Excel file or file is empty"}), 500

        testcases_content = "\n".join([split.page_content for split in splits])
        print(f"Extracted {len(splits)} chunks from test cases")

        return jsonify(
            {
                "message": "Test case file processed successfully",
                "filename": file.filename,
                "chunks_extracted": len(splits),
                "content_preview": testcases_content[:500] + "..." if len(testcases_content) > 500 else testcases_content,
                "user_id": user_id,
                "status": "processed"
            }
        )

    except Exception as e:
        print(f"Error in quick validation: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ==================== QUERY & RAG ====================


@app.route("/api/query/search", methods=["POST"])
def search():
    """Semantic search in vector store."""
    try:
        user_id = get_user_id()
        data = request.get_json()

        if not data or "query" not in data:
            return jsonify({"error": "Query not provided"}), 400

        query_text = data["query"]
        top_k = data.get("top_k", 5)

        results = query_collection(query_text, user_id, top_k=top_k)

        return jsonify({"results": results, "query": query_text, "count": len(results)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/query/rag", methods=["POST"])
def rag_query():
    """RAG query with LLM response."""
    try:
        user_id = get_user_id()
        data = request.get_json()

        if not data or "query" not in data:
            return jsonify({"error": "Query not provided"}), 400

        query_text = data["query"]
        force_type = data.get("type", None)  # Optional: user can force a specific action type
        top_k = data.get("top_k", 5)
        use_reranking = data.get("use_reranking", True)

        # Retrieve context
        context_results = query_collection(query_text, user_id, n_results=top_k)

        if not context_results:
            # Even if no context is found, we can still call the LLM to get a response based on the query alone
           # return jsonify({"warning": "No relevant context found"}), 200
            print(f"No context found for query: {query_text}")
            context_results = query_collection("about", user_id, n_results=top_k)

        context_docs = []
        if context_results:
            context_docs = [result["content"] for result in context_results]

        context = "\n\n".join(context_docs[:3]) if context_docs else ""
        # Re-rank if enabled
        if use_reranking and len(context_docs) > 1:
            context_docs = re_rank_cross_encoders(query_text, context_docs)

            context = "\n\n".join(context_docs[:3])  # Use top 3 re-ranked docs

        # List of available actions for AI agent to decide
        prompt_templates = [
            {
                "type": "ask",
                "description": "Answer general questions based on the knowledge base",
                "sys_prompt": qa_prompt,
                "spl_prompt": "Provide a comprehensive answer based on the context.",
            },
            {
                "type": "summary",
                "description": "Summarize the provided context or documents",
                "sys_prompt": qa_prompt,
                "spl_prompt": "Summarize the context in concise bullet points or paragraphs.",
            },
            {
                "type": "testcase_excel",
                "description": "Generate test cases in Excel-compatible format",
                "sys_prompt": qa_prompt,
                "spl_prompt": "Generate test cases in a Markdown table format compatible with Excel import.",
            },
            {
                "type": "test_case",
                "description": "Generate test cases in standard format",
                "sys_prompt": qa_testcase_prompt,
                "spl_prompt": qa_testcase_prompt,
            },
            {
                "type": "validate",
                "description": "Validate existing test cases",
                "sys_prompt": qa_prompt,
                "spl_prompt": qa_testcase_validate_prompt,
            },
            {
                "type": "test_strategy",
                "description": "Develop a comprehensive test strategy",
                "sys_prompt": qa_strategy_prompt,
                "spl_prompt": "Provide a detailed test strategy. Also mention the risks, assumptions and estimated efforts required to complete the testing.",
            },
            {
                "type": "risk",
                "description": "Perform risk assessment and analysis",
                "sys_prompt": qa_risk_prompt,
                "spl_prompt": qa_risk_prompt,
            },
        ]

        # Determine which action to use
        if force_type:
            # User specified a type, use it if valid
            determined_action = force_type
        else:
            # AI agent determines the action based on user query
            determined_action = determine_action(query_text, context)

        # Get the selected action from the template list
        selected_action = next(
            (action for action in prompt_templates if action["type"] == determined_action),
            prompt_templates[0]  # Default to 'ask' if action not found
        )

        sys_prompt = selected_action["sys_prompt"]
        spl_prompt = selected_action["spl_prompt"]
        final_action_type = selected_action["type"]

        # Call LLM with proper error handling for long-running operations
        try:
            response = call_llm(
                context=context,
                sysprompt=sys_prompt,
                prompt=query_text,
                spl_prompt=spl_prompt,
                mode="offline",
                client=None
            )
        except Exception as llm_error:
            print(f"LLM call error in RAG query: {str(llm_error)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"LLM processing failed: {str(llm_error)}",
                "query": query_text,
                "type": final_action_type
            }), 500

        # Return full list of context results so the frontend can display
        # all knowledge sources (do not slice to top-3 here).
        return jsonify(
            {
                "query": query_text,
                "type": final_action_type,
                "context_chunks": len(context_results),
                "response": response,
                "sources": context_results,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== EXPORT ====================


@app.route("/api/export/pdf", methods=["POST"])
def export_pdf():
    """Export query results as PDF."""
    try:
        data = request.get_json()

        if not data or "content" not in data:
            return jsonify({"error": "Content not provided"}), 400

        content = data["content"]
        title = data.get("title", "NexQA Report")

        pdf_bytes = generate_pdf(content, title)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{title}.pdf",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/export/excel", methods=["POST"])
def export_excel():
    """Export query results as Excel."""
    try:
        data = request.get_json()

        if not data or "data" not in data:
            return jsonify({"error": "Data not provided"}), 400

        excel_data = data["data"]
        df = pd.DataFrame(excel_data)

        output = io.BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)

        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="nexqa_export.xlsx",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== ERROR HANDLERS ====================


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({"error": "File too large. Maximum size is 50MB"}), 413


@app.errorhandler(404)
def not_found(error):
    """Handle not found error."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server error."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    # Enable threaded mode to handle concurrent requests and prevent socket errors on Windows
    # Use_reloader=False to prevent double initialization issues
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=debug,
        threaded=True,
        use_reloader=False
    )
