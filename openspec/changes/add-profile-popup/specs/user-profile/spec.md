# User Profile Management Specification

## ADDED Requirements

### Requirement: Profile Avatar Display with Initials

The system SHALL display user avatars in the navigation sidebar with intelligent fallback logic.

#### Scenario: User has uploaded profile picture
- **WHEN** a user has uploaded a profile picture
- **THEN** the avatar displays the uploaded image
- **AND** the image is displayed at 40x40 pixels with rounded corners

#### Scenario: User has no profile picture
- **WHEN** a user has not uploaded a profile picture
- **AND** the user has a name set in their profile
- **THEN** the avatar displays the first letter of the user's first name
- **AND** the letter is centered and capitalized
- **AND** the avatar maintains the existing color scheme (gradient background)

#### Scenario: User has no profile picture and no name
- **WHEN** a user has neither profile picture nor name
- **THEN** the avatar displays a generic user icon
- **AND** the avatar maintains the existing color scheme

### Requirement: Interactive Profile Popup

The system SHALL provide an interactive profile popup that opens when users click on their profile section in the sidebar.

#### Scenario: Opening profile popup
- **WHEN** a user clicks on their profile section (avatar or name area) in the sidebar
- **THEN** a profile popup SHALL appear with a fade-in animation
- **AND** the popup SHALL display over a semi-transparent backdrop
- **AND** the popup animation SHALL complete within 300 milliseconds

#### Scenario: Profile popup displays user information
- **WHEN** the profile popup is open
- **THEN** it SHALL display the following user information:
  - Full name
  - Email address
  - User role
  - Profile picture or initials avatar (larger, 80x80 pixels)

#### Scenario: Closing profile popup by backdrop click
- **WHEN** a user clicks on the backdrop area outside the popup
- **THEN** the popup SHALL close with a fade-out animation
- **AND** the user SHALL return to the normal portal view

#### Scenario: Closing profile popup by ESC key
- **WHEN** the profile popup is open
- **AND** the user presses the ESC key
- **THEN** the popup SHALL close with a fade-out animation

#### Scenario: Closing profile popup by close button
- **WHEN** the profile popup is open
- **AND** the user clicks the X close button in the popup header
- **THEN** the popup SHALL close with a fade-out animation

### Requirement: Profile Picture Upload

The system SHALL allow users to upload custom profile pictures with validation and optimization.

#### Scenario: Uploading valid profile picture
- **WHEN** a user clicks the "Foto hochladen" button in the profile popup
- **AND** selects a valid image file (JPEG, PNG, or WebP)
- **AND** the file size is under 2MB
- **THEN** the system SHALL upload and process the image
- **AND** the system SHALL resize the image to 400x400 pixels
- **AND** the system SHALL store the image as base64 in the user profile
- **AND** the avatar SHALL immediately update to show the new picture

#### Scenario: Uploading oversized image
- **WHEN** a user attempts to upload an image file larger than 2MB
- **THEN** the system SHALL reject the upload
- **AND** display an error message: "Datei zu groß. Maximum 2MB."
- **AND** the existing avatar SHALL remain unchanged

#### Scenario: Uploading invalid file type
- **WHEN** a user attempts to upload a non-image file or unsupported image format
- **THEN** the system SHALL reject the upload
- **AND** display an error message: "Ungültiges Format. Nur JPEG, PNG, WebP erlaubt."
- **AND** the existing avatar SHALL remain unchanged

#### Scenario: Upload network failure
- **WHEN** an image upload fails due to network issues
- **THEN** the system SHALL display an error message: "Upload fehlgeschlagen. Bitte erneut versuchen."
- **AND** allow the user to retry the upload
- **AND** the existing avatar SHALL remain unchanged

#### Scenario: Upload progress indication
- **WHEN** a user is uploading a profile picture
- **THEN** the system SHALL display a loading indicator
- **AND** disable the upload button until completion

### Requirement: Profile Picture Removal

The system SHALL allow users to remove their profile picture and revert to initials display.

