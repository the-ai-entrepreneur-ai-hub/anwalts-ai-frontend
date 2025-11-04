# AI Email Processing Spec

## ADDED Requirements

### Requirement: Email AI Processing Endpoint
The system SHALL provide an API endpoint to process emails with AI for summarization, categorization, and draft response generation.

#### Scenario: Process email request
- **WHEN** user clicks "Generate AI Summary" on email detail view
- **THEN** system calls POST /api/email/process with email ID
- **AND** endpoint verifies user has Gmail connected
- **AND** fetches full email body from Gmail API
- **AND** extracts plain text content from HTML if needed
- **AND** calls legal-rag-api with email content
- **AND** returns AI-generated summary, category, and draft response
- **AND** caches result in database to avoid re-processing

#### Scenario: Already processed email
- **WHEN** email has been previously processed
- **THEN** system returns cached AI processing results immediately
- **AND** skips legal-rag-api call to save quota
- **AND** displays cache timestamp "Processed X minutes ago"

#### Scenario: Processing timeout
- **WHEN** legal-rag-api takes longer than 30 seconds
- **THEN** system returns 504 Gateway Timeout
- **AND** shows error message "AI processing timed out, try again"
- **AND** does not cache failed result

#### Scenario: AI service unavailable
- **WHEN** legal-rag-api is unreachable or returns 500 error
- **THEN** system returns graceful error "AI service temporarily unavailable"
- **AND** logs error for monitoring
- **AND** email remains viewable without AI features

### Requirement: Email Summarization
The system SHALL generate concise summaries of email content using AI model.

#### Scenario: Contract email summary
- **WHEN** email contains contract review content
- **THEN** AI generates 2-3 sentence summary focusing on:
- Key contractual terms mentioned
- Action items or deadlines
- Priority level assessment
- **AND** summary is displayed in AI Summary section of email detail view

#### Scenario: Termination email summary
- **WHEN** email contains termination/severance content
- **THEN** AI generates summary highlighting:
- Type of termination (voluntary, involuntary)
- Important dates and deadlines
- Required documentation
- **AND** flags high priority if urgent action needed

#### Scenario: Reminder email summary
- **WHEN** email contains appointment or deadline reminder
- **THEN** AI extracts:
- Event date and time
- Location or meeting details
- Participants mentioned
- **AND** formats as structured summary

#### Scenario: General legal email summary
- **WHEN** email doesn't match specific category
- **THEN** AI generates general summary covering:
- Main topic or issue discussed
- Any mentioned parties or cases
- Requested actions or responses
- **AND** provides context for legal relevance

### Requirement: Email Categorization
The system SHALL automatically categorize emails based on content analysis using AI and keyword detection.

#### Scenario: Contract categorization
- **WHEN** email subject or body contains keywords: "contract", "agreement", "vertrag", "vereinbarung"
- **THEN** system assigns type = "Contracts"
- **AND** displays green category badge
- **AND** may include AI-detected sub-categories (NDA, employment contract, etc.)

#### Scenario: Termination categorization
- **WHEN** email contains keywords: "termination", "severance", "kündigung", "kündigungsvereinbarung"
- **THEN** system assigns type = "Terminations"
- **AND** displays red category badge
- **AND** flags as high priority

#### Scenario: Reminder categorization
- **WHEN** email contains keywords: "reminder", "appointment", "deadline", "erinnerung", "termin"
- **THEN** system assigns type = "Reminders"
- **AND** displays blue category badge
- **AND** extracts deadline/appointment date if present

#### Scenario: Court document categorization
- **WHEN** email sender domain is .gov or contains "court", "gericht"
- **THEN** system assigns type = "Court"
- **AND** displays purple category badge
- **AND** marks as high priority

#### Scenario: Client categorization
- **WHEN** email is from known client domain or contains client reference
- **THEN** system adds "Client" label
- **AND** associates with client record if exists
- **AND** applies client-specific handling rules

### Requirement: Draft Response Generation
The system SHALL generate professional draft email responses based on email content and context.

#### Scenario: Contract review response draft
- **WHEN** email requests contract review
- **THEN** AI generates draft response:
- Professional greeting
- Acknowledgment of contract review request
- Estimated timeline for review
- Request for any additional context needed
- Professional closing
- **AND** draft is editable before sending

#### Scenario: Information request response draft
- **WHEN** email asks legal questions
- **THEN** AI generates draft response:
- Acknowledgment of inquiry
- Brief answer or next steps
- Request for consultation if complex
- Disclaimer if needed
- **AND** flags areas needing manual review

#### Scenario: Appointment confirmation draft
- **WHEN** email proposes meeting or appointment
- **THEN** AI generates draft response:
- Confirmation or alternative time proposal
- Meeting details confirmation
- Agenda items if applicable
- Contact information
- **AND** integrates with calendar context

#### Scenario: Response tone matching
- **WHEN** generating draft response
- **THEN** AI matches formality level of original email
- **AND** uses appropriate legal terminology for context
- **AND** maintains professional tone throughout
- **AND** includes user's signature from profile

