## ADDED Requirements

### Requirement: Templates catalog must appear before supporting rails on narrow viewports.
The Templates page MUST render the main catalog before highlight or recommendation rails on viewports at or below 960px, ensuring users immediately see available templates when browsing on tablet or mobile.

#### Scenario: Mobile user visits Templates
- **GIVEN** the viewport width is 600px
- **WHEN** the user opens `/templates`
- **THEN** the catalog list renders before side-rail content
- **AND** no horizontal scrolling is required to reach the card grid

### Requirement: Templates header controls adapt without overflow on tablet/mobile.
The header action buttons and search bar MUST stack responsively and remain fully visible at widths from 600px–960px.

#### Scenario: Tablet user sees search and actions stacked
- **GIVEN** the viewport width is 820px
- **WHEN** the user opens `/templates`
- **THEN** the search input spans the available width with action buttons wrapping beneath it
- **AND** no action button text is clipped or hidden

### Requirement: Template cards resize gracefully across breakpoints.
Template listing cards MUST collapse into one-column layout below 720px and avoid clipped content or horizontal overflow between 720px and 1280px.

#### Scenario: Narrow desktop shows two-column grid without overflow
- **GIVEN** the viewport width is 1100px
- **WHEN** the user views the catalog grid
- **THEN** the cards arrange into two columns with consistent gutter spacing
- **AND** the main column width remains at least 560px without horizontal scrolling

#### Scenario: Mobile collapses to single column
- **GIVEN** the viewport width is 480px
- **WHEN** the user views the catalog grid
- **THEN** the cards render as a single column that fits the viewport width
- **AND** card padding and typography remain legible
