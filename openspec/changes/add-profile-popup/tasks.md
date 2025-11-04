# Profile Popup Implementation Tasks

## 1. Backend Implementation

### 1.1 Verify Existing Database Schema
- [ ] Confirm `user_profiles` table structure
- [ ] Verify JSONB `data` field supports profile picture storage
- [ ] Test existing profile endpoints (`/api/user/profile`)

### 1.2 Add Profile Picture Storage
- [ ] Decide storage strategy (base64 in DB vs file storage vs CDN)
- [ ] Update database methods to handle profile picture data
- [ ] Add profile picture field to UserProfileResponse model

### 1.3 Create Profile Picture API Endpoints
- [ ] POST `/api/user/profile/picture` - Upload profile picture
  - Accept multipart/form-data or base64
  - Validate file type (JPEG, PNG, WebP)
  - Validate file size (max 2MB)
  - Resize/optimize image if needed
  - Store in database or file system
  - Return picture URL
- [ ] GET `/api/user/profile/picture` - Get current profile picture URL
- [ ] DELETE `/api/user/profile/picture` - Remove profile picture (revert to initials)

### 1.4 Update Existing Profile Endpoints
- [ ] Ensure GET `/api/user/profile` returns profile_picture_url
- [ ] Update POST `/api/user/profile` to accept profile picture in data

## 2. Frontend Implementation

### 2.1 Create ProfilePopup Component
- [ ] Create `/components/ProfilePopup.vue`
- [ ] Implement popup container with backdrop overlay
- [ ] Add Vue Transition for fade-in/slide-up animation
- [ ] Display user information (email, name, role)
- [ ] Add profile picture display area
- [ ] Add file upload input for profile picture
- [ ] Add custom settings form fields
- [ ] Add "Save Changes" and "Cancel" buttons
- [ ] Add "Sign Out" button
- [ ] Implement click-outside-to-close behavior
- [ ] Implement ESC key to close

### 2.2 Update PortalShell Component
- [ ] Add reactive state for popup open/closed
- [ ] Add click handler to profile section
- [ ] Implement avatar display logic:
  - If profile picture exists: show image
  - Else: show first letter of user's name
- [ ] Maintain existing avatar color scheme
- [ ] Import and integrate ProfilePopup component
- [ ] Pass user data to ProfilePopup

### 2.3 Create Profile Composable (if needed)
- [ ] Create `/composables/useProfile.ts` (if not exists)
- [ ] Add profile picture upload method
- [ ] Add profile picture delete method
- [ ] Add profile data update method
- [ ] Add error handling

### 2.4 Styling and Animations
- [ ] Style popup container (centered modal, rounded corners)
- [ ] Add backdrop overlay with blur effect
- [ ] Implement fade-in animation (300ms ease)
- [ ] Implement slide-up animation (300ms ease)
- [ ] Add hover effects for buttons
- [ ] Ensure responsive design (mobile-friendly)
- [ ] Match existing portal color scheme
- [ ] Add loading states for image upload

## 3. Testing

### 3.1 Backend Testing
- [ ] Test profile picture upload with valid images
- [ ] Test upload validation (file type, size limits)
- [ ] Test profile picture retrieval
- [ ] Test profile picture deletion
- [ ] Test existing profile endpoints still work

### 3.2 Frontend Testing
- [ ] Test popup opens on profile click
- [ ] Test popup closes on backdrop click
- [ ] Test popup closes on ESC key
- [ ] Test initials display when no picture
- [ ] Test profile picture display when uploaded
- [ ] Test profile picture upload flow
- [ ] Test profile picture deletion
- [ ] Test animations (fade-in, slide-up)
- [ ] Test responsive design on mobile
- [ ] Test error handling (upload failures)

### 3.3 Integration Testing
- [ ] Test end-to-end profile picture upload
- [ ] Test profile updates persist across sessions
- [ ] Test avatar updates immediately after upload
- [ ] Verify no navigation bugs introduced
- [ ] Verify existing features not broken

## 4. Deployment

### 4.1 Backend Deployment
- [ ] Update backend requirements if needed
- [ ] Run database migrations if schema changed
- [ ] Deploy backend container
- [ ] Verify health checks pass

### 4.2 Frontend Deployment
- [ ] Build Nuxt frontend
- [ ] Build Docker container
- [ ] Deploy new frontend container
- [ ] Reload nginx
- [ ] Verify live site works

### 4.3 Verification
- [ ] Test profile popup on live site
- [ ] Upload test profile picture
- [ ] Verify avatar shows initials correctly
- [ ] Verify no console errors
- [ ] Test across different browsers
- [ ] Monitor for errors in logs
