## ADDED Requirements

### Requirement: Top Horizontal Navigation Bar

The email interface SHALL provide a horizontal top navigation bar that contains primary email controls and branding.

#### Scenario: Desktop top bar display
- **WHEN** user accesses the email page on desktop (≥1024px width)
- **THEN** the top bar SHALL display:
  - Email section logo/title on the left
  - Search input in the center
  - Compose button on the right
  - All elements in a single horizontal row

#### Scenario: Mobile top bar display
- **WHEN** user accesses the email page on mobile (<768px width)
- **THEN** the top bar SHALL display:
  - Hamburger menu icon on the left
  - Email section title in the center
  - Compose button icon on the right

### Requirement: Horizontal Folder Tabs Navigation

The email interface SHALL replace the left sidebar with horizontal folder tabs positioned below the top bar.

#### Scenario: Folder tabs on desktop
- **WHEN** user views email page on desktop
- **THEN** folder tabs (Posteingang, Markiert, Gesendet, Entwürfe, Papierkorb) SHALL be displayed horizontally
- **AND** each tab SHALL show folder icon, label, and unread count badge
- **AND** active folder SHALL be visually highlighted

#### Scenario: Folder selection
- **WHEN** user clicks on a folder tab
- **THEN** the email list SHALL update to show emails from that folder
- **AND** the tab SHALL be marked as active with visual indicator

#### Scenario: Mobile folder navigation
- **WHEN** user opens hamburger menu on mobile
- **THEN** folders SHALL be displayed in a vertical drawer menu
- **AND** selecting a folder SHALL close the drawer and update email list

### Requirement: Labels Filter Management

The email interface SHALL provide label filtering through a dropdown or chip-based interface.

#### Scenario: Label dropdown access
- **WHEN** user clicks on "Labels" dropdown in the navigation bar
- **THEN** a dropdown menu SHALL display all available labels
- **AND** each label SHALL show name, color indicator, and count

#### Scenario: Label filter application
- **WHEN** user selects a label from the dropdown
- **THEN** the email list SHALL filter to show only emails with that label
- **AND** the active label SHALL be displayed as a chip/badge in the UI
- **AND** user SHALL be able to clear the filter

### Requirement: Full-Width Email List Layout

The email interface SHALL utilize the full viewport width for displaying the email list, without left sidebar constraints.

#### Scenario: Email list on widescreen
- **WHEN** user views email list on widescreen display (≥1440px)
- **THEN** email list SHALL expand to use available horizontal space
- **AND** email subject lines SHALL display more text before truncation
- **AND** all columns (checkbox, star, sender, subject, preview, timestamp) SHALL be visible

#### Scenario: Email list responsive scaling
- **WHEN** viewport width decreases
- **THEN** email list SHALL responsively adjust
- **AND** less important columns SHALL hide on smaller screens
- **AND** email items SHALL remain readable and clickable

### Requirement: Compact Email Modal Action Buttons

The email detail modal SHALL display action buttons in a compact, icon-first format similar to Gmail.

#### Scenario: Modal footer on desktop
- **WHEN** user opens an email in the detail modal
- **THEN** the modal footer SHALL display compact action buttons
- **AND** buttons SHALL be maximum 36px height with 8px-16px padding
- **AND** icons SHALL be 18px size with text labels
- **AND** buttons SHALL be: Antworten (primary), Weiterleiten, Archivieren, Löschen

#### Scenario: Primary action emphasis
- **WHEN** modal footer is displayed
- **THEN** "Antworten" button SHALL have primary styling (colored background)
- **AND** other action buttons SHALL have subtle secondary styling
- **AND** destructive action (Löschen) SHALL have danger color on hover

#### Scenario: Action button interactions
- **WHEN** user hovers over an action button
- **THEN** button SHALL display subtle background color change
- **AND** tooltip SHALL appear with full action description
- **AND** cursor SHALL change to pointer

### Requirement: Removal of Navigation Duplication

