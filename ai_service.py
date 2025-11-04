import os
import json
import logging
import httpx
import re
from collections import Counter
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pii_sanitizer import sanitize_text

logger = logging.getLogger(__name__)


def _extract_http_error_detail(exc: httpx.HTTPStatusError) -> str:
    try:
        data = exc.response.json()
        if isinstance(data, dict):
            error_data = data.get("error")
            if isinstance(error_data, dict):
                message = error_data.get("message")
                if message:
                    return str(message)
            for key in ("message", "detail", "error"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value
        text = exc.response.text
        if text:
            return text.strip()
    except Exception:
        pass
    return str(exc)

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
        # Provider selection: 'sidecar' (default) or 'together'
        provider_raw = (
            os.getenv("AI_PROVIDER")
            or os.getenv("AI_MODEL_PROVIDER")
            or os.getenv("AI_PROVIDER_DEFAULT")
            or "sidecar"
        )
        self.provider = provider_raw.strip().lower()

        # Local sidecar
        local_model_raw = (
            os.getenv("LOCAL_AI_MODEL")
            or os.getenv("AI_FALLBACK_MODEL")
            or "qwen_legal_q4_k_m"
        )
        self.local_default_model = local_model_raw
        self.local_ai_url = os.getenv("LOCAL_AI_URL", "https://portal-anwalts.ai").rstrip("/")

        # Together API (OpenAI-compatible)
        self.together_base = os.getenv("TOGETHER_BASE", "https://api.together.xyz/v1").rstrip("/")
        together_model_raw = (
            os.getenv("AI_MODEL_NAME")
            or os.getenv("TOGETHER_MODEL")
            or "deepcogito/cogito-v2-preview-llama-405B"
        )
        self.together_model = together_model_raw
        # Prefer env var; allow Docker secret fallback at /run/secrets/together_api_key
        self.together_api_key = (
            os.getenv("TOGETHER_API_KEY", "").strip()
            or os.getenv("TOGETHER_AI_API_KEY", "").strip()
            or self._read_secret_file("/run/secrets/together_api_key")
        )
        
        # Auto-fallback if Together API key missing
        if self.provider == "together" and not self.together_api_key:
            logger.warning("⚠️ TOGETHER_API_KEY missing, automatically switching to sidecar provider")
            self.provider = "sidecar"

        # Domain/system prompt to bias toward precise German legal answers
        self.system_prompt_de_legal = (
            "Du bist ein hochpräziser deutscher Rechtsassistent. Antworte in klarem, "
            "korrektem Deutsch, juristisch fundiert, mit konkreten Bezügen zum geltenden Recht. "
            "Sei knapp und zuverlässig; wenn unsicher, weise sachlich darauf hin."
        )

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

    def _read_secret_file(self, path: str) -> str:
        try:
            if path and os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read().strip()
        except Exception:
            pass
        return ""
    
    async def generate_completion(
        self,
        prompt: str,
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        context: Optional[str] = None,
        fail_hard: bool = False,
    ) -> AIResponse:
        """Generate AI completion using configured provider ('together' or 'sidecar') with cascade fallback."""
        # Try Together if configured and API key available
        if self.provider == "together" and self.together_api_key:
            try:
                return await self._generate_together_completion(
                    prompt=prompt,
                    model=(model or self.together_model),
                    max_tokens=max_tokens,
                    temperature=temperature,
                    context=context,
                )
            except Exception as e:
                logger.warning(f"⚠️ Together AI failed, falling back to sidecar: {e}")
                # Continue to sidecar fallback below
        
        # Always fall back to sidecar (local model)
        try:
            use_model = model or self.local_default_model
            return await self._generate_sidecar_completion(prompt, use_model, max_tokens, temperature, context)
        except httpx.HTTPStatusError as exc:
            logger.error(f"Provider {self.provider} returned error {exc.response.status_code}: {exc}")
            if fail_hard:
                raise
            return AIResponse(
                content=(
                    "Ich konnte die Antwort gerade nicht fertigstellen. "
                    "Bitte stellen Sie Ihre Frage gleich noch einmal – ich helfe sofort weiter."
                ),
                model=(model or (self.together_model if self.provider == "together" else self.local_default_model)),
                usage={"error": _extract_http_error_detail(exc)},
            )
        except Exception as e:
            logger.error(f"Error generating AI completion via {self.provider}: {e}")
            if fail_hard:
                raise
            return AIResponse(
                content=(
                    "Ich konnte die Antwort gerade nicht fertigstellen. "
                    "Bitte stellen Sie Ihre Frage gleich noch einmal – ich helfe sofort weiter."
                ),
                model=(model or (self.together_model if self.provider == "together" else self.local_default_model)),
                usage={"error": str(e)}
            )
    
    # Removed OpenAI and Anthropic providers; only sidecar is supported
    
    async def _generate_sidecar_completion(self, prompt: str, model: str, max_tokens: int, temperature: float, context: Optional[str] = None) -> AIResponse:
        """Generate completion using the remote FastAPI sidecar (Qwen legal model)."""
        try:
            async with httpx.AsyncClient() as client:
                # Add context to question if provided
                full_question = prompt
                if context:
                    full_question = f"Kontext aus vorherigen Nachrichten:\n{context}\n\nAktuelle Frage:\n{prompt}"
                
                payload = {
                    "question": full_question,
                    "k": 6  # Number of retrieval results
                }
                response = await client.post(
                    f"{self.local_ai_url}/v1/legal/answer_v2",
                    json=payload,
                    timeout=120.0,
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("answer", "")
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
                content=(
                    "Ich konnte Ihre Anfrage gerade nicht vollständig beantworten. "
                    "Bitte formulieren Sie sie kurz neu – ich unterstütze Sie sofort wieder."
                ),
                model=model,
                usage={"error": str(e)}
            )

    async def _generate_together_completion(self, prompt: str, model: str, max_tokens: int, temperature: float, context: Optional[str] = None) -> AIResponse:
        """Generate completion via Together's OpenAI-compatible Chat Completions API."""
        if not self.together_api_key:
            logger.error("Together AI: API key not configured")
            raise RuntimeError("TOGETHER_API_KEY not configured")
        
        logger.info(f"Together AI request: model={model}, prompt_len={len(prompt)}, max_tokens={max_tokens}")

        messages = [
            {"role": "system", "content": self.system_prompt_de_legal},
        ]
        if context:
            messages.append({"role": "system", "content": f"Kontext aus vorherigen Nachrichten:\n{context}"})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens or 1000,
            "temperature": 0.7 if temperature is None else float(temperature),
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                r = await client.post(f"{self.together_base}/chat/completions", headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()
            except httpx.TimeoutException as e:
                logger.error(f"Together AI timeout after 60s: {e}")
                raise RuntimeError("KI-Anfrage hat zu lange gedauert (Timeout). Bitte erneut versuchen.")
            except httpx.ConnectError as e:
                logger.error(f"Together AI connection error: {e}")
                raise RuntimeError("Verbindung zum KI-Dienst fehlgeschlagen. Bitte prüfen Sie Ihre Internetverbindung.")
            except httpx.HTTPStatusError as e:
                error_detail = _extract_http_error_detail(e)
                logger.error(f"Together AI HTTP error {e.response.status_code}: {error_detail}")
                if e.response.status_code == 429:
                    raise RuntimeError("AI-Dienst ist derzeit ausgelastet. Bitte in einigen Minuten erneut versuchen.")
                elif e.response.status_code in [404, 400]:
                    raise RuntimeError(f"Angefordertes KI-Modell nicht verfügbar: {model}")
                else:
                    raise RuntimeError(f"KI-Dienst Fehler: {error_detail}")
            except json.JSONDecodeError as e:
                logger.error(f"Together AI invalid JSON response: {e}")
                raise RuntimeError("KI-Dienst hat ungültige Antwort geliefert.")
            
            content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage") or {}
            
            logger.info(f"Together AI success: tokens={usage.get('total_tokens', 0)}, content_len={len(content)}")
            
            return AIResponse(
                content=content,
                model=model,
                model_used=model,
                tokens_used=usage.get("total_tokens"),
                generation_time_ms=None,
                cost_estimate=None,
                prompt_used=None,
                usage=usage,
            )

    
    def _tone_hint(self, tone: Optional[str]) -> str:
        return {
            "legal": "Juristisch präzise Formulierung.",
            "plain": "Leicht verständliche Formulierung.",
            "legal+plain": "Juristisch präzise – zugleich gut lesbar.",
            "neutral": "Neutraler Stil.",
        }.get(tone or "neutral", "Neutraler Stil.")

    def _extract_json_payload(self, text: str) -> Dict[str, Any]:
        snippet = (text or "").strip()
        if not snippet:
            raise ValueError("Antwort enthält kein JSON.")
        if snippet.startswith("```"):
            segments = [segment.strip() for segment in snippet.split("```") if segment.strip()]
            for segment in segments:
                if segment.startswith("{"):
                    snippet = segment
                    break
        start = snippet.find("{")
        end = snippet.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("JSON-Block konnte nicht erkannt werden.")
        candidate = snippet[start:end + 1]
        return json.loads(candidate)

    def compose_document_prompt(
        self,
        document_type: str,
        title: Optional[str],
        instructions: Optional[str],
        tone: Optional[str],
        template_content: Optional[str],
        variables: Optional[Dict[str, Any]],
        upload_excerpt: Optional[str],
    ) -> Tuple[str, Dict[str, Any]]:
        sanitized_instructions, inst_repl = sanitize_text(instructions or "")
        sanitized_template, tpl_repl = sanitize_text(template_content or "")
        sanitized_upload, upload_repl = sanitize_text((upload_excerpt or "")[:12000])

        sanitized_vars: Dict[str, str] = {}
        var_lines: List[str] = []
        var_repl = Counter()
        for key, value in (variables or {}).items():
            clean_value, repl = sanitize_text(str(value))
            sanitized_vars[key] = clean_value
            var_lines.append(f"- {key}: {clean_value}" if clean_value else f"- {key}: (leer)")
            var_repl.update(repl)

        redaction_counter = Counter()
        redaction_counter.update(inst_repl)
        redaction_counter.update(tpl_repl)
        redaction_counter.update(upload_repl)
        redaction_counter.update(var_repl)

        redaction_lines = (
            "\n".join(f"- {token}: {count}×" for token, count in redaction_counter.items())
            if redaction_counter
            else "Keine automatischen Redaktionen vorgenommen."
        )

        tone_hint = self._tone_hint(tone)

        prompt = f"""
[task:document][format:json]
Erstellen Sie ein vollständiges deutsches Rechtsdokument.

TITEL: {title or document_type}
DOKUMENTTYP: {document_type}
STIL: {tone_hint}

NUTZERANGABEN (bereits DSGVO-konform bereinigt):
{sanitized_instructions or '(keine zusätzlichen Angaben)'}

EINGELESENER TEXT (aus Upload, redigiert):
{sanitized_upload or '(kein Uploadtext)'}

VARIABLEN:
{("\n".join(var_lines) if var_lines else '(keine)')}

REDAKTIONSHINWEISE:
{redaction_lines}

VORLAGENINHALT (nur falls sinnvoll):
{sanitized_template or '(keine Vorlage)'}

ANFORDERUNGEN:
1. Verwenden Sie korrektes deutsches Recht und Rechtssprache; keine Platzhalter-Fragen.
2. Strukturieren Sie logisch (Überschriften, Abschnitte, ggf. Paragraphen) und formulieren Sie verbindlich.
3. Verfassen Sie den Text neu; keine unveränderten Passagen aus Beispielen/Vorlagen übernehmen.
4. Ergänzen Sie passende Klauseln, ohne sensible Daten erneut einzufügen.
5. Liefern Sie ein anwendungsbereites, kohärentes Dokument ohne Rückfragen.

AUSGABEFORMAT:
- JSON ONLY, ohne Prä-/Nachtext, in folgendem Schema: {json.dumps(self.document_json_schema, ensure_ascii=False)}
""".strip()

        return prompt, {
            "sanitized_instructions": sanitized_instructions,
            "sanitized_upload": sanitized_upload,
            "sanitized_variables": sanitized_vars,
            "sanitized_template": sanitized_template,
            "redactions": redaction_counter,
        }

    async def generate_document(
        self,
        document_type: str,
        title: Optional[str] = None,
        instructions: Optional[str] = None,
        tone: Optional[str] = None,
        template_content: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        upload_excerpt: Optional[str] = None,
        model: Optional[str] = None,
        fail_hard: bool = False,
    ) -> AIResponse:
        """Generate a legal document based on sanitized inputs."""
        prompt, meta = self.compose_document_prompt(
            document_type=document_type,
            title=title,
            instructions=instructions,
            tone=tone,
            template_content=template_content,
            variables=variables,
            upload_excerpt=upload_excerpt,
        )

        response = await self.generate_completion(
            prompt,
            model=model or (self.together_model if self.provider == "together" else self.local_default_model),
            max_tokens=getattr(self, "llm_max_tokens_default", 900),
            temperature=0.2,
            fail_hard=fail_hard,
        )
        response.prompt_used = prompt
        try:
            response.usage = response.usage or {}
            response.usage["redactions"] = dict(meta["redactions"])
            response.usage["sanitized"] = {
                "instructions": meta["sanitized_instructions"],
                "upload_excerpt": meta["sanitized_upload"],
                "template": meta["sanitized_template"],
                "variables": meta["sanitized_variables"],
            }
        except Exception:
            pass
        return response

    async def generate_template_from_document(
        self,
        document_text: str,
        filename: str = "",
        fail_hard: bool = False,
        max_chars: int = 12000,
    ) -> Tuple[Dict[str, Any], AIResponse, Dict[str, Any]]:
        """Derive a reusable template (title/category/content) from uploaded document text."""
        sanitized_text, replacements = sanitize_text(document_text or "")
        excerpt = (sanitized_text or "").strip()
        if not excerpt:
            raise ValueError("Keine verwertbaren Inhalte im Dokument gefunden.")
        excerpt = excerpt[:max_chars]

        prompt = f"""
[task:template_import][format:json]
Du bist ein deutscher Rechtsassistent. Analysiere den folgenden bereinigten Dokumenttext und erstelle daraus eine wiederverwendbare Vorlage.

ANFORDERUNGEN:
- Antworte ausschließlich mit JSON.
- Felder: "title" (max 90 Zeichen, prägnanter Vorlagenname), "category" (z.B. Arbeitsrecht, Vertrag, Compliance, Allgemein), "content" (HTML mit Überschriften, Absätzen, Listen; nutze Platzhalter in eckigen Klammern für variablen Text), optional "summary" (1–2 Sätze).
- Entferne Mandanten-spezifische Daten; verwende neutrale Platzhalter wie [Mandant], [Datum], [Betrag].
- Struktur: Verwende sinnvolle Abschnitte (z.B. <h1>, <h2>, <p>, <ul><li>).
- Wenn keine Kategorie eindeutig ableitbar ist, setze "Allgemein".

DATEINAME: {filename or 'Upload'}
TEXT (bereinigt):
\"\"\"{excerpt}\"\"\"
""".strip()

        response = await self.generate_completion(
            prompt,
            model=(self.together_model if self.provider == "together" else self.local_default_model),
            max_tokens=900,
            temperature=0.15,
            fail_hard=fail_hard,
        )

        payload = self._extract_json_payload(response.content or "")
        response.usage = response.usage or {}
        response.usage["import_replacements"] = dict(replacements)
        response.usage["import_chars"] = len(excerpt)
        meta = {
            "sanitized_text": sanitized_text,
            "replacements": replacements,
        }
        return payload, response, meta
    
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
        """Get list of available AI models for the active provider."""
        if self.provider == "together":
            return [self.together_model]
        return [self.local_default_model]

    async def summarize_email_message(
        self,
        subject: Optional[str],
        body: Optional[str],
        tone: str = "neutral",
        max_tokens: int = 600,
    ) -> AIResponse:
        """Generate a concise German legal summary for an email."""
        sanitized_subject, _ = sanitize_text(subject or "")
        sanitized_body, _ = sanitize_text(body or "")

        prompt = f"""
[task:email_summary][language:de]
Erstelle eine prägnante Zusammenfassung einer eingegangenen Mandanten-E-Mail.

Anforderungen:
- Sprache: Deutsch
- Ton: {tone}
- Umfang: 3–5 Bullet-Points plus optionale Handlungsempfehlung
- Hebe Fristen, Risiken und Verpflichtungen hervor.
- Gib, falls ersichtlich, Absenderrolle und Datum an.

BETREFF: {sanitized_subject or '(kein Betreff)'}

INHALT:
\"\"\"{sanitized_body}\"\"\"

LIEFERE:
- "summary_points": Aufzählung mit den Kernpunkten
- "risks": Liste konkreter Risiken oder "Keine"
- "actions": Liste empfohlener Schritte
- "deadline": ISO-Datum falls erwähnt, sonst leer
- "confidence": Prozentwert 0-100
- "language": Erkannten Sprachcode (z.B. de, en)
- "metadata": weitere Hinweise (z.B. Aktenzeichen)

Gib ausschließlich JSON zurück.
""".strip()

        return await self.generate_completion(
            prompt=prompt,
            model=self.together_model if self.provider == "together" else self.local_default_model,
            max_tokens=max_tokens,
            temperature=0.25,
            fail_hard=False,
        )

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.6,
        max_tokens: int = 900,
    ) -> AIResponse:
        """Run a conversational chat completion using sanitized history."""
        if not messages:
            raise ValueError("messages erforderlich")

        sanitized_history: List[Tuple[str, str]] = []
        for msg in messages:
            role = (msg.get("role") or "user").strip().lower()
            if role not in {"user", "assistant", "system"}:
                role = "user"
            content = (msg.get("content") or "").strip()
            sanitized, _ = sanitize_text(content)
            sanitized_history.append((role, sanitized))

        # Separate latest user message from prior context
        user_content = sanitized_history[-1][1]
        context_parts: List[str] = []
        system_prompt = self.system_prompt_de_legal

        for role, content in sanitized_history[:-1]:
            if role == "system":
                system_prompt = content or system_prompt
                continue
            role_label = "Mandant" if role == "user" else "Assistent"
            context_parts.append(f"{role_label}: {content}")

        context_text = "\n\n".join(context_parts).strip()

        return await self.generate_completion(
            prompt=user_content,
            model=model or (self.together_model if self.provider == "together" else self.local_default_model),
            max_tokens=max_tokens,
            temperature=temperature,
            context=f"{system_prompt}\n\n{context_text}" if context_text else system_prompt,
        )

    async def analyze_document_text(
        self,
        title: Optional[str],
        document_text: str,
        categories: Optional[List[str]] = None,
        max_tokens: int = 1000,
    ) -> AIResponse:
        """Extract legal insights, obligations, and risks from a document."""
        sanitized_text, replacements = sanitize_text(document_text or "")
        limited_text = sanitized_text[:18000]

        categories_hint = ", ".join(categories or [])

        prompt = f"""
[task:document_analysis][language:de]
Analysiere das folgende juristische Dokument und liefere strukturierte Erkenntnisse.

ANFORDERUNGEN:
- Sprache: Deutsch
- Gib JSON zurück mit Feldern:
  - "title": Klarer Titel (fallback: {title or "Dokument"})
  - "summary": Kurzfassung in 3-5 Sätzen
  - "obligations": Liste konkreter Pflichten/Termine
  - "risks": Liste erkannter Risiken mit Bewertung (niedrig/mittel/hoch)
  - "clauses": Liste wichtiger Klauseln (name, beschreibung, passage)
  - "categories": Liste thematischer Kategorien (z.B. {categories_hint or 'Arbeitsrecht, Datenschutz'})
  - "next_steps": Konkrete Handlungsempfehlungen
  - "confidence": Prozentwert 0-100
- Fass keine personenbezogenen Daten an; nutze neutrale Platzhalter.
- Markiere wörtliche Zitate als solche.

TITEL: {title or 'Dokument'}

TEXT (bereinigt):
\"\"\"{limited_text}\"\"\"

Hinweis: Ersetzte Werte (DSGVO) = {", ".join(replacements.keys()) if replacements else "keine"}
""".strip()

        return await self.generate_completion(
            prompt=prompt,
            model=self.together_model if self.provider == "together" else self.local_default_model,
            max_tokens=max_tokens,
            temperature=0.2,
            fail_hard=False,
        )
