# Profile Popup Feature Design

## Context

The portal currently uses `PortalShell.vue` as the main navigation wrapper, which displays a sidebar with navigation links and a profile section at the bottom. The profile section shows a static avatar and basic user information, but users cannot interact with it to view or update their profile.

This design document outlines the technical approach for adding an interactive profile popup feature that allows users to:
- View their complete profile information
- Upload and manage profile pictures
- Update custom settings
- Sign out

### Existing Infrastructure
- **Database**: `user_profiles` table with JSONB `data` field (flexible schema)
- **Backend**: Existing endpoints `/api/user/profile` (GET/POST) and `/api/user/settings` (GET/POST)
- **Frontend**: `usePortalUser()` composable for user data management
- **Models**: `UserProfileResponse`, `UserProfileUpdate` already defined

### Constraints
- Must not break existing navigation
- Must maintain current color scheme and design language
- Must be performant (no sluggish animations)
- Must handle errors gracefully (upload failures, network issues)
- Must work on mobile devices (responsive)

## Goals / Non-Goals

### Goals
1. **User Initials Display**: Avatar shows first letter of user's first name when no profile picture is set
2. **Profile Picture Upload**: Users can upload JPEG/PNG/WebP images up to 2MB
3. **Interactive Popup**: Clicking profile section opens animated popup with user details
4. **Settings Management**: Users can update custom settings from popup
5. **Professional UX**: Smooth animations, consistent styling, loading states
6. **Mobile Support**: Popup works well on small screens

### Non-Goals
1. **Advanced Image Editing**: No cropping, filters, or rotation tools (users should prepare images beforehand)
2. **External Storage**: No S3/CDN integration in initial version (store in database)
3. **Avatar Gallery**: No pre-made avatar selection (future enhancement)
4. **Social Features**: No public profiles or user directories
5. **Account Security Settings**: Password change, 2FA remain in separate settings page

## Decisions

### 1. Profile Picture Storage Strategy

**Decision**: Store profile pictures as base64-encoded strings in the `user_profiles.data` JSONB field.

**Rationale**:
- Simpler implementation (no file system management)
- Already have JSONB storage infrastructure
- No additional storage service needed
- Atomic updates with profile data
- Easy to backup with database

**Alternatives Considered**:
- **File System Storage**: Requires volume management, backup complexity
- **S3/CDN**: Over-engineering for initial version, adds external dependency
- **Separate Database Table**: Unnecessary complexity for single field

**Trade-offs**:
- **Pro**: Simple, works with existing infrastructure
- **Pro**: No additional storage costs or services
- **Con**: Database size increase (mitigated by 2MB limit)
- **Con**: Slightly slower queries (mitigated by caching)

**Implementation Details**:
```json
{
  "profile_picture": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "profile_picture_uploaded_at": "2025-10-16T10:30:00Z"
}
```

### 2. Image Upload Validation

**Decision**: Validate images on backend with the following rules:
- Maximum file size: 2MB
- Allowed formats: JPEG, PNG, WebP
- Automatic image optimization (resize to 400x400px)

**Rationale**:
- 2MB is sufficient for high-quality profile pictures
- Common formats cover 99% of use cases
- 400x400px is standard for profile pictures (balance quality/size)
- Backend validation prevents malicious uploads

**Implementation**: Use Python Pillow library for validation and resizing.

### 3. Frontend Animation Strategy

**Decision**: Use Vue's built-in `<Transition>` component with CSS animations.

**Rationale**:
- Native Vue feature, no additional libraries
- Performant (CSS animations use GPU acceleration)
- Simple to implement and maintain
- Consistent with existing portal animations

**Animation Specifications**:
- **Backdrop**: Fade in over 200ms
- **Popup**: Slide up + fade in over 300ms with ease-out timing
- **Closing**: Reverse animations over 250ms

**Example**:
```vue
<Transition name="popup-fade">
  <div v-if="showPopup" class="profile-popup-backdrop">
    <Transition name="popup-slide">
      <div class="profile-popup">
        <!-- Content -->
      </div>
    </Transition>
  </div>
</Transition>
```

### 4. Avatar Display Logic

**Decision**: Implement cascading display logic in PortalShell:
1. If `profile_picture` exists in user data → show image
2. Else if `user.name` exists → show first letter of name
3. Else fallback to generic icon

**Rationale**:
- Clear priority order
- Graceful degradation
- Handles edge cases (new users, missing data)

**Implementation**:
```vue
<div class="portal-user__avatar">
  <img v-if="user?.profile_picture" :src="user.profile_picture" alt="Profile" />
  <span v-else>{{ getInitials(user?.name) }}</span>
</div>
```

### 5. Popup Component Structure

**Decision**: Create standalone `ProfilePopup.vue` component with the following sections:
1. **Header**: "Mein Profil" title with close button
2. **Avatar Section**: Large avatar with "Foto hochladen" button
3. **User Info Section**: Display email, name, role (read-only)
4. **Settings Section**: Editable custom settings fields
5. **Footer**: "Änderungen speichern" and "Abmelden" buttons

**Rationale**:
- Separate component keeps PortalShell clean
- Clear visual hierarchy
- Reusable across different pages (if needed)

### 6. API Endpoint Design

**Decision**: Add dedicated profile picture endpoints separate from general profile endpoint.

**Endpoints**:
```
POST   /api/user/profile/picture    # Upload picture
GET    /api/user/profile/picture    # Get picture URL
DELETE /api/user/profile/picture    # Remove picture
```

