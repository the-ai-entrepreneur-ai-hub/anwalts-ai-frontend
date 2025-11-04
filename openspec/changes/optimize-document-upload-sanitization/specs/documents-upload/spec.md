## ADDED Requirements
### Requirement: Sanitized Upload Pipeline
Uploaded documents MUST be processed through the PII sanitizer before any textual content is persisted or returned by backend APIs.

#### Scenario: Redacted text stored for downstream use
- **GIVEN** a signed-in user uploads a document containing email addresses, phone numbers, or IBANs
- **WHEN** the backend finishes processing the upload
- **THEN** the stored text excerpt and the response payload MUST contain the sanitized tokens (e.g., `[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, `[REDACTED_IBAN]`) instead of the raw values

#### Scenario: Subsequent reads reuse sanitized output
- **GIVEN** the same upload id is requested again for preview or prompt generation
- **WHEN** the backend serves the request
- **THEN** it MUST return the previously sanitized text without re-reading raw bytes, completing within 200 ms for files ≤10 MB

### Requirement: Documents UI Clears Upload State
The Documents page MUST accurately reflect sanitized uploads and allow users to clear the state without manual refreshes.

#### Scenario: Sanitized preview is shown after upload
- **GIVEN** a user drops a file with personal data into the Documents upload control
- **WHEN** the upload completes
- **THEN** the UI MUST render the sanitized preview returned by the backend and indicate that sensitive data was redacted

#### Scenario: "Empty All" resets document composition
- **GIVEN** a sanitized upload has populated the preview and metadata
- **WHEN** the user triggers the "Empty All" action
- **THEN** the file input, cached upload id/metadata, preview content, and AI prompt context MUST all reset to an empty state, removing any residual sanitized or raw text from the composer

### Requirement: Upload Performance Safeguards
Upload processing MUST stay within the existing latency budget while sanitizing content.

#### Scenario: Typical legal document upload
- **GIVEN** a text, PDF, or DOCX upload up to 10 MB with common German legal formatting
- **WHEN** the upload pipeline completes
- **THEN** the end-to-end response time MUST remain ≤2 seconds in nominal conditions and log a warning if the sanitizer adds more than 300 ms of overhead