#### Scenario: Removing profile picture
- **WHEN** a user has an uploaded profile picture
- **AND** clicks the "Foto entfernen" button in the profile popup
- **THEN** the system SHALL delete the profile picture from the database
- **AND** the avatar SHALL immediately revert to displaying user initials
- **AND** display a success message: "Profilbild entfernt"

#### Scenario: Removing when no picture exists
- **WHEN** a user has no profile picture uploaded
- **THEN** the "Foto entfernen" button SHALL be disabled or hidden

### Requirement: Custom Settings Management in Popup

The system SHALL provide editable custom settings fields within the profile popup.

#### Scenario: Displaying current settings
- **WHEN** the profile popup is open
- **THEN** it SHALL display the user's current custom settings
- **AND** settings SHALL be editable in form fields

#### Scenario: Saving settings changes
- **WHEN** a user modifies one or more settings
- **AND** clicks the "Änderungen speichern" button
- **THEN** the system SHALL save the updated settings to the database
- **AND** display a success message: "Einstellungen gespeichert"
- **AND** the popup SHALL remain open

#### Scenario: Canceling settings changes
- **WHEN** a user modifies settings but clicks "Abbrechen"
- **THEN** the changes SHALL be discarded
- **AND** the popup SHALL close
- **AND** the original settings SHALL remain unchanged

#### Scenario: Settings validation
- **WHEN** a user enters invalid data in a settings field
- **AND** attempts to save
- **THEN** the system SHALL display field-specific validation errors
- **AND** prevent saving until errors are corrected

### Requirement: Sign Out from Profile Popup

The system SHALL provide a sign-out action within the profile popup.

#### Scenario: Signing out
- **WHEN** a user clicks the "Abmelden" button in the profile popup
- **THEN** the system SHALL log the user out
- **AND** redirect to the login page
- **AND** clear all authentication tokens

### Requirement: Profile Popup Theme Consistency

The system SHALL maintain visual consistency with the existing portal design.

#### Scenario: Popup styling matches portal theme
- **WHEN** the profile popup is displayed
- **THEN** it SHALL use the same color palette as the existing portal
- **AND** match the typography and spacing conventions
- **AND** use consistent border-radius and shadow styles

#### Scenario: Popup animations match portal animations
- **WHEN** profile popup animations play
- **THEN** they SHALL use the same timing functions as existing portal animations
- **AND** animation durations SHALL not exceed 300 milliseconds

### Requirement: Responsive Profile Popup Design

The system SHALL ensure the profile popup works well on all device sizes.

#### Scenario: Profile popup on desktop
- **WHEN** the profile popup is displayed on a desktop device (>768px width)
- **THEN** the popup SHALL be centered on the screen
- **AND** have a maximum width of 500 pixels

#### Scenario: Profile popup on mobile
- **WHEN** the profile popup is displayed on a mobile device (<768px width)
- **THEN** the popup SHALL be full-width with side margins
- **AND** position itself near the bottom of the screen for thumb accessibility

#### Scenario: Popup scroll behavior
- **WHEN** the profile popup content exceeds viewport height
- **THEN** the popup content SHALL be scrollable
- **AND** the backdrop SHALL remain fixed
- **AND** the popup header SHALL remain sticky at the top

### Requirement: Profile Data Persistence

The system SHALL persist profile data including pictures across user sessions.

#### Scenario: Profile picture persists after logout
- **WHEN** a user uploads a profile picture
- **AND** logs out
- **AND** logs back in
- **THEN** the profile picture SHALL still be displayed in the avatar

#### Scenario: Settings persist after browser close
- **WHEN** a user updates custom settings in the profile popup
- **AND** closes the browser
- **AND** reopens and logs in
- **THEN** the custom settings SHALL reflect the saved values

### Requirement: Backend API Endpoints for Profile Management

The system SHALL provide RESTful API endpoints for profile picture management.

#### Scenario: Upload profile picture endpoint
- **GIVEN** endpoint POST `/api/user/profile/picture`
- **WHEN** a valid image is uploaded with multipart/form-data
- **THEN** the server SHALL validate the image
- **AND** resize to 400x400 pixels
- **AND** store as base64 in user_profiles.data
- **AND** return HTTP 200 with the profile picture URL in JSON

