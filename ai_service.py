import os
import json
import logging
import httpx
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class AIResponse:
    def __init__(self, content: str, model: str = "", usage: Dict[str, Any] = None,
                 model_used: Optional[str] = None,
                 tokens_used: Optional[int] = None,
                 generation_time_ms: Optional[int] = None,
                 cost_estimate: Optional[float] = None,
                 prompt_used: Optional[str] = None):
        self.content = content
        self.model = model
        self.usage = usage or {}
        self.model_used = model_used
        self.tokens_used = tokens_used
        self.generation_time_ms = generation_time_ms
        self.cost_estimate = cost_estimate
        self.prompt_used = prompt_used

class AIService:
    def __init__(self):
        # Only use the remote legal model sidecar
        self.local_default_model = os.getenv("LOCAL_AI_MODEL", "qwen_legal_q4_k_m")
        self.local_ai_url = os.getenv("LOCAL_AI_URL", "https://portal-anwalts.ai").rstrip("/")

        # Document JSON schema for structured output
        self.document_json_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "heading": {"type": "string"},
                            "content": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["title", "content"]
        }
    
    async def generate_completion(self, prompt: str, model: str = None, max_tokens: int = 1000, temperature: float = 0.7, context: Optional[str] = None) -> AIResponse:
        """Generate AI completion using the remote sidecar (trained Qwen legal model)."""
        model = model or self.local_default_model

        try:
            return await self._generate_sidecar_completion(prompt, model, max_tokens, temperature)
        except Exception as e:
            logger.error(f"Error generating AI completion: {e}")
            # Return a fallback response
            return AIResponse(
                content="Entschuldigung, es gab einen Fehler bei der Generierung der Antwort. Bitte versuchen Sie es erneut.",
                model=model,
                usage={"error": str(e)}
            )
    
    # Removed OpenAI and Anthropic providers; only sidecar is supported
    
    async def _generate_sidecar_completion(self, prompt: str, model: str, max_tokens: int, temperature: float) -> AIResponse:
        """Generate completion using the remote FastAPI sidecar (Qwen legal model)."""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "question": prompt,
                    "user_context": None,
                    "preferences": {
                        "temperature": temperature,
                        "top_p": 0.9,
                        "max_tokens": max_tokens,
                    },
                }
                response = await client.post(
                    f"{self.local_ai_url}/ai/legal/answer",
                    json=payload,
                    timeout=120.0,
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("answer_md", "")
                latency_ms = data.get("latency_ms")
                return AIResponse(
                    content=content,
                    model=model,
                    model_used=(model or self.local_default_model),
                    tokens_used=None,
                    generation_time_ms=latency_ms,
                    cost_estimate=None,
                    prompt_used=None,
                    usage={
                        "prompt_tokens": None,
                        "completion_tokens": None,
                        "total_tokens": None,
                    },
                )
        except Exception as e:
            logger.error(f"Error with sidecar AI completion: {e}")
            # Fallback to a simple response
            return AIResponse(
                content="Entschuldigung, der AI-Service ist momentan nicht verfügbar. Bitte versuchen Sie es später erneut.",
                model=model,
                usage={"error": str(e)}
            )
    
    async def generate_document(self, document_type: str, template_content: Optional[str] = None, variables: Optional[Dict[str, Any]] = None, model: Optional[str] = None) -> AIResponse:
        """Generate a legal document based on the provided parameters (sidecar-backed)."""
        # Build the prompt for document generation from variables
        parts: List[str] = []
        parts.append(f"Erstelle ein professionelles {document_type} auf Deutsch.")
        if variables:
            try:
                pretty_vars = json.dumps(variables, ensure_ascii=False, indent=2)
                parts.append("Eingabedaten:")
                parts.append(pretty_vars)
            except Exception:
                pass
        if template_content:
            parts.append("Verwende optional diese Vorlage als Basis (nur bei Bedarf):")
            parts.append(template_content)
        parts.append("Bitte liefere das Ergebnis als Fließtext in Markdown, juristisch korrekt und präzise.")
        prompt = "\n\n".join(parts)

        return await self.generate_completion(prompt, model=model or self.local_default_model, max_tokens=2000, temperature=0.3)
    
    def format_document_json(self, json_content: str) -> str:
        """Format JSON document content as HTML"""
        try:
            # Try to parse as JSON first
            doc_data = json.loads(json_content)
            
            html = f"<h1>{doc_data.get('title', 'Dokument')}</h1>\n"
            
            # Add main content
            if doc_data.get('content'):
                html += f"<div class='document-content'>{doc_data['content']}</div>\n"
            
            # Add sections if they exist
            if doc_data.get('sections'):
                for section in doc_data['sections']:
                    html += f"<h2>{section.get('heading', '')}</h2>\n"
                    html += f"<div class='section-content'>{section.get('content', '')}</div>\n"
            
            return html
            
        except json.JSONDecodeError:
            # If not valid JSON, return the content as-is with basic formatting
            return self._sanitize_output_text(json_content)
    
    def _sanitize_output_text(self, text: str) -> str:
        """Sanitize and format text output"""
        if not text:
            return ""
        
        # Remove any potential script tags or dangerous HTML
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<iframe[^>]*>.*?</iframe>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert line breaks to HTML
        text = text.replace('\n', '<br>')
        
        # Basic markdown-like formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        return text
    
    def _normalize_document_output(self, content: str) -> str:
        """Normalize document output for display"""
        if not content:
            return ""
        
        # Try to extract JSON from the content if it's wrapped in other text
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return self.format_document_json(json_match.group())
            except:
                pass
        
        # If no JSON found, sanitize the text
        return self._sanitize_output_text(content)
    
    def get_available_models(self) -> List[str]:
        """Get list of available AI models (restricted to the trained legal model)."""
        return ["qwen_legal_q4_k_m"]
