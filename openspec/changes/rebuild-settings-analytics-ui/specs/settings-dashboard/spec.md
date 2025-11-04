# Settings Dashboard Specification Delta

## MODIFIED Requirements

### Requirement: Analytics Tab Visual Layout
The Analytics & Metrics tab SHALL display system metrics in a visually organized layout with clear spacing between sections.

#### Scenario: Admin views Analytics tab on desktop
- **GIVEN** an admin user is logged in
- **AND** the user navigates to Settings → Analytics & Metriken
- **WHEN** the page loads
- **THEN** four sections render with 40px spacing between them
- **AND** all cards are visually distinct and separated
- **AND** no console errors appear

### Requirement: KPI Cards Section
The KPI Cards section SHALL display four key performance indicators in a responsive grid.

#### Scenario: Desktop view shows 4 columns
- **GIVEN** viewport width is 1440px
- **WHEN** admin views Analytics tab
- **THEN** four KPI cards render in single row
- **AND** 24px gap between adjacent cards

### Requirement: System Health Section
The System Health section SHALL display status of four critical services with color-coded indicators.

#### Scenario: Services show operational status
- **GIVEN** services return healthy status
- **WHEN** admin views Analytics tab
- **THEN** service cards have green borders for operational
- **AND** service cards have red borders for disruptions

## ADDED Requirements

### Requirement: Browser Cache Invalidation
The Settings page SHALL force browsers to load latest CSS on every deployment.

#### Scenario: User has old CSS cached
- **GIVEN** user previously visited Settings page
- **AND** old CSS is cached in browser
- **WHEN** new version is deployed with updated CSS
- **AND** user navigates to Settings page
- **THEN** browser fetches new CSS file
- **AND** new styles apply immediately

### Requirement: Loading State Consistency
Loading skeletons SHALL maintain exact layout and spacing as actual content.

#### Scenario: Skeletons match final layout
- **GIVEN** page is loading data
- **WHEN** skeleton loaders render
- **THEN** skeleton cards have same dimensions as real cards
- **AND** 40px spacing between skeleton sections
- **AND** no layout shift occurs when real data loads

### Requirement: Accessibility Compliance
The Settings Analytics tab SHALL meet WCAG 2.1 Level AA standards.

#### Scenario: Screen reader navigation
- **GIVEN** user is using screen reader
- **WHEN** user navigates to Analytics tab
- **THEN** screen reader announces section headings correctly
- **AND** cards have semantic HTML structure
- **AND** status indicators have aria-labels

### Requirement: Performance Optimization
The Settings Analytics tab SHALL load and render within performance budgets.

#### Scenario: Page load performance
- **GIVEN** user on average broadband connection
- **WHEN** user navigates to Analytics tab
- **THEN** First Contentful Paint occurs within 1 second
- **AND** Cumulative Layout Shift score is less than 0.1
- **AND** page is fully interactive within 2 seconds

## REMOVED Requirements

### Requirement: Flexbox Gap Usage
**Reason:** Inconsistent browser support and rendering issues  
**Migration:** Replaced with margin-based spacing

### Requirement: Tailwind Utility Classes
**Reason:** Conflicts with custom CSS causing missing styles  
**Migration:** All utilities converted to scoped CSS classes