#### Scenario: Get profile picture endpoint
- **GIVEN** endpoint GET `/api/user/profile/picture`
- **WHEN** the endpoint is called by an authenticated user
- **THEN** the server SHALL return HTTP 200 with the profile picture base64 data
- **OR** return HTTP 404 if no profile picture exists

#### Scenario: Delete profile picture endpoint
- **GIVEN** endpoint DELETE `/api/user/profile/picture`
- **WHEN** the endpoint is called by an authenticated user
- **THEN** the server SHALL remove the profile_picture field from user_profiles.data
- **AND** return HTTP 200 with success confirmation

#### Scenario: Authentication required for all profile endpoints
- **GIVEN** any profile picture endpoint
- **WHEN** called without valid authentication token
- **THEN** the server SHALL return HTTP 401 Unauthorized
- **AND** provide error message "Authentication required"

### Requirement: Rate Limiting on Profile Picture Uploads

The system SHALL implement rate limiting to prevent abuse of the profile picture upload feature.

#### Scenario: Normal upload frequency
- **WHEN** a user uploads 5 or fewer profile pictures within 1 hour
- **THEN** all uploads SHALL be processed normally

#### Scenario: Excessive upload attempts
- **WHEN** a user attempts to upload more than 5 profile pictures within 1 hour
- **THEN** the system SHALL reject subsequent uploads
- **AND** return HTTP 429 Too Many Requests
- **AND** provide error message "Zu viele Upload-Versuche. Bitte später erneut versuchen."

### Requirement: Image Security and Validation

The system SHALL validate and sanitize uploaded images to prevent security vulnerabilities.

#### Scenario: File type validation by magic numbers
- **WHEN** an image is uploaded
- **THEN** the server SHALL verify the file type by checking magic numbers (file signature)
- **AND** reject files that do not match JPEG, PNG, or WebP signatures
- **AND** not rely solely on file extension

#### Scenario: Image re-encoding for security
- **WHEN** a valid image is uploaded
- **THEN** the server SHALL re-encode the image using Pillow library
- **AND** strip all EXIF metadata
- **AND** remove potential embedded scripts or malicious data

#### Scenario: SQL injection prevention
- **WHEN** storing profile picture data in the database
- **THEN** the system SHALL use parameterized queries
- **AND** prevent SQL injection attacks

### Requirement: Accessibility Considerations

The system SHALL ensure profile popup features are accessible to users with disabilities.

#### Scenario: Keyboard navigation
- **WHEN** the profile popup is open
- **THEN** users SHALL be able to navigate all interactive elements using Tab key
- **AND** the focus order SHALL be logical (top to bottom)
- **AND** the focused element SHALL have visible focus indicators

#### Scenario: Screen reader support
- **WHEN** a screen reader user interacts with the profile section
- **THEN** the avatar SHALL have appropriate alt text
- **AND** the popup SHALL have ARIA labels
- **AND** status messages (upload success, errors) SHALL be announced

#### Scenario: Reduced motion preference
- **WHEN** a user has enabled "prefers-reduced-motion" in their OS settings
- **THEN** profile popup animations SHALL be minimal or disabled
- **AND** the popup SHALL still be functional

### Requirement: Error Handling and User Feedback

The system SHALL provide clear feedback for all profile-related actions.

#### Scenario: Success message display
- **WHEN** a profile action succeeds (upload, save settings, delete picture)
- **THEN** a success message SHALL appear
- **AND** the message SHALL auto-dismiss after 3 seconds
- **AND** use a green checkmark icon

#### Scenario: Error message display
- **WHEN** a profile action fails
- **THEN** an error message SHALL appear
- **AND** the message SHALL remain visible until dismissed by user
- **AND** use a red alert icon
- **AND** provide actionable guidance when possible

#### Scenario: Network offline handling
- **WHEN** the user is offline
- **AND** attempts a profile action that requires network
- **THEN** the system SHALL display message: "Keine Internetverbindung"
- **AND** allow the user to retry when connection is restored
