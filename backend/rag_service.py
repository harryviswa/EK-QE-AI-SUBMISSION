"""Shared RAG service logic used by HTTP and MCP servers."""

from typing import Optional, Dict, Any, List

from models import (
    query_collection,
    call_llm,
    call_llm_stream,
    determine_action,
    re_rank_cross_encoders,
)
from prompts import (
    qa_testcase_prompt,
    qa_prompt,
    qa_strategy_prompt,
    qa_testcase_validate_prompt,
    qa_risk_prompt,
)

# Logging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def run_rag_query(
    query_text: str,
    user_id: str,
    force_type: Optional[str] = None,
    top_k: int = 5,
    use_reranking: bool = True,
) -> Dict[str, Any]:
    """Run RAG query and return response payload."""
    context_results = query_collection(query_text, user_id, n_results=top_k)

    if not context_results:
        context_results = query_collection("about", user_id, n_results=top_k)

    context_docs: List[str] = []
    if context_results:
        context_docs = [result["content"] for result in context_results]

    context = "\n\n".join(context_docs[:3]) if context_docs else ""

    if use_reranking and len(context_docs) > 1:
        context_docs = re_rank_cross_encoders(query_text, context_docs)
        context = "\n\n".join(context_docs[:3])

    prompt_templates = [
        {
            "type": "ask",
            "aliases": ["question", "answer", "general"],
            "description": "Answer general questions based on the knowledge base",
            "sys_prompt": qa_prompt,
            "spl_prompt": "Provide a comprehensive answer based on the context.",
        },
        {
            "type": "summary",
            "aliases": ["summarize", "summarise", "overview"],
            "description": "Summarize the provided context or documents",
            "sys_prompt": qa_prompt,
            "spl_prompt": "Summarize the context in concise bullet points or paragraphs.",
        },
        {
            "type": "testcase_excel",
            "aliases": ["excel", "xlsx", "test_case_excel", "testcase", "test_cases", "tc", "generate test", "test_case"],
            "description": "Generate test cases in Excel-compatible JIRA format with S.no, Summary, Description, Preconditions, Step Summary, Expected Results",
            "sys_prompt": qa_testcase_prompt,
            "spl_prompt": qa_testcase_prompt,
        },
        {
            "type": "validate",
            "aliases": ["validate test", "check test", "review test", "improve test"],
            "description": "Analyze and suggest improvements to existing test cases",
            "sys_prompt": qa_testcase_validate_prompt,
            "spl_prompt": qa_testcase_validate_prompt,
        },
        {
            "type": "test_strategy",
            "aliases": ["strategy", "test plan", "test approach", "test scope"],
            "description": "Develop a comprehensive test strategy with scope, approach, levels, types, environment, criteria, risks",
            "sys_prompt": qa_strategy_prompt,
            "spl_prompt": qa_strategy_prompt,
        },
        {
            "type": "risk",
            "aliases": ["risk assessment", "risk analysis", "potential risk"],
            "description": "Perform risk assessment and analysis with description, category, impact, likelihood, and mitigation",
            "sys_prompt": qa_risk_prompt,
            "spl_prompt": qa_risk_prompt,
        },
    ]

    if force_type:
        determined_action = force_type
    else:
        determined_action = determine_action(query_text, context)

    logger.info(f"[RAG] determine_action returned: {determined_action}")
    logger.info(f"[RAG] Available prompt_templates: {[a['type'] for a in prompt_templates]}")

    # Try exact match first
    selected_action = next(
        (action for action in prompt_templates if action["type"] == determined_action),
        None,
    )
    
    if selected_action:
        logger.info(f"[RAG] ✓ Exact match found for: {determined_action}")
    else:
        logger.warning(f"[RAG] ✗ No exact match for: {determined_action}, trying aliases...")
    
    # Fallback: try alias matching
    if not selected_action:
        selected_action = next(
            (action for action in prompt_templates 
             if determined_action in action.get("aliases", [])),
            None,
        )
        if selected_action:
            logger.info(f"[RAG] ✓ Alias match found: {selected_action['type']}")
    
    # Final fallback: use ask
    if not selected_action:
        logger.warning(f"[RAG] Action '{determined_action}' not found, falling back to 'ask'")
        selected_action = next(action for action in prompt_templates if action["type"] == "ask")

    logger.info(f"[RAG] Final selected action: {selected_action['type']}")

    sys_prompt = selected_action["sys_prompt"]
    spl_prompt = selected_action["spl_prompt"]
    final_action_type = selected_action["type"]

    response = call_llm(
        context=context,
        sysprompt=sys_prompt,
        prompt=query_text,
        spl_prompt=spl_prompt,
        mode="offline",
        client=None,
    )

    return {
        "query": query_text,
        "type": final_action_type,
        "context_chunks": len(context_results) if context_results else 0,
        "response": response,
        "sources": context_results,
    }


