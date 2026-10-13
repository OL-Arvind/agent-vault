import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from agent_vault.mcp_server import search_vault
from agent_vault.config import get_default_vault_dir

SYSTEM_PROMPT = """You are Agent-Vault Assistant, an intelligent engineering memory companion.
You have access to historical session cards extracted from the developer's local AI coding agent sessions (Antigravity, Cursor, Claude Code, etc.).
Your job is to answer the developer's question by analyzing and synthesizing insights from their actual past coding history.

Guidelines:
1. Be specific and grounded in the provided session excerpts. Cite conversation topics, dates, and file paths when relevant.
2. If identifying patterns, extract repeated bugs, architecture decisions, tools used, and common mistakes.
3. If the context doesn't have enough information to answer completely, acknowledge what is known and suggest what to search for.
4. Format your answer with clean Markdown headers, bullet points, and code blocks where helpful.
"""

def detect_provider() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Detects available LLM provider, API key, and default model from environment.
    Returns: (provider_name, api_key, default_model)
    """
    # 1. Google Gemini
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini", os.environ["GEMINI_API_KEY"], "gemini-2.0-flash"
    
    # 2. Groq (Free & Ultra Fast)
    if os.environ.get("GROQ_API_KEY"):
        return "groq", os.environ["GROQ_API_KEY"], "llama-3.3-70b-versatile"

    # 3. OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        return "openai", os.environ["OPENAI_API_KEY"], "gpt-4o-mini"

    # 4. Anthropic
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic", os.environ["ANTHROPIC_API_KEY"], "claude-3-5-haiku-latest"

    # 5. DeepSeek
    if os.environ.get("DEEPSEEK_API_KEY"):
        return "deepseek", os.environ["DEEPSEEK_API_KEY"], "deepseek-chat"

    # 6. OpenRouter
    if os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter", os.environ["OPENROUTER_API_KEY"], "meta-llama/llama-3.3-70b-instruct"

    # 7. Check local Ollama
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    try:
        req = urllib.request.Request(f"{ollama_host}/api/tags", headers={"User-Agent": "agent-vault"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", [])]
                chosen = models[0] if models else "llama3"
                return "ollama", ollama_host, chosen
    except Exception:
        pass

    return None, None, None

def call_llm(provider: str, api_key: str, model: str, system_prompt: str, user_prompt: str) -> str:
    """Invokes LLM API using pure standard library urllib."""
    if provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": user_prompt}]}
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json["candidates"][0]["content"]["parts"][0]["text"]

    elif provider in ("openai", "groq", "deepseek", "openrouter"):
        endpoints = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "groq": "https://api.groq.com/openai/v1/chat/completions",
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
            "openrouter": "https://openrouter.ai/api/v1/chat/completions"
        }
        url = endpoints[provider]
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json["choices"][0]["message"]["content"]

    elif provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": model,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json["content"][0]["text"]

    elif provider == "ollama":
        url = f"{api_key}/api/generate"
        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json.get("response", "")

    raise ValueError(f"Unsupported provider: {provider}")

def synthesize_vault_answer(
    query: str,
    vault_dir: Optional[Path] = None,
    limit: int = 5,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieves matching sessions and prompts the selected LLM to synthesize an answer."""
    if vault_dir is None:
        vault_dir = get_default_vault_dir()

    # Detect provider if not specified
    det_provider, det_key, det_model = detect_provider()
    provider = provider or det_provider
    api_key = api_key or det_key
    model = model or det_model

    if not provider or not api_key:
        return {
            "status": "no_provider",
            "answer": None,
            "sources": []
        }

    # Search vault
    matches = search_vault(query, vault_dir=vault_dir, limit=limit)
    if not matches:
        return {
            "status": "no_matches",
            "answer": f"No past sessions found in your vault matching: '{query}'",
            "sources": []
        }

    # Build context from full dev cards (capped to avoid exceeding token limit)
    context_chunks = []
    sources = []
    for m in matches:
        conv_file = Path(m["file_path"])
        sources.append({
            "id": m["conversation_id"],
            "title": m["title"],
            "date": m["date"],
            "file": str(conv_file)
        })
        if conv_file.exists():
            text = conv_file.read_text(encoding="utf-8", errors="ignore")
            # Truncate very long cards to 3500 chars to fit context window comfortably
            if len(text) > 3500:
                text = text[:3500] + "\n...[truncated for length]..."
            context_chunks.append(f"--- SESSION CARD ({m['date'][:10]} | {m['title']}) ---\n{text}\n")

    combined_context = "\n".join(context_chunks)
    user_prompt = f"""Developer's Question:
"{query}"

Here are the most relevant session dev cards retrieved from the developer's Agent-Vault:
{combined_context}

Please provide a comprehensive, structured response answering the question based directly on these historical sessions."""

    try:
        answer = call_llm(provider, api_key, model, SYSTEM_PROMPT, user_prompt)
        return {
            "status": "success",
            "provider": provider,
            "model": model,
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "provider": provider,
            "model": model,
            "sources": sources
        }
