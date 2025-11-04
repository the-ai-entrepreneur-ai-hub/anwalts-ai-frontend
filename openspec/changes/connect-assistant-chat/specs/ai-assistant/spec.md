## ADDED Requirements

### Requirement: Conversational AI Chat Interface

The system SHALL provide a conversational AI chat interface that allows authenticated users to interact with the trained Qwen legal AI model through natural language conversations on the `/assistant` page.

#### Scenario: User sends first message in new conversation
- **WHEN** authenticated user submits a message on the `/assistant` page without a conversation_id
- **THEN** the system generates a new conversation_id, saves the user message to the database, calls the AI model, saves the AI response to the database, and returns the response with conversation_id and message_id

#### Scenario: User sends follow-up message in existing conversation
- **WHEN** authenticated user submits a message with a conversation_id from a previous response
- **THEN** the system retrieves the last 5 messages from that conversation, includes them as context for the AI model, saves both the user message and AI response to the database linked to the same conversation_id, and returns the response

#### Scenario: User sends message without authentication
- **WHEN** unauthenticated user attempts to submit a message
- **THEN** the system returns a 401 Unauthorized error and the frontend redirects to the login page

### Requirement: Conversation Persistence

The system SHALL persist all user messages and AI responses to the `assistant_messages` database table with proper user_id and conversation_id linkage.

#### Scenario: Message saved before AI generation
- **WHEN** user submits a message
- **THEN** the system saves the user message to the database immediately before calling the AI service, ensuring no message loss even if AI generation fails

#### Scenario: AI response saved after successful generation
- **WHEN** AI service successfully generates a response
- **THEN** the system saves the AI response to the database linked to the same conversation_id as the user message

#### Scenario: Conversation history retrieval
- **WHEN** backend processes a message with a conversation_id
- **THEN** the system retrieves the last 5 messages from that conversation ordered by created_at ASC and includes them in the AI context

### Requirement: Rate Limiting

The system SHALL implement rate limiting to prevent abuse of the AI chat service, limiting users to 10 messages per minute.

#### Scenario: User within rate limit
- **WHEN** authenticated user has sent fewer than 10 messages in the current minute
- **THEN** the system processes the message normally and increments the message counter in Redis with 60-second TTL

#### Scenario: User exceeds rate limit
- **WHEN** authenticated user attempts to send an 11th message within the same minute
- **THEN** the system returns a 429 Too Many Requests error with German message "Sie haben das Nachrichtenlimit überschritten. Bitte warten Sie einen Moment." and does not call the AI service

#### Scenario: Rate limit resets after 60 seconds
- **WHEN** 60 seconds have elapsed since the rate limit was triggered
- **THEN** the Redis counter expires and the user can send messages again

### Requirement: Conversation Context Management

The system SHALL provide relevant conversation context to the AI model for multi-turn conversations by including recent message history.

#### Scenario: Context formatting for AI
- **WHEN** backend prepares context for AI model
- **THEN** the system formats the last 5 messages as "User: {message content}\n\nAssistant: {response content}\n\n" and passes this formatted string to the AI service as context

#### Scenario: New conversation with no context
- **WHEN** user starts a new conversation (no conversation_id provided)
- **THEN** the system calls the AI service with the user message as prompt and empty context

#### Scenario: Context length limitation
- **WHEN** conversation has more than 5 messages
- **THEN** the system only includes the last 5 messages to limit token usage and maintain performance

### Requirement: Error Handling

The system SHALL provide graceful error handling with user-friendly German error messages for all failure scenarios.

#### Scenario: AI service unavailable
- **WHEN** AI service fails to respond or returns an error
- **THEN** the system saves the user message to the database, logs the detailed error, and returns a 503 error with message "Ich konnte die Antwort gerade nicht fertigstellen. Bitte stellen Sie Ihre Frage gleich noch einmal – ich helfe sofort weiter."

#### Scenario: Invalid conversation_id
- **WHEN** user provides a conversation_id that doesn't exist or doesn't belong to them
- **THEN** the system returns a 404 error with message "Diese Konversation wurde nicht gefunden."

#### Scenario: Message exceeds maximum length
- **WHEN** user submits a message longer than 4000 characters
- **THEN** the system returns a 400 error with message "Ihre Nachricht ist zu lang. Maximal 4000 Zeichen erlaubt."

#### Scenario: Authentication token expired
- **WHEN** user's JWT token has expired
- **THEN** the system returns a 401 error and the frontend redirects to the landing page with re-login prompt

### Requirement: API Endpoint Contract

The system SHALL expose a `/api/assistant/chat` POST endpoint that accepts chat messages and returns AI responses with conversation metadata.

#### Scenario: Valid request format
- **WHEN** frontend sends POST request to `/api/assistant/chat`
- **THEN** the endpoint accepts JSON body with fields: message (required string), conversation_id (optional UUID string), model (optional string), max_tokens (optional integer), temperature (optional float)

#### Scenario: Response format
- **WHEN** endpoint successfully processes a message
- **THEN** the response includes: content (string), conversation_id (UUID string), message_id (UUID string), model (string), usage (object with token counts), generation_time_ms (integer)

#### Scenario: Authorization header required
- **WHEN** request is made to `/api/assistant/chat`
- **THEN** the endpoint requires "Authorization: Bearer {token}" header with valid JWT token

### Requirement: Frontend Integration

The system SHALL integrate the frontend assistant.vue component with the backend chat endpoint, managing conversation state and displaying responses.

#### Scenario: Send message with authentication token
- **WHEN** user submits a message on the `/assistant` page
- **THEN** the frontend retrieves the auth token from localStorage.getItem('auth_token'), includes it in the Authorization header, and sends the request to `/api/assistant/chat`

#### Scenario: Store conversation_id for follow-up messages
- **WHEN** frontend receives the first response from a new conversation
- **THEN** the component stores the conversation_id in local state and includes it in all subsequent messages

#### Scenario: Clear conversation state
- **WHEN** user clicks "Neue Anfrage" button
- **THEN** the frontend clears the message history, resets the conversation_id to null, and displays the welcome screen

#### Scenario: Display loading indicator
- **WHEN** frontend sends a message and waits for AI response
- **THEN** the component displays an animated loading indicator with "Analyse läuft..." text and typing dots

#### Scenario: Display error messages
- **WHEN** backend returns an error response
- **THEN** the frontend extracts the error message from the response and displays it as an assistant message in red/warning styling

### Requirement: Database Schema Utilization

The system SHALL use the existing `assistant_messages` table to store all conversation data without requiring schema migrations.

#### Scenario: Insert user message
- **WHEN** backend saves a user message
- **THEN** the system inserts a row with: id (UUID), conversation_id (UUID), user_id (UUID), role ('user'), content (text), model (null), message_hash (null), created_at (timestamp)

#### Scenario: Insert assistant message
- **WHEN** backend saves an AI response
- **THEN** the system inserts a row with: id (UUID), conversation_id (same as user message), user_id (same as user message), role ('assistant'), content (text), model (string, e.g., 'qwen_legal_q4_k_m'), message_hash (null), created_at (timestamp)

#### Scenario: Query conversation history
- **WHEN** backend retrieves conversation history
- **THEN** the system queries: SELECT * FROM assistant_messages WHERE conversation_id = $1 AND user_id = $2 ORDER BY created_at ASC LIMIT 5
