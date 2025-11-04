## ADDED Requirements

### Requirement: Document Preview Shows Processing Feedback
The documents workspace MUST display a visible progress indicator inside the preview container while a generation or submission request is in-flight, and update the status once the backend responds.

#### Scenario: Spinner visible during generation
- **GIVEN** the user clicks “Dokument erzeugen” or “Zur Verarbeitung senden”
- **WHEN** the frontend awaits the backend response
- **THEN** an animated indicator with copy such as “Dokument wird erstellt …” appears within the preview pane
- **AND** the indicator hides once real document content is rendered

#### Scenario: Success status replaces spinner
- **GIVEN** the backend returns generated content
- **WHEN** the preview updates
- **THEN** the status text switches to success messaging (e.g., “Dokument aktualisiert”) without removing existing styling
- **AND** the toolbar actions (copy, feedback, edit, download) become active based on the saved document id

### Requirement: Generation Pipeline Uses Sanitized Inputs
Document generation MUST pass user instructions and uploaded excerpts through the PIWI sanitizer before invoking Together AI, and surface the sanitized metadata in the response for preview display.

#### Scenario: Sanitized instructions forwarded
- **GIVEN** the user enters instructions and/or uploads a document
- **WHEN** a generation request is processed
- **THEN** the backend sanitizes the inputs via PIWI before calling Together AI
- **AND** the response metadata includes the sanitized text so the preview can show what was retained

#### Scenario: Sanitizer failure surfaces error
- **GIVEN** the sanitizer fails or rejects the content
- **WHEN** the generation call finishes
- **THEN** the frontend shows an inline error message while keeping the existing layout intact
- **AND** backend logs include the sanitizer failure for diagnostics
