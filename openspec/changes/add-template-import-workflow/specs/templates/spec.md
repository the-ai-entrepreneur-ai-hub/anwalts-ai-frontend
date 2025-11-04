## ADDED Requirements

### Requirement: Template modal respects design sizing.
The create/edit template modal MUST render with consistent width, padding, and scroll handling across desktop and mobile so that inputs are never cropped or squashed.

#### Scenario: Desktop modal
- GIVEN the user clicks “Neue Vorlage” on a desktop viewport (≥ 1024px)
- WHEN the modal opens
- THEN the shell width is at least 640px and no more than 840px
- AND the form fields are fully visible with internal scrolling for overflow

#### Scenario: Mobile modal
- GIVEN the viewport is ≤ 640px
- WHEN the modal opens
- THEN it anchors to the bottom sheet style with rounded top corners
- AND vertical scrolling keeps the primary action buttons accessible

### Requirement: Import creates templates from uploaded documents.
The Templates page MUST let users import a document, have the backend extract its contents with AI assistance, and insert the resulting template into the catalogue list.

#### Scenario: Successful import
- GIVEN the user clicks “Importieren” and selects a supported file (PDF, DOCX, TXT)
- WHEN the backend finishes processing the upload
- THEN the UI shows a success message
- AND the new template (title + generated content) appears at the top of the grid without a manual refresh

#### Scenario: Unsupported or oversized file
- GIVEN the user selects a file over the size limit or with an unsupported type
- WHEN the backend rejects the upload
- THEN the UI surfaces a descriptive error toast
- AND no partial template is created

#### Scenario: AI generation failure
- GIVEN the upload succeeds but the AI service times out or returns empty content
- WHEN the import endpoint responds with an error
- THEN the frontend informs the user that the import failed and keeps the original catalogue unchanged
