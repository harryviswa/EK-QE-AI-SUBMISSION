import os
import tempfile
import chromadb
import ollama
from typing import List
import numpy as np
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, UnstructuredExcelLoader, WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from prompts import qa_testcase_prompt, qa_prompt, qa_strategy_prompt
from chromadb.config import Settings
from chromadb import Client
from chromadb import PersistentClient
from chromadb import EmbeddingFunction

# LLM Configuration
offline_models = ["gpt-oss:20b", "llama3.2:3b", "gemma3:1b", "deepseek-r1:latest", "qwen3:30b", "mistral:7b"]
active_model =  os.environ.get("OLLAMA_LLM_MODEL", "gemma3:1b").lower() #offline_models[2]  # Default offline model

# Embedding Configuration
# Set EMBEDDING_PROVIDER to 'azure' or 'ollama' via environment variable
embedding_provider = os.environ.get("EMBEDDING_PROVIDER", "ollama").lower()
embedding_model = os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text:latest")  # For Ollama
azure_embedding_model = os.environ.get("AZURE_EMBEDDING_MODEL", "text-embedding-ada-002")  # For Azure
cross_encoder_model = ["cross-encoder/ms-marco-MiniLM-L-12-v2", "cross-encoder/ms-marco-MiniLM-L-6-v2"]


# Custom Embedding Functions for ChromaDB
class OllamaEmbeddingFunction:
    """Custom Ollama embedding function for ChromaDB."""
    
    def __init__(self, url: str = "http://localhost:11434/api/embeddings", model_name: str = "nomic-embed-text:latest"):
        self.url = url
        self.model_name = model_name
    
    def name(self) -> str:
        """Return the name of the embedding function."""
        return "ollama"  # Keep consistent name for backward compatibility
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for input texts using Ollama."""
        embeddings = []
        try:
            for text in input:
                try:
                    response = ollama.embeddings(model=self.model_name, prompt=text)
                    embeddings.append(response['embedding'])
                except Exception as e:
                    print(f"Warning: Failed to generate embedding for text snippet: {str(e)[:100]}")
                    # Return zero vector as fallback
                    embeddings.append([0.0] * 384)  # Nomic embed text produces 384-dimensional vectors
            return embeddings
        except Exception as e:
            print(f"Error in Ollama embedding: {str(e)}")
            # Return zero vectors as fallback
            return [[0.0] * 384 for _ in input]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compatibility method for libraries expecting embed_documents."""
        return self(texts)

    def embed_query(self, text: str) -> List[float]:
        """Compatibility method for libraries expecting embed_query."""
        return self([text])[0]


def process_document(uploaded_file):
    """Process uploaded file and return document chunks."""
    suffix = os.path.splitext(uploaded_file.filename)[1]
    temp_file = tempfile.NamedTemporaryFile("wb", delete=False, suffix=suffix)
    try:
        temp_file.write(uploaded_file.read())
        temp_file.flush()
        temp_file.close()  # Close the file before loading
        
        if suffix.lower() == ".pdf":
            loader = PyMuPDFLoader(temp_file.name)
        elif suffix.lower() in [".txt"]:
            loader = TextLoader(temp_file.name)
        elif suffix.lower() in [".xlsx", ".xls"]:
            loader = UnstructuredExcelLoader(temp_file.name)
        else:
            raise ValueError("Unsupported file type!")
        
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""],
        )
        return text_splitter.split_documents(docs)
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file.name)
        except:
            pass


def process_url(url: str):
    """Process URL and return document chunks."""
    loader = WebBaseLoader(url)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "?", "!", " ", ""],
    )
    return text_splitter.split_documents(docs)


