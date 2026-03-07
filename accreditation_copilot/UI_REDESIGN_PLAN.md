# UI Redesign Plan - Hybrid Approach

## Status: IN PROGRESS

## Overview
Redesigning the existing UI with a soft organic neon palette and glassmorphism while fixing all broken functionality.

## Issues Fixed

### 1. Backend API Fix ✅
- **Problem**: Audit endpoint was calling `audit_criterion()` with wrong parameters
- **Solution**: Added criterion registry lookup to get `query_template` and `description`
- **File**: `api/routers/audit.py`

## Design System Changes

### New Color Palette
```css
/* Soft Organic Neon Palette */
--neon-pink: #FF6EC7;
--neon-cyan: #5DE2E7;
--deep-indigo: #0F172A;
--background: #020617;
--glass-bg: rgba(15, 23, 42, 0.7);
--glass-border: rgba(94, 226, 231, 0.2);
```

### Design Features
- Glassmorphism cards with backdrop blur
- Smooth pink → cyan gradients
- Soft glow effects on hover
- Rounded corners (12px-16px)
- Subtle shadows with neon tints

## Pages to Implement

### Existing Pages (Redesign)
1. ✅ Dashboard - Apply new design
2. ✅ Run Audit - Fix buttons + new design
3. ✅ Evidence Explorer - New design
4. ✅ Metrics - New design
5. ✅ Audit History - New design

### New Pages (Create)
6. ⏳ Home - Landing page with hero section
7. ⏳ Login - Authentication page
8. ⏳ Register - User registration
9. ⏳ Profile - User profile management

## Button Fixes Required

### QueryPanel.tsx
- ✅ Voice Input Button - Already has onClick handler
- ✅ Upload Button - Already has onClick handler
- ✅ Run Audit Button - Fixed backend endpoint
- ⏳ Add visual feedback on click
- ⏳ Add loading states

### Upload Functionality
- ⏳ Connect to `/api/upload` endpoint
- ⏳ Show upload progress
- ⏳ Display uploaded file previews

### Voice Input
- ✅ Web Speech API already implemented
- ⏳ Add better visual feedback
- ⏳ Add error handling

## Implementation Steps

### Phase 1: Fix Functionality ✅
1. ✅ Fix audit endpoint backend
2. ⏳ Test audit button
3. ⏳ Fix upload endpoint connection
4. ⏳ Test voice input

### Phase 2: Apply New Design System
1. ⏳ Update globals.css with new colors
2. ⏳ Update tailwind.config.ts
3. ⏳ Create glassmorphism utility classes
4. ⏳ Update all existing components

### Phase 3: Add New Pages
1. ⏳ Create Home page
2. ⏳ Create Login page
3. ⏳ Create Register page
4. ⏳ Create Profile page
5. ⏳ Add routing

### Phase 4: Add Authentication
1. ⏳ Create auth context
2. ⏳ Add JWT token handling
3. ⏳ Protect routes
4. ⏳ Add logout functionality

## Next Steps

1. Start backend API server to test fixes
2. Update design system (colors, glassmorphism)
3. Fix remaining button functionality
4. Create new pages
5. Add authentication

## Testing Checklist

- [ ] Backend API starts successfully
- [ ] Audit button triggers API call
- [ ] Upload button accepts files
- [ ] Voice input captures speech
- [ ] All pages render correctly
- [ ] New design system applied
- [ ] Authentication works
- [ ] Routing works

## Files Modified

### Backend
- `api/routers/audit.py` - Fixed audit endpoint

### Frontend (To Modify)
- `app/globals.css` - New color palette
- `tailwind.config.ts` - New design tokens
- `components/QueryPanel.tsx` - Button fixes
- `components/*.tsx` - Apply new design
- `app/page.tsx` - Update layout

### Frontend (To Create)
- `app/(auth)/login/page.tsx`
- `app/(auth)/register/page.tsx`
- `app/(dashboard)/profile/page.tsx`
- `app/(marketing)/page.tsx` - New home page
- `lib/auth.ts` - Authentication utilities
- `contexts/AuthContext.tsx` - Auth state management

