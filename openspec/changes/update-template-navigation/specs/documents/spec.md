## ADDED Requirements

### Requirement: Documents page template controls must route users to the Templates page.
The Documents page MUST send users to the dedicated Templates route whenever they request the broader catalog, ensuring consistent discovery of reusable drafts.

#### Scenario: Authenticated user clicks toolbar “Vorlagen”
- GIVEN the user is on `/documents`
- WHEN the user activates the “Vorlagen” toolbar button
- THEN the app navigates to `/templates?origin=documents`
- AND the Templates page loads without client errors

#### Scenario: Inline “Alle Vorlagen” link is used
- GIVEN the inline templates quick-pick section is visible
- WHEN the user clicks the “Alle Vorlagen” link
- THEN the app navigates to `/templates?origin=documents`
- AND the Templates page shows the template catalog

### Requirement: Template selection still pre-fills the Documents form.
Templates chosen from the Templates page MUST continue handing content back to the Documents workflow without manual copy/paste.

#### Scenario: Template applied from Templates page after navigation
- GIVEN the user arrived on `/templates` from `/documents`
- AND the user clicks “Verwenden” for a template
- WHEN the app routes back to `/documents`
- THEN the corresponding template content is applied to the form fields
- AND the toolbar helper text confirms the template takeover