class AzureOpenAIEmbeddingFunction(EmbeddingFunction):
    """Custom Azure OpenAI embedding function for ChromaDB."""
    
    def __init__(self, api_key: str, azure_endpoint: str, api_version: str = "2024-02-01", model: str = "text-embedding-ada-002"):
        try:
            from openai import AzureOpenAI
        except ImportError:
            raise ImportError("Please install openai package: pip install openai")
        
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version
        )
        self.model = model
    
    def name(self) -> str:
        """Return the name of the embedding function."""
        return f"azure_openai_{self.model.replace('-', '_')}"
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for input texts."""
        # Azure OpenAI has a limit on batch size, process in chunks if needed
        embeddings = []
        batch_size = 16  # Azure OpenAI recommended batch size
        
        for i in range(0, len(input), batch_size):
            batch = input[i:i + batch_size]
            response = self.client.embeddings.create(
                input=batch,
                model=self.model
            )
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
        
        return embeddings


def get_embedding_function():
    """Get the appropriate embedding function based on configuration."""
    if embedding_provider == "azure":
        # Azure OpenAI Embeddings
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
        
        if not api_key or not azure_endpoint:
            raise ValueError(
                "Azure OpenAI credentials not found. Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables."
            )
        
        print(f"Using Azure OpenAI embeddings: {azure_embedding_model}")
        return AzureOpenAIEmbeddingFunction(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            model=azure_embedding_model
        )
    else:
        # Ollama Embeddings (default)
        print(f"Using Ollama embeddings: {embedding_model}")
        try:
            # Test Ollama connection
            test_response = ollama.embeddings(model=embedding_model, prompt="test")
            if test_response and 'embedding' in test_response:
                print(f"[OK] Ollama connection successful")
        except Exception as e:
            print(f"[WARN] Ollama connection failed: {str(e)}")
            print(f"       Proceeding with Ollama embeddings (will retry on each request)")
        
        return OllamaEmbeddingFunction(
            url="http://localhost:11434/api/embeddings",
            model_name=embedding_model,
        )


def get_vector_collection():
    """Get or create ChromaDB collection."""
    embedding_function = get_embedding_function()
    db_path = os.environ.get("CHROMA_DB_PATH", "./harry-rag-chroma-db")
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    return chroma_client.get_or_create_collection(
        name="harry_rag",
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"},
    )


def add_to_vector_collection(all_splits, file_name, user_id):
    """Add document chunks to vector collection."""
    collection = get_vector_collection()
    documents, metadatas, ids = [], [], []
    
    for idx, split in enumerate(all_splits):
        documents.append(split.page_content)
        split.metadata["file_name"] = file_name
        split.metadata["user_id"] = user_id
        metadatas.append(split.metadata)
        ids.append(f"{user_id}_{file_name}_{idx}")
    
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )
    return {"status": "success", "chunks_added": len(all_splits)}


def query_collection(prompt, user_id, n_results=10):
    """Query vector collection for relevant documents."""
    collection = get_vector_collection()
    results = collection.query(
        query_texts=[prompt],
        n_results=n_results,
        where={"user_id": user_id}
    )
    
    # Format results
    formatted_results = []
    if results["documents"] and len(results["documents"]) > 0:
        for i, doc in enumerate(results["documents"][0]):
            formatted_results.append({
                "content": doc,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0,
            })
    else:
        # Add first 5 documents if no results found
        collection = get_vector_collection()
        all_results = collection.get(
            where={"user_id": user_id},
            limit=5,
            include=["documents", "metadatas", "distances"]
        )
        if all_results["documents"]:
            for i, doc in enumerate(all_results["documents"]):
                formatted_results.append({
                    "content": doc,
                    "metadata": all_results["metadatas"][i] if all_results["metadatas"] else {},
                    "distance": all_results["distances"][i] if all_results["distances"] else 0,
                })
    
    return formatted_results


def determine_action(user_query, context=""):
    """AI agent determines which action to perform based on user input."""
    actions_description = """
Available actions:
1. ask - Answer general questions based on the knowledge base
2. summary - Summarize the provided context or documents
3. testcase_excel - Generate test cases in Excel-compatible format
4. test_case - Generate test cases in standard format
5. validate - Validate and analyze existing test cases
6. test_strategy - Develop a comprehensive test strategy
7. risk - Perform risk assessment and analysis

Based on the user query, determine which action is most appropriate.
    """
    
    decision_prompt = f"""You are an AI agent that decides which action to perform based on user queries.

{actions_description}

User Query: {user_query}

{f'Context: {context}' if context else ''}