The email interface SHALL NOT display duplicate navigation elements from PortalShell or other layouts.

#### Scenario: Email page layout isolation
- **WHEN** user navigates to the email page
- **THEN** PortalShell navigation SHALL NOT be rendered
- **AND** email-specific layout SHALL be used
- **AND** only email top bar and folder tabs SHALL be visible

#### Scenario: Return to dashboard navigation
- **WHEN** user wants to exit email section
- **THEN** a "Back to Dashboard" or "Dashboard" link SHALL be available in the top bar
- **AND** clicking it SHALL navigate to /dashboard
- **AND** no conflicting navigation elements SHALL be present

### Requirement: Responsive Email Interface

The email interface SHALL adapt seamlessly to desktop, tablet, and mobile screen sizes.

#### Scenario: Desktop layout (≥1024px)
- **WHEN** viewport width is ≥1024px
- **THEN** full horizontal folder tabs SHALL be displayed
- **AND** search bar SHALL be full-width in top bar
- **AND** email list SHALL show all columns
- **AND** labels SHALL be in dropdown

#### Scenario: Tablet layout (768px-1023px)
- **WHEN** viewport width is between 768px and 1023px
- **THEN** folder tabs SHALL be compressed or in dropdown
- **AND** search bar SHALL be condensed
- **AND** email sender column MAY be hidden
- **AND** email list SHALL remain scrollable

#### Scenario: Mobile layout (<768px)
- **WHEN** viewport width is <768px
- **THEN** hamburger menu SHALL be displayed
- **THEN** folders and labels SHALL be in drawer menu
- **AND** compose button SHALL be icon-only in top bar
- **AND** email list SHALL show simplified layout (subject + timestamp only)

### Requirement: Professional Visual Design

The email interface SHALL maintain a professional, clean visual design consistent with modern email clients.

#### Scenario: Color and typography consistency
- **WHEN** email interface is rendered
- **THEN** color palette SHALL match application's primary/secondary colors
- **AND** typography SHALL use consistent font family and sizes
- **AND** spacing SHALL follow design system guidelines (8px grid)

#### Scenario: Smooth transitions and interactions
- **WHEN** user interacts with UI elements (tabs, buttons, modals)
- **THEN** transitions SHALL be smooth with 150-300ms duration
- **AND** hover states SHALL be subtle and professional
- **AND** focus states SHALL be clearly visible for accessibility

#### Scenario: Visual hierarchy
- **WHEN** email list is displayed
- **THEN** unread emails SHALL be visually distinct (bold, background color)
- **AND** starred emails SHALL show filled star icon
- **AND** priority emails SHALL have visual indicator
- **AND** email preview text SHALL be lighter color than subject

## MODIFIED Requirements

### Requirement: Email Controls Bar

The email controls bar SHALL be integrated into the horizontal navigation area, not as a separate bar below the sidebar.

#### Scenario: Controls bar positioning
- **WHEN** user views the email list
- **THEN** action controls (select all, bulk actions, sort) SHALL be below the folder tabs
- **AND** SHALL NOT be duplicated in multiple locations
- **AND** SHALL span full width of email content area

#### Scenario: Bulk action availability
- **WHEN** user selects one or more emails
- **THEN** bulk action buttons (Archive, Delete, Mark Read) SHALL become enabled
- **AND** buttons SHALL maintain compact size (30px height)
- **AND** selected count SHALL be displayed

## REMOVED Requirements

### Requirement: Left Sidebar Folder Navigation

**Reason**: Replaced with horizontal top navigation for better screen space utilization and Gmail-like UX

**Migration**: 
- All folder navigation functionality moved to horizontal tabs below top bar
- Label navigation moved to dropdown or filter chips
- No data migration needed - purely UI change

### Requirement: PortalShell Wrapper for Email Page

**Reason**: Creates duplicate navigation and constrains email-specific layout needs

**Migration**:
- Email page will use dedicated email layout instead of PortalShell
- Back-to-dashboard link added to email top bar
- User authentication and session management unchanged
