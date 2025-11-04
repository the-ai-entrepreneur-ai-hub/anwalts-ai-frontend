## ADDED Requirements

### Requirement: Header status cards summarise mandate state
- The Documents page MUST display two hero cards (“Qualitätsscore” and “PDF-Export”) that follow a consistent structure, surface live drafting metrics, and guide the lawyer toward the next action.

#### Scenario: Lawyer opens Documents page before generating any draft
- GIVEN the lawyer has no generated preview in the current session
- WHEN the Documents page loads
- THEN the quality card shows the badge “Entwurf ausstehend”, a neutral headline metric, and explains that texts update once a draft exists
- AND the export card presents a prompt to generate a draft before export

#### Scenario: Lawyer generates a document draft with clauses
- GIVEN a draft preview is available
- AND at least one clause has been selected
- WHEN the page renders the header cards
- THEN the quality card lists the live word count and clause coverage
- AND the export card conveys that the draft is export-ready with the latest status message from the processing banner

#### Scenario: Generation reports an error
- GIVEN the most recent generation attempt failed
- WHEN the header cards render
- THEN the quality card signals attention is required (error tone, short explanation)
- AND the export card asks the lawyer to retry the generation rather than offering a download prompt
