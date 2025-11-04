# Profile Popup Feature - OpenSpec Change Proposal

**Change ID**: `add-profile-popup`  
**Status**: Awaiting Approval  
**Created**: 2025-10-16

## Quick Summary

This change adds an interactive profile popup feature to the portal, allowing users to:
- View their complete profile information
- Upload custom profile pictures
- See their initials in the avatar when no picture is set
- Update custom settings
- Sign out

## Files in This Proposal

- **proposal.md** - Why we need this feature and what changes
- **tasks.md** - Step-by-step implementation checklist
- **design.md** - Technical decisions and architecture
- **specs/user-profile/spec.md** - Detailed requirements with scenarios

## Key Features

### 1. Smart Avatar Display
- Shows profile picture when uploaded
- Falls back to first letter of user's name
- Maintains existing color scheme

### 2. Interactive Popup
- Click profile section to open animated popup
- Smooth fade-in/slide-up animations
- Click outside or press ESC to close

### 3. Profile Picture Upload
- Support for JPEG, PNG, WebP
- Maximum 2MB file size
- Automatic resize to 400x400px
- Stored as base64 in database

### 4. Settings Management
- Edit custom settings from popup
- Save or cancel changes
- Real-time validation

### 5. Sign Out
- Quick sign-out button in popup

## Technical Highlights

### Backend
- New endpoints: POST/GET/DELETE `/api/user/profile/picture`
- Image validation with Pillow library
- Rate limiting (5 uploads/hour)
- Security: file type validation, re-encoding, metadata stripping

### Frontend
- New component: `ProfilePopup.vue`
- Updates to `PortalShell.vue`
- Vue Transition animations
- Responsive design (mobile-friendly)

### Database
- Uses existing `user_profiles` table
- Stores picture in JSONB `data` field
- No schema migration required

## Impact

✅ **Benefits**:
- Better user engagement and personalization
- Professional appearance
- Centralized profile management
- No breaking changes to existing features

⚠️ **Considerations**:
- Database size increase (mitigated by 2MB limit and image optimization)
- Additional API endpoints to maintain
- Image upload security requires careful validation

## Validation Status

✅ OpenSpec validation passed with `--strict` flag

## Next Steps

1. **Review this proposal** - Check if requirements align with business needs
2. **Get approval** - Confirm this is a priority feature
3. **Begin implementation** - Follow tasks.md checklist
4. **Test thoroughly** - Follow testing section in tasks.md
5. **Deploy** - Follow deployment checklist

## Estimated Timeline

- Backend implementation: 2-3 days
- Frontend implementation: 3-4 days
- Testing and refinement: 2 days
- **Total**: ~1.5 weeks

## Questions?

See `design.md` for detailed technical decisions and trade-offs.