**Rationale**:
- Separation of concerns (profile data vs picture)
- Clearer REST semantics
- Easier to implement caching
- Allows for future enhancements (multiple pictures, picture history)

**Alternative Considered**:
- Include picture in general `/api/user/profile` endpoint
- **Rejected**: Mixing multipart/form-data with JSON is messy

## Risks / Trade-offs

### Risk 1: Database Size Growth
**Description**: Base64 images stored in database will increase size over time.

**Mitigation**:
- Enforce 2MB maximum file size
- Resize all images to 400x400px (reduces size by ~70%)
- Monitor database growth
- Plan migration to CDN if user base grows significantly

**Trade-off**: Accept larger database for simpler architecture in initial version.

### Risk 2: Image Upload Failures
**Description**: Network issues or invalid files could frustrate users.

**Mitigation**:
- Clear validation error messages ("File too large", "Invalid format")
- Show upload progress indicator
- Client-side validation before upload (check size/type)
- Retry logic for network failures
- Preserve existing avatar if upload fails

**Trade-off**: More code for error handling, but better UX.

### Risk 3: Animation Performance
**Description**: Animations could be janky on slower devices.

**Mitigation**:
- Use CSS transforms (GPU-accelerated)
- Keep animations under 300ms
- Test on mobile devices
- Provide reduced-motion alternative (respect `prefers-reduced-motion`)

**Trade-off**: Slightly more CSS complexity for smoother UX.

### Risk 4: Security - Malicious File Uploads
**Description**: Users could attempt to upload malicious files disguised as images.

**Mitigation**:
- Backend validation of file magic numbers (not just extension)
- Use Pillow to re-encode images (strips potential exploits)
- Set strict file size limit
- Rate limiting on upload endpoint (5 uploads per hour)
- Store base64 only (no executable code)

**Trade-off**: Additional validation overhead, but necessary for security.

## Migration Plan

### Phase 1: Backend Setup (Week 1)
1. Add profile picture endpoints to `backend-main.py`
2. Update database methods in `database.py`
3. Add image validation and processing
4. Test endpoints with Postman/curl
5. Deploy backend

### Phase 2: Frontend Implementation (Week 1-2)
1. Create ProfilePopup.vue component
2. Update PortalShell.vue with initials logic
3. Add file upload UI and handling
4. Implement animations
5. Test locally

### Phase 3: Integration Testing (Week 2)
1. End-to-end testing
2. Cross-browser testing
3. Mobile responsive testing
4. Performance testing
5. Security testing

### Phase 4: Deployment (Week 2)
1. Deploy backend changes
2. Deploy frontend changes
3. Monitor for errors
4. Gather user feedback

### Rollback Plan
If critical issues arise:
1. Revert frontend container to previous version
2. Revert backend container if endpoints cause issues
3. Profile pictures stored in database remain intact (no data loss)
4. Users revert to seeing initials only

### Data Migration
- **No migration required**: Existing users continue with no profile picture
- New `profile_picture` field added to their profile when they upload
- Backward compatible: Old profiles display initials

## Open Questions

### Q1: Should we support animated GIFs?
**Status**: Deferred
**Reasoning**: Adds complexity (size validation, frame extraction), low priority
**Decision**: Phase 2 feature, not initial release

### Q2: Should profile popup show additional stats (documents created, templates used)?
**Status**: Deferred
**Reasoning**: Requires additional database queries, slows popup load time
**Decision**: Keep popup lightweight, add stats to dashboard instead

### Q3: Should we compress images on client-side before upload?
**Status**: Investigate
**Reasoning**: Could reduce upload time and bandwidth
**Decision**: Backend compression is sufficient for v1, client-side is nice-to-have

### Q4: Should we allow users to delete their profile picture?
**Status**: Yes
**Reasoning**: User control and privacy
**Decision**: Add DELETE endpoint and "Remove Photo" button in popup

## Performance Considerations

### Expected Load
- Profile popup opens: ~1-2 times per session per user
- Profile picture uploads: ~1 per user per month (low frequency)
- Profile picture loads: Once per page load (cached)

### Optimization Strategies
1. **Caching**: Store profile picture in localStorage after first load
2. **Lazy Loading**: Don't load popup component until user clicks profile
3. **Image Optimization**: Resize to 400x400px, compress to ~100KB
4. **Debouncing**: Debounce settings updates (wait 500ms after typing)

### Monitoring
- Track upload success rate
- Monitor popup open/close times
- Track image file sizes
- Monitor API response times

## Success Metrics

### User Engagement
- **Target**: 30% of active users upload profile picture within first week
- **Target**: 50% of users open profile popup at least once

### Performance
- **Target**: Popup opens in <300ms
- **Target**: Image upload completes in <2 seconds (average)
- **Target**: Zero image-related security incidents

### Quality
- **Target**: <5% upload error rate
- **Target**: Zero breaking bugs affecting navigation
- **Target**: 95%+ positive user feedback

## Future Enhancements (Out of Scope)

1. **Avatar Gallery**: Pre-made avatars for users who don't want to upload
2. **Image Cropping**: In-browser image cropper for better framing
3. **CDN Integration**: Move images to CDN as user base grows
4. **Profile Badges**: Achievement badges shown on profile
5. **Public Profiles**: Shareable profile pages for collaboration
6. **Profile Themes**: Custom color schemes per user