def stream_rag_query(
    query_text: str,
    user_id: str,
    force_type: Optional[str] = None,
    top_k: int = 5,
    use_reranking: bool = True,
) -> Dict[str, Any]:
    """Prepare streaming RAG query and return metadata + stream generator."""
    context_results = query_collection(query_text, user_id, n_results=top_k)

    if not context_results:
        context_results = query_collection("about", user_id, n_results=top_k)

    context_docs: List[str] = []
    if context_results:
        context_docs = [result["content"] for result in context_results]

    context = "\n\n".join(context_docs[:3]) if context_docs else ""

    if use_reranking and len(context_docs) > 1:
        context_docs = re_rank_cross_encoders(query_text, context_docs)
        context = "\n\n".join(context_docs[:3])

    prompt_templates = [
        {
            "type": "ask",
            "aliases": ["question", "answer", "general"],
            "description": "Answer general questions based on the knowledge base",
            "sys_prompt": qa_prompt,
            "spl_prompt": "Provide a comprehensive answer based on the context.",
        },
        {
            "type": "summary",
            "aliases": ["summarize", "summarise", "overview"],
            "description": "Summarize the provided context or documents",
            "sys_prompt": qa_prompt,
            "spl_prompt": "Summarize the context in concise bullet points or paragraphs.",
        },
        {
            "type": "testcase_excel",
            "aliases": ["excel", "xlsx", "test_case_excel", "testcase", "test_cases", "tc", "generate test", "test_case"],
            "description": "Generate test cases in Excel-compatible JIRA format with S.no, Summary, Description, Preconditions, Step Summary, Expected Results",
            "sys_prompt": qa_testcase_prompt,
            "spl_prompt": qa_testcase_prompt,
        },
        {
            "type": "validate",
            "aliases": ["validate test", "check test", "review test", "improve test"],
            "description": "Analyze and suggest improvements to existing test cases",
            "sys_prompt": qa_testcase_validate_prompt,
            "spl_prompt": qa_testcase_validate_prompt,
        },
        {
            "type": "test_strategy",
            "aliases": ["strategy", "test plan", "test approach", "test scope"],
            "description": "Develop a comprehensive test strategy with scope, approach, levels, types, environment, criteria, risks",
            "sys_prompt": qa_strategy_prompt,
            "spl_prompt": qa_strategy_prompt,
        },
        {
            "type": "risk",
            "aliases": ["risk assessment", "risk analysis", "potential risk"],
            "description": "Perform risk assessment and analysis with description, category, impact, likelihood, and mitigation",
            "sys_prompt": qa_risk_prompt,
            "spl_prompt": qa_risk_prompt,
        },
    ]

    if force_type:
        determined_action = force_type
    else:
        determined_action = determine_action(query_text, context)

    logger.info(f"[RAG] determine_action returned: {determined_action}")
    logger.info(f"[RAG] Available prompt_templates: {[a['type'] for a in prompt_templates]}")

    selected_action = next(
        (action for action in prompt_templates if action["type"] == determined_action),
        None,
    )

    if selected_action:
        logger.info(f"[RAG] ✓ Exact match found for: {determined_action}")
    else:
        logger.warning(f"[RAG] ✗ No exact match for: {determined_action}, trying aliases...")

    if not selected_action:
        selected_action = next(
            (action for action in prompt_templates
             if determined_action in action.get("aliases", [])),
            None,
        )
        if selected_action:
            logger.info(f"[RAG] ✓ Alias match found: {selected_action['type']}")

    if not selected_action:
        logger.warning(f"[RAG] Action '{determined_action}' not found, falling back to 'ask'")
        selected_action = next(action for action in prompt_templates if action["type"] == "ask")

    logger.info(f"[RAG] Final selected action: {selected_action['type']}")

    sys_prompt = selected_action["sys_prompt"]
    spl_prompt = selected_action["spl_prompt"]
    final_action_type = selected_action["type"]

    stream = call_llm_stream(
        context=context,
        sysprompt=sys_prompt,
        prompt=query_text,
        spl_prompt=spl_prompt,
        mode="offline",
        client=None,
    )

    return {
        "query": query_text,
        "type": final_action_type,
        "context_chunks": len(context_results) if context_results else 0,
        "sources": context_results,
        "stream": stream,
    }