### Requirement: AI Processing Rate Limiting
The system SHALL enforce rate limits on AI email processing to prevent abuse and control costs.

#### Scenario: Within rate limit
- **WHEN** user requests AI processing
- **THEN** system checks rate limit counter (20 requests/hour/user)
- **AND** if under limit, processes request and increments counter
- **AND** returns AI results normally

#### Scenario: Rate limit exceeded
- **WHEN** user exceeds 20 AI processing requests in 1 hour
- **THEN** system returns 429 Too Many Requests
- **AND** shows error message "AI processing limit reached (20/hour)"
- **AND** displays time remaining until limit resets
- **AND** cached results still accessible

#### Scenario: Rate limit reset
- **WHEN** rate limit window expires (1 hour)
- **THEN** system resets counter to 0
- **AND** user can process emails again
- **AND** logs rate limit usage for monitoring

### Requirement: AI Result Storage
The system SHALL store AI processing results for reuse and audit purposes.

#### Scenario: Store processing result
- **WHEN** AI successfully processes email
- **THEN** system stores in email_processing_results table:
- user_id (FK to users)
- email_id (Gmail message ID)
- summary (text)
- category (string)
- draft_response (text)
- processed_at (timestamp)
- model_version (string)
- **AND** indexes on user_id and email_id for fast lookup

#### Scenario: Retrieve cached result
- **WHEN** user views previously processed email
- **THEN** system queries email_processing_results by user_id and email_id
- **AND** returns cached summary, category, and draft
- **AND** skips legal-rag-api call
- **AND** shows "AI processed on [date]" timestamp

#### Scenario: Reprocess email
- **WHEN** user clicks "Regenerate AI Summary" on cached result
- **THEN** system deletes old processing result
- **AND** calls legal-rag-api again with email content
- **AND** stores new result with updated timestamp
- **AND** displays new AI output

### Requirement: AI Consent Management
The system SHALL respect user consent settings for AI email processing.

#### Scenario: AI consent granted
- **WHEN** user has checked "AI can read my emails" in settings
- **THEN** system enables AI summary buttons on emails
- **AND** allows AI processing requests
- **AND** displays AI-generated content in UI

#### Scenario: AI consent not granted
- **WHEN** user has not granted AI reading consent
- **THEN** system hides AI summary buttons
- **AND** returns 403 Forbidden on AI processing requests
- **AND** shows message "Enable AI reading in settings to use this feature"

#### Scenario: Revoke AI consent
- **WHEN** user unchecks "AI can read my emails" in settings
- **THEN** system updates user_profiles.data['ai_read_consent'] = False
- **AND** hides AI features in email UI
- **AND** preserves existing AI processing results (not deleted)
- **AND** prevents new AI processing requests

#### Scenario: Consent timestamp tracking
- **WHEN** user grants AI consent
- **THEN** system records user_profiles.data['ai_consent_timestamp']
- **AND** displays consent date in settings
- **AND** includes in audit logs for compliance

### Requirement: AI Quality Indicators
The system SHALL display quality indicators and confidence levels for AI-generated content.

#### Scenario: High confidence summary
- **WHEN** AI generates summary with high confidence
- **THEN** system displays "AI Summary" badge without warnings
- **AND** shows full summary text
- **AND** allows direct use in workflow

#### Scenario: Low confidence warning
- **WHEN** AI confidence score is below threshold (if available)
- **THEN** system displays warning icon with tooltip
- **AND** shows message "AI summary may need review"
- **AND** recommends manual verification

#### Scenario: AI-generated content labeling
- **WHEN** displaying any AI-generated text
- **THEN** system clearly labels with "AI-generated" tag
- **AND** uses distinct visual styling (light blue background)
- **AND** includes disclaimer "Review before using in legal work"

#### Scenario: Draft response disclaimer
- **WHEN** displaying draft response
- **THEN** system shows prominent notice:
- "This is an AI-generated draft. Review and edit before sending."
- **AND** requires explicit "Edit Draft" action before use
- **AND** never sends draft automatically

### Requirement: AI Processing Logging
The system SHALL log all AI processing activities for audit and quality improvement.

#### Scenario: Processing request logging
- **WHEN** AI processing request is made
- **THEN** system logs to ai_processing_log table:
- user_id
- email_id
- request_timestamp
- processing_duration_ms
- success (boolean)
- error_message (if failed)
- model_version
- **AND** includes in weekly quality reports

#### Scenario: Processing failure logging
- **WHEN** AI processing fails
- **THEN** system logs error details:
- Error type (timeout, model error, network error)
- Partial response if available
- Request parameters
- **AND** alerts on high failure rate (>10%)
- **AND** includes in debugging reports

#### Scenario: Quality metrics tracking
- **WHEN** processing completes successfully
- **THEN** system tracks metrics:
- Average processing time per email type
- Cache hit rate
- User satisfaction (if feedback provided)
- Model version performance
- **AND** generates weekly quality dashboard