Respond with ONLY the action name from the list (ask, summary, testcase_excel, test_case, validate, test_strategy, or risk). 
No explanation, just the action name."""
    
    try:
        response = ollama.chat(
            model=active_model,
            messages=[{"role": "user", "content": decision_prompt}],
            stream=False,
        )
        action = response["message"]["content"].strip().lower()
        print(f"AI Agent determined action: {action}")
        
        # Validate action
        valid_actions = ["ask", "summary", "testcase_excel", "test_case", "validate", "test_strategy", "risk"]
        if action not in valid_actions:
            print(f"Invalid action '{action}', defaulting to 'ask'")
            return "ask"  # Default to ask if invalid action
        
        return action
    except Exception as e:
        print(f"Error determining action: {str(e)}")
        return "ask"  # Default to ask on error


def call_llm(context="", sysprompt="", prompt="", spl_prompt="", mode="offline", client=None):
    """Call LLM with given context, system prompt, user prompt and special prompt."""
   

    if mode == "offline":
        # Use Ollama for offline mode
        try:
            user_message = (
                f"Context:\n{context}\n\n"
                f"Question:\n{prompt}\n\n"
                f"Requirements:\n{spl_prompt}\n\n"
                "Now provide your response:"
            )
            response = ollama.chat(
                model=active_model,
                messages=[
                    {"role": "system", "content": sysprompt},
                    {"role": "user", "content": user_message},
                ],
                stream=False,
            )
            result = response["message"]["content"]
            # Clean up the response - remove any accidental prompt echoing
            if "---CONTEXT START---" in result or "---QUESTION START---" in result:
                # If the response contains our markers, extract just the answer part
                if "Now provide your response:" in result:
                    result = result.split("Now provide your response:", 1)[1].strip()
            result = result.strip() if isinstance(result, str) else result
            if not result:
                return "No response generated. Please try again or provide more context."
            return result
        except Exception as e:
            raise Exception(f"Ollama LLM call failed: {str(e)}")
    else:
        # Use Azure OpenAI for online mode
        if client is None:
            # Try to create client from environment variables
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
            azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            
            if not api_key or not azure_endpoint:
                raise ValueError("Azure OpenAI client is required for online mode. Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")
            
            try:
                from openai import AzureOpenAI
                client = AzureOpenAI(
                    api_key=api_key,
                    azure_endpoint=azure_endpoint,
                    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
                )
            except ImportError:
                raise ImportError("Please install openai package: pip install openai")
        
        try:
             # Construct the full prompt - keep it clean and focused
            full_message = f"""{sysprompt}
                                Context:
                                {context}
                                Question:
                                {prompt}
                                {f'Requirements:' + chr(10) + spl_prompt + chr(10) + '' if spl_prompt else ''}

            Now provide your response:"""
            azure_model = os.environ.get("AZURE_OPENAI_MODEL", "gpt-4")
            response = client.chat.completions.create(
                model=azure_model,
                messages=[{"role": "user", "content": full_message}],
                temperature=0.7,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Azure OpenAI call failed: {str(e)}")


def re_rank_cross_encoders(query, documents):
    """Re-rank documents using cross-encoder."""
    if not documents or len(documents) == 0:
        return []
    
    # Lazy import to avoid torch initialization on startup
    try:
        from sentence_transformers import CrossEncoder
    except Exception as e:
        print(f"[WARN] Cross-encoder unavailable: {str(e)}")
        print("       Skipping re-ranking and returning original documents")
        return documents

    try:
        encoder_model = CrossEncoder(cross_encoder_model[0], trust_remote_code=True)
        ranks = encoder_model.rank(query, documents, top_k=min(3, len(documents)))

        ranked_docs = []
        for rank in ranks:
            ranked_docs.append(documents[rank["corpus_id"]])

        return ranked_docs
    except Exception as e:
        print(f"[WARN] Cross-encoder re-ranking failed: {str(e)}")
        print("       Falling back to original documents")
        return documents


def list_vector_sources(user_id):
    """List all document sources for a user."""
    collection = get_vector_collection()
    all_metadatas = collection.get(include=["metadatas"])["metadatas"]
    
    sources = set()
    for meta in all_metadatas:
        if meta.get("user_id") != user_id:
            continue
        source = meta.get("source") or meta.get("file_name") or meta.get("url")
        if source:
            sources.add(source)
    
    return list(sources)
