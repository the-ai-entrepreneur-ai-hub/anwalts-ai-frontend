# Frontend Styling Specification Deltas

## MODIFIED Requirements

### Requirement: Frontend Build Process
The frontend build process SHALL occur within the Docker container using a multi-stage build pattern, ensuring consistent CSS generation across all environments.

#### Scenario: Build in Docker container
- **WHEN** Docker image is built
- **THEN** all dependencies (including devDependencies) SHALL be installed in builder stage
- **AND** application SHALL be built in builder stage
- **AND** built output SHALL be copied to runtime stage
- **AND** runtime stage SHALL contain only production dependencies

#### Scenario: Consistent CSS output
- **WHEN** application is built in any environment
- **THEN** generated CSS SHALL be identical
- **AND** all Tailwind utilities SHALL be present
- **AND** CSS SHALL not contain calc(var(--spacing)) patterns

### Requirement: Tailwind Spacing Configuration
The Tailwind CSS configuration SHALL define a complete spacing scale in the theme, eliminating the need for CSS variable workarounds.

#### Scenario: Spacing scale defined
- **WHEN** Tailwind config is loaded
- **THEN** spacing scale SHALL include values: 0, 0.5, 1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24
- **AND** all spacing values SHALL use rem units
- **AND** spacing SHALL follow Tailwind's standard scale

#### Scenario: Gap utilities generated correctly
- **WHEN** CSS is generated
- **THEN** gap-6 utility SHALL have value "gap: 1.5rem"
- **AND** gap-12 utility SHALL have value "gap: 3rem"
- **AND** gap utilities SHALL NOT use calc() functions
- **AND** gap utilities SHALL NOT depend on CSS variables

### Requirement: CSS File Organization
Custom CSS files SHALL contain only project-specific styles and SHALL NOT define utility classes that conflict with Tailwind.

#### Scenario: Tailwind CSS file clean
- **WHEN** tailwind.css is loaded
- **THEN** file SHALL only contain @import 'tailwindcss'
- **AND** file SHALL NOT define --spacing CSS variable
- **AND** all configuration SHALL come from tailwind.config.ts

#### Scenario: Main CSS file clean
- **WHEN** main.css is loaded
- **THEN** file SHALL contain only custom component styles
- **AND** file SHALL contain project-specific CSS variables
- **AND** file SHALL NOT define utility classes like .gap-12
- **AND** file SHALL NOT override Tailwind utilities

## REMOVED Requirements

### Requirement: CSS Variable Spacing System
**Reason**: Replaced by proper Tailwind theme configuration

**Migration**: Remove `:root { --spacing: 0.25rem; }` from tailwind.css

This requirement used CSS variables as a workaround for missing Tailwind spacing configuration. With proper theme configuration, CSS variables are no longer needed and create fragility.

### Requirement: Custom Gap Utilities in main.css
**Reason**: Conflicts with Tailwind's gap utilities

**Migration**: Remove `.gap-12 { gap: 12px; }` and similar utilities from main.css. Use Tailwind's gap-3 (12px) or gap-12 (48px) instead.

This requirement created conflicts where custom utilities overrode Tailwind's utilities, causing unpredictable behavior.

## ADDED Requirements

### Requirement: Docker Multi-Stage Build
The Dockerfile SHALL use a multi-stage build pattern with separate builder and runtime stages.

#### Scenario: Builder stage setup
- **WHEN** Docker image is built
- **THEN** builder stage SHALL use node:20-alpine base image
- **AND** builder stage SHALL install all dependencies via npm ci
- **AND** builder stage SHALL copy all source files
- **AND** builder stage SHALL run npm run build

#### Scenario: Runtime stage setup
- **WHEN** Docker image is built
- **THEN** runtime stage SHALL use node:20-alpine base image
- **AND** runtime stage SHALL install only production dependencies
- **AND** runtime stage SHALL copy .output directory from builder stage
- **AND** runtime stage SHALL copy public directory from builder stage
- **AND** runtime stage SHALL NOT contain devDependencies or build tools

#### Scenario: Build consistency
- **WHEN** same source code is built multiple times
- **THEN** generated Docker image SHALL produce identical CSS output
- **AND** build process SHALL be reproducible in CI/CD environments
- **AND** build SHALL NOT depend on host machine state

### Requirement: Build Validation (Optional)
The build process MAY include validation scripts to verify CSS output correctness.

#### Scenario: CSS validation
- **WHEN** build validation script is run
- **THEN** script SHALL check for presence of required Tailwind utilities
- **AND** script SHALL check for absence of problematic patterns
- **AND** script SHALL return non-zero exit code if validation fails

#### Scenario: Automated validation
- **WHEN** npm run build:validate is executed
- **THEN** application SHALL be built
- **AND** validation script SHALL run automatically
- **AND** build SHALL fail if CSS validation fails
