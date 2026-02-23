"""
NexQA.ai Backend API - Flask-based REST API for RAG operations
"""
import os
import io
import uuid
import json
from datetime import datetime
from functools import wraps

import pandas as pd
from flask import Flask, request, jsonify, send_file, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.serving import WSGIRequestHandler

# Load environment variables before importing modules that read them
load_dotenv(override=True)

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
from rag_service import run_rag_query, stream_rag_query
from utils import generate_pdf
from swagger_generator import create_api_automation_script
from log_analyzer import AutomationLogAnalyzer, generate_llm_insights

app = Flask(__name__)
CORS(app)

# Increase timeout for long-running LLM operations (especially on Windows)
WSGIRequestHandler.timeout = 300  # 5 minutes

# Configuration
UPLOAD_FOLDER = "uploads"
LOG_UPLOAD_FOLDER = "automation_logs"
ALLOWED_EXTENSIONS = {"pdf", "txt", "xlsx", "xls"}
LOG_EXTENSIONS = {"xml", "html", "log", "junit"}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(LOG_UPLOAD_FOLDER):
    os.makedirs(LOG_UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["LOG_UPLOAD_FOLDER"] = LOG_UPLOAD_FOLDER
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


# ==================== AUTOMATION LOG ANALYSIS ====================


@app.route("/api/logs/analyze-folder", methods=["POST"])
def analyze_log_folder():
    """Analyze automation logs from a folder path."""
    try:
        user_id = get_user_id()
        data = request.get_json()

        if not data or "folder_path" not in data:
            return jsonify({"error": "Folder path not provided"}), 400

        folder_path = data["folder_path"].strip()
        generate_insights = data.get("generate_insights", True)

        # Security: Prevent path traversal
        if ".." in folder_path or folder_path.startswith("/"):
            return jsonify({"error": "Invalid folder path"}), 400

        # Resolve absolute path
        if not os.path.isabs(folder_path):
            folder_path = os.path.abspath(folder_path)

        if not os.path.isdir(folder_path):
            return jsonify({"error": f"Folder not found: {folder_path}"}), 404

        print(f"[LOG ANALYSIS] Analyzing folder: {folder_path}")

        # Analyze logs
        analyzer = AutomationLogAnalyzer()
        analysis_results = analyzer.analyze_log_folder(folder_path)
        summary = analyzer.get_summary()

        result = {
            "status": "success",
            "folder": folder_path,
            "user_id": user_id,
            "analysis_results": analysis_results,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Generate LLM insights if requested
        if generate_insights and summary.get("total_tests", 0) > 0:
            try:
                print("[LOG ANALYSIS] Generating LLM insights...")
                insights = generate_llm_insights(summary, call_llm)
                result["insights"] = insights
            except Exception as e:
                print(f"[LOG ANALYSIS] Error generating insights: {str(e)}")
                result["insights"] = f"Unable to generate insights: {str(e)}"

        return jsonify(result)

    except Exception as e:
        print(f"[LOG ANALYSIS] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "status": "failed"}), 500


@app.route("/api/logs/upload", methods=["POST"])
def upload_log_files():
    """Upload automation log files (supports multiple files)."""
    try:
        user_id = get_user_id()

        if "files" not in request.files:
            return jsonify({"error": "No files provided"}), 400

        files = request.files.getlist("files")
        if not files or len(files) == 0:
            return jsonify({"error": "No files selected"}), 400

        # Create user-specific log folder
        user_log_folder = os.path.join(LOG_UPLOAD_FOLDER, user_id)
        if not os.path.exists(user_log_folder):
            os.makedirs(user_log_folder)

        uploaded_files = []
        for file in files:
            if file.filename == "":
                continue

            # Check file extension
            file_ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
            if file_ext not in LOG_EXTENSIONS:
                continue

            # Save file
            filename = os.path.join(user_log_folder, file.filename)
            file.save(filename)
            uploaded_files.append(file.filename)

        if not uploaded_files:
            return jsonify({"error": "No valid log files uploaded"}), 400

        print(f"[LOG UPLOAD] Uploaded {len(uploaded_files)} files to {user_log_folder}")

        # Analyze the uploaded logs
        analyzer = AutomationLogAnalyzer()
        analysis_results = analyzer.analyze_log_folder(user_log_folder)
        summary = analyzer.get_summary()

        result = {
            "status": "success",
            "uploaded_files": uploaded_files,
            "folder": user_log_folder,
            "file_count": len(uploaded_files),
            "analysis_results": analysis_results,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Generate insights automatically
        try:
            print("[LOG UPLOAD] Generating LLM insights...")
            insights = generate_llm_insights(summary, call_llm)
            result["insights"] = insights
        except Exception as e:
            print(f"[LOG UPLOAD] Error generating insights: {str(e)}")
            result["insights"] = f"Unable to generate insights: {str(e)}"

        return jsonify(result)

    except Exception as e:
        print(f"[LOG UPLOAD] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "status": "failed"}), 500


@app.route("/api/logs/summary", methods=["GET"])
def get_logs_summary():
    """Get summary of previously analyzed logs."""
    try:
        user_id = get_user_id()
        user_log_folder = os.path.join(LOG_UPLOAD_FOLDER, user_id)

        if not os.path.exists(user_log_folder):
            return jsonify({
                "status": "no_logs",
                "message": "No logs found for this user",
                "summary": {}
            })

        analyzer = AutomationLogAnalyzer()
        analysis_results = analyzer.analyze_log_folder(user_log_folder)
        summary = analyzer.get_summary()

        return jsonify({
            "status": "success",
            "folder": user_log_folder,
            "analysis_results": analysis_results,
            "summary": summary,
        })

    except Exception as e:
        print(f"[LOG SUMMARY] Error: {str(e)}")
        return jsonify({"error": str(e), "status": "failed"}), 500


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

        try:
            result = run_rag_query(
                query_text=query_text,
                user_id=user_id,
                force_type=force_type,
                top_k=top_k,
                use_reranking=use_reranking,
            )
            print(f"[SERVER] RAG query returned: type={result.get('type')}, query={query_text}")
        except Exception as llm_error:
            print(f"[SERVER] LLM call error in RAG query: {str(llm_error)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"LLM processing failed: {str(llm_error)}",
                "query": query_text,
                "type": force_type or "ask",
            }), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _sse_event(event_name: str, payload: dict) -> str:
    return f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.route("/api/query/rag/stream", methods=["POST"])
def rag_query_stream():
    """RAG query with streaming response (SSE)."""
    try:
        user_id = get_user_id()
        data = request.get_json()

        if not data or "query" not in data:
            return jsonify({"error": "Query not provided"}), 400

        query_text = data["query"]
        force_type = data.get("type", None)
        top_k = data.get("top_k", 5)
        use_reranking = data.get("use_reranking", True)

        try:
            result = stream_rag_query(
                query_text=query_text,
                user_id=user_id,
                force_type=force_type,
                top_k=top_k,
                use_reranking=use_reranking,
            )
            print(f"[SERVER] RAG stream started: type={result.get('type')}, query={query_text}")
        except Exception as llm_error:
            print(f"[SERVER] LLM call error in RAG stream: {str(llm_error)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"LLM processing failed: {str(llm_error)}",
                "query": query_text,
                "type": force_type or "ask",
            }), 500

        def generate():
            try:
                meta_payload = {
                    "query": result.get("query"),
                    "type": result.get("type"),
                    "context_chunks": result.get("context_chunks"),
                    "sources": result.get("sources") or [],
                }
                yield _sse_event("meta", meta_payload)

                full_response = ""
                for token in result.get("stream"):
                    full_response += token
                    yield _sse_event("token", {"token": token})

                if not full_response:
                    try:
                        fallback = run_rag_query(
                            query_text=query_text,
                            user_id=user_id,
                            force_type=force_type,
                            top_k=top_k,
                            use_reranking=use_reranking,
                        )
                        full_response = fallback.get("response", "") or ""
                    except Exception as fallback_error:
                        yield _sse_event("error", {"error": str(fallback_error)})

                yield _sse_event("done", {
                    "response": full_response,
                    "type": result.get("type"),
                })
            except Exception as e:
                yield _sse_event("error", {"error": str(e)})

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
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
