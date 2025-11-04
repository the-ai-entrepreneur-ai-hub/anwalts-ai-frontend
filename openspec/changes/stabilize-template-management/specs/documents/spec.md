## ADDED Requirements

### Requirement: Documents Page Applies Templates Idempotently
The Documents workflow MUST allow users to pick, clear, and reapply templates (including those created moments ago) without stale state or empty renders.

#### Scenario: Reapply after clear
- **GIVEN** a user selects a template from the inline list and sees the fields prefilled
- **WHEN** they click “Leeren” and then choose the same template again
- **THEN** the form repopulates and `template_id`/`template_content` are set for the next generation request

#### Scenario: Return from Templates page
- **GIVEN** a user creates or edits a template in `/templates`
- **WHEN** they click “Verwenden” to navigate back to `/documents`
- **THEN** the inline list refreshes from `/api/templates`
- **AND** the handed-off template is applied even if the catalog was previously cached

#### Scenario: Catalog refresh on failure
- **GIVEN** a template apply attempt fails because the entry no longer exists
- **WHEN** the user toggles “Alle Vorlagen”
- **THEN** the page refetches the catalog, removes the stale entry, and keeps the toggle responsive
