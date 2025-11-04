# AI Integration Capability - Together AI

## ADDED Requirements

### Requirement: Together AI Provider Integration
The system SHALL integrate with Together AI as the primary AI service provider for document generation and completions.

#### Scenario: Successful AI completion request
- **WHEN** backend calls `ai_service.generate_completion(prompt="Erstelle einen Mietvertrag", model="deepcogito/cogito-v2-preview-llama-405B")`
- **THEN** system sends POST request to `https://api.together.xyz/v1/chat/completions`
- **AND** includes Bearer token authentication with `TOGETHER_API_KEY`
- **AND** receives JSON response with `choices[0].message.content` containing generated text
- **AND** returns AIResponse object with content, model, usage stats

#### Scenario: API key validation
- **WHEN** system starts and `AI_PROVIDER=together` is set
- **THEN** system reads `TOGETHER_API_KEY` from environment variable
- **AND** if API key is missing or empty, logs warning "TOGETHER_API_KEY not configured"
- **AND** API requests fail with clear error message about missing authentication

#### Scenario: Handle Together AI rate limiting
- **WHEN** Together AI returns HTTP 429 (rate limit exceeded)
- **THEN** system parses rate limit error from response
- **AND** returns user-friendly error "AI-Dienst ist derzeit ausgelastet. Bitte in einigen Minuten erneut versuchen."
- **AND** logs detailed error for debugging including retry-after header

#### Scenario: Handle Together AI model unavailability
- **WHEN** Together AI returns HTTP 404 (model not found) or 400 (invalid model)
- **THEN** system parses model error from response
- **AND** returns error "Angefordertes KI-Modell nicht verfügbar"
- **AND** logs which model was requested for debugging

### Requirement: AI Service Error Handling
The system SHALL handle all AI service failures gracefully with proper error messages and fallback behavior.

#### Scenario: Timeout handling for slow AI responses
- **WHEN** Together AI request takes longer than 60 seconds
- **THEN** system times out the request with httpx timeout configuration
- **AND** returns error "KI-Anfrage hat zu lange gedauert (Timeout)"
- **AND** logs timeout event with prompt length and model for debugging

#### Scenario: Network error handling
- **WHEN** system cannot connect to Together AI due to network issue
- **THEN** catches httpx.ConnectError or httpx.NetworkError
- **AND** returns error "Verbindung zum KI-Dienst fehlgeschlagen. Bitte prüfen Sie Ihre Internetverbindung."
- **AND** logs full network error for investigation

#### Scenario: Invalid API response handling
- **WHEN** Together AI returns malformed JSON or unexpected response structure
- **THEN** system catches JSON parse error
- **AND** returns error "KI-Dienst hat ungültige Antwort geliefert"
- **AND** logs raw response body (truncated) for debugging

#### Scenario: Fallback to graceful degradation
- **WHEN** Together AI fails with any error in non-critical operation
- **THEN** system can optionally return fallback response instead of hard error
- **AND** fallback response contains message "Ich konnte Ihre Anfrage gerade nicht vollständig beantworten. Bitte formulieren Sie sie kurz neu."
- **AND** error is logged but user can continue using the application

### Requirement: AI Prompt Composition for Legal Documents
The system SHALL compose comprehensive prompts for legal document generation that produce high-quality, legally sound German documents.

#### Scenario: Basic document prompt composition
- **WHEN** system composes prompt for document_type="Mietvertrag", instructions="2-Zimmer-Wohnung, 800 EUR Miete"
- **THEN** prompt includes German legal system context
- **AND** prompt specifies document type clearly
- **AND** prompt includes user instructions
- **AND** prompt requests structured output with proper headings
- **AND** prompt emphasizes German legal terminology and precision

#### Scenario: Prompt with template content
- **WHEN** system composes prompt with template_content containing NDA structure
- **THEN** prompt instructs AI to follow template structure
- **AND** prompt asks AI to fill in placeholders with generated content
- **AND** generated document maintains template format

#### Scenario: Prompt with uploaded file context
- **WHEN** system composes prompt with upload_excerpt containing extracted text
- **THEN** prompt includes sanitized upload content as reference
- **AND** prompt instructs AI to use upload as context/example
- **AND** prompt notes that PII has been redacted for privacy

#### Scenario: Prompt with tone specification
- **WHEN** user selects tone="legal" (juristic language)
- **THEN** prompt emphasizes precise legal terminology
- **AND** generated document uses formal German legal style
- **WHEN** user selects tone="plain" (easy language)
- **THEN** prompt requests clear, accessible German language
- **AND** generated document avoids complex legal jargon where possible

### Requirement: AI Response Caching
The system SHALL cache AI responses in Redis to improve performance and reduce API costs.

#### Scenario: Cache hit for repeated prompt
- **WHEN** user generates document with identical inputs as previous request
- **THEN** system generates cache key from prompt + model + parameters
- **AND** checks Redis for cached response
- **AND** if cache hit, returns cached response immediately without calling Together AI
- **AND** response time is under 100ms for cached requests

#### Scenario: Cache miss triggers new AI request
- **WHEN** user generates document with new/modified inputs
- **THEN** system checks Redis cache and finds no match
- **AND** calls Together AI API for new generation
- **AND** stores response in Redis with TTL=3600 seconds (1 hour)
- **AND** subsequent identical requests use cached version

#### Scenario: Cache key includes user context
- **WHEN** system generates cache key for AI request
- **THEN** key includes user_id to prevent cross-user cache leaks
- **AND** key includes prompt hash, model, temperature, max_tokens
- **AND** key is deterministic for same inputs

### Requirement: AI Service Health Monitoring
The system SHALL provide health check endpoints to verify AI service connectivity and configuration.

#### Scenario: AI health check endpoint
- **WHEN** monitoring system calls `/health/ai` endpoint
- **THEN** system attempts simple AI completion request
- **AND** returns HTTP 200 if Together AI responds successfully
- **AND** returns HTTP 503 if Together AI is unreachable or returns errors
- **AND** response includes status, latency_ms, model used, timestamp

#### Scenario: Health check included in main health endpoint
- **WHEN** system calls `/health` endpoint
- **THEN** response includes `ai_service: {status: "healthy", provider: "together", model: "deepcogito/cogito-v2-preview-llama-405B"}`
- **AND** if AI service is down, status shows "degraded" but main health endpoint still returns 200
- **AND** degraded services are listed separately for alerting

### Requirement: AI Service Logging and Debugging
The system SHALL log comprehensive information about AI requests and responses for troubleshooting.

#### Scenario: Detailed AI request logging
- **WHEN** system sends request to Together AI
- **THEN** logs "AI completion request" with model name, prompt length, max_tokens
- **AND** if request fails, logs full error details including status code, error type, response body
- **AND** logs do not include sensitive user data or full prompts (only metadata)

#### Scenario: AI response metrics logging
- **WHEN** system receives successful response from Together AI
- **THEN** logs "AI completion success" with model, tokens used, latency_ms
- **AND** includes cost estimate based on tokens (if available)
- **AND** logs cache hit/miss status for monitoring cache effectiveness

#### Scenario: Debug mode for AI service
- **WHEN** environment variable `DEBUG_AI=1` is set
- **THEN** system logs full prompts and responses (sanitized) to debug log file
- **AND** debug logs include request/response headers
- **AND** debug logs help diagnose prompt engineering and response parsing issues
