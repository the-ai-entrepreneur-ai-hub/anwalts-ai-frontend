## ADDED Requirements

### Requirement: Admin-Only Navigation Items
The system SHALL conditionally display navigation items based on user role, ensuring non-admin users do not see admin-only features in the navigation sidebar.

#### Scenario: Admin user sees Settings navigation
- **GIVEN** a user with admin email (test.reg.e2e+20251026@anwalts.ai or angelageneralao.1997@gmail.com)
- **WHEN** they view the portal navigation sidebar
- **THEN** the Settings navigation link SHALL be visible
- **AND** clicking the Settings link SHALL navigate to the settings page successfully

#### Scenario: Non-admin user does not see Settings navigation
- **GIVEN** a user with non-admin email (any email not in admin list)
- **WHEN** they view the portal navigation sidebar
- **THEN** the Settings navigation link SHALL NOT be visible
- **AND** all other navigation links (Dashboard, Assistant, Documents, Templates, Email) SHALL remain visible

#### Scenario: Non-admin user attempts direct URL access
- **GIVEN** a user with non-admin email
- **WHEN** they navigate directly to `/settings` via URL
- **THEN** the settings page SHALL display "Access Denied" message
- **AND** the user SHALL be able to navigate back to Dashboard
- **NOTE**: This maintains defense-in-depth security at both navigation and page levels

#### Scenario: Admin check is case-insensitive
- **GIVEN** the admin email "angelageneralao.1997@gmail.com" is in the admin list
- **WHEN** a user logs in with "ANGELAGENERALAO.1997@GMAIL.COM" (uppercase)
- **THEN** the system SHALL recognize them as admin
- **AND** the Settings navigation link SHALL be visible
- **NOTE**: Email comparison uses lowercase normalization in useAuth composable

### Requirement: Navigation Component Integration
The PortalShell component SHALL integrate with the authentication composable to determine user roles and conditionally render navigation items.

#### Scenario: PortalShell uses useAuth composable
- **GIVEN** the PortalShell component is rendered
- **WHEN** the component initializes
- **THEN** it SHALL call useAuth() composable
- **AND** it SHALL extract the isAdmin computed property
- **AND** it SHALL use isAdmin to conditionally render admin-only navigation items

#### Scenario: Navigation renders without errors
- **GIVEN** a user logs in (admin or non-admin)
- **WHEN** the PortalShell component renders
- **THEN** there SHALL be no JavaScript errors in the console
- **AND** there SHALL be no visual flashing or layout shifts
- **AND** the navigation SHALL render smoothly with correct items visible
