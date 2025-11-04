# Profile Popup Feature Proposal

## Why

The current profile section in the portal sidebar shows only a static avatar and basic user information (name and role). Users have no way to:

1. **View Complete Profile Details**: Cannot access their full profile information (email, first name, custom settings) from within the portal
2. **Update Profile Settings**: No interface exists for users to manage their profile settings and preferences
3. **Visual Avatar Personalization**: The profile avatar is currently blank/generic with no personalization (no user initials or custom profile pictures)
4. **Quick Access to Profile Actions**: Users need a convenient way to access profile-related actions without navigating to settings

This creates a fragmented user experience where users cannot easily manage their profile information or personalize their account appearance.

## What Changes

- **Add Interactive Profile Popup**: Clicking the profile section in the sidebar will trigger an animated popup overlay showing complete user details and settings
- **Display User Initials in Avatar**: The profile avatar will show the first letter of the user's first name by default (maintaining the existing color scheme)
- **Profile Picture Upload**: Users can upload a custom profile picture that replaces the initials
- **Profile Information Display**: Popup will show email, first name, role, and other profile details
- **Custom Settings Management**: Users can modify custom settings directly from the popup
- **Backend Profile Picture Endpoint**: Add API endpoint for uploading and retrieving profile pictures
- **Database Schema Enhancement**: Store profile picture URL in the existing `user_profiles.data` JSONB field
- **Smooth Animations**: Implement fade-in/fade-out and slide animations for professional UX
- **Theme Consistency**: Popup maintains existing portal color scheme and design patterns

## Impact

### Affected Specs
- `user-profile` (new spec) - Complete user profile management capability

### Affected Code
- `/components/PortalShell.vue` - Add click handler, display initials/profile picture
- `/components/ProfilePopup.vue` (new) - Profile popup component with animations
- `/backend-main.py` - Add profile picture upload/retrieve endpoints
- `/models.py` - Potentially add profile picture models
- `/database.py` - Profile picture storage methods (if needed beyond existing)

### Database Impact
- **No new tables required**: Existing `user_profiles` table already has JSONB `data` field
- **Schema extension**: Store `profile_picture_url` in the JSONB data field
- **Backward compatible**: Existing profiles continue to work without profile pictures

### User Experience Impact
- **Positive**: Users can quickly view and update their profile without leaving the current page
- **Positive**: Personalized avatars improve user engagement and identification
- **Positive**: Centralized profile management improves discoverability
- **Positive**: Professional animations enhance perceived quality
- **No breaking changes**: Existing navigation and functionality remain unchanged

### Technical Impact
- Frontend: New Vue component with animations (Vue Transition)
- Backend: 2-3 new API endpoints (upload, retrieve, delete profile picture)
- Storage: Profile pictures stored as base64 in database or as file URLs
- Performance: Minimal impact (profile pictures lazy-loaded)
- Security: File upload validation required (size limits, file types)

### Non-Goals
- This change does NOT include:
  - Advanced profile fields beyond basic information
  - Social media integration
  - Multi-factor authentication settings (separate feature)
  - Team/organization management
