# Documents Page Debug Guide - Testing Instructions

**Date:** October 18, 2025  
**Status:** ✅ Debug Logging Added - Ready for Testing

---

## Changes Made

### 1. Comprehensive Debug Logging Added
- ✅ Log when onMounted starts
- ✅ Log API endpoint configuration
- ✅ Log when buttons are found/not found
- ✅ Log when button listeners are attached
- ✅ Log when generate() is called
- ✅ Log when documentAction() is called
- ✅ Log when onMounted completes successfully

### 2. Error Boundary Added
- ✅ Wrap entire onMounted in try-catch
- ✅ Log detailed error information to console
- ✅ Show visible error message to user if initialization fails
- ✅ Set window.__DOCUMENTS_INITIALIZED flag

### 3. Frontend Container Restarted
- ✅ Container restarted to pick up code changes
- ✅ Nuxt will rebuild on next page load

---

## How to Test on Live Site

### Step 1: Open Browser Console

1. Navigate to: https://portal-anwalts.ai/documents
2. Open browser developer tools (F12 or Right-click → Inspect)
3. Go to **Console** tab
4. Clear any existing logs

### Step 2: Check Initialization Logs

**You should see these console logs immediately:**

```
[Documents] onMounted started at 2025-10-18T...
[Documents] API configuration: {apiBase: "/api", hasEndpoints: true}
[Documents] Endpoints configured: {generate: "...", process: "/api/documents/process", ...}
[Documents] Generate button found: true
[Documents] Generate button listener attached
[Documents] Send button found: true
[Documents] onMounted completed successfully
```

**If you see these logs → JavaScript is working! ✅**

**If you DON'T see these logs → Problem identified:**
- No logs at all = JavaScript not executing
- Partial logs = Failed during initialization
- Error logs = Check error message

### Step 3: Test Generate Button

1. Fill in the form:
   - **Document type**: "Testdokument"
   - **Instructions**: "Dies ist ein Test"
2. Click **"Dokument erzeugen"** button

**Expected console logs:**
```
[Documents] Generate button clicked
[Documents] generate() called
[Documents] Generate params: {type: "Testdokument", instrLength: 17}
[Documents] Calling documentAction with generate
```

**Also check Network tab:**
- Should see POST request to `/api/documents/process`
- Request payload: `{"action":"generate","payload":{...}}`

### Step 4: Check Response

**Success scenario:**
- Loading overlay appears: "Dokument wird erstellt..."
- After 2-10 seconds, document appears in preview pane
- Word count updates
- Action buttons appear (Accept, Copy, Export)

**Error scenario:**
- Error message appears: "Generierung fehlgeschlagen: [reason]"
- Console shows error with details
- Check Network tab response for backend error

---

## Troubleshooting Guide

### Problem: No Console Logs at All

**Possible causes:**
1. JavaScript execution blocked by browser
2. Page didn't load completely
3. Frontend container not serving new code

**Solutions:**
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Clear browser cache
- Try incognito/private browsing mode
- Check if frontend container is running: `docker ps | grep frontend`

### Problem: Logs Show "Generate button NOT FOUND"

**Cause:** DOM element with id="btnGenerate" doesn't exist

**Solutions:**
- Check if HTML was modified
- Verify page rendered correctly (View Source)
- Check if button is inside a hidden/conditional section
- Verify PortalShell component loaded correctly

### Problem: Button Click Logs But No API Call

**Possible causes:**
1. documentAction() function failing
2. API endpoint misconfigured
3. Authentication issue

**Debug:**
- Check console for error after "Calling documentAction"
- Look for 401/403 authentication errors
- Verify `/api/documents/process` endpoint exists

### Problem: API Call Made But No Response

**Possible causes:**
1. Backend timeout (>60 seconds)
2. Backend error (500)
3. Together AI not responding

**Debug:**
- Check Network tab for response status code
- Check backend logs: `docker logs anwalts_backend --tail 50`
- Look for Together AI errors in backend logs
- Verify Together AI API key is valid

### Problem: Red Error Box Appears on Page

**Meaning:** onMounted failed during initialization

**What to do:**
1. Read error message in red box
2. Check console for full error stack trace
3. Note which line failed
4. Report exact error message

---

## Common Error Messages & Solutions

### "Could not validate credentials"
**Cause:** Not logged in or session expired  
**Solution:** Log in again via OAuth or email/password

### "Generierung fehlgeschlagen: KI-Anfrage hat zu lange gedauert"
**Cause:** Together AI timeout after 60 seconds  
**Solution:** Retry with shorter instructions

### "Generierung fehlgeschlagen: Backend lieferte kein verwendbares Dokument"
**Cause:** Backend returned empty/invalid response  
**Solution:** Check backend logs for errors

### "Nicht autorisiert (403)"
**Cause:** Authentication token invalid  
**Solution:** Log out and log in again

---

## Manual Testing Checklist

### Basic Functionality
- [ ] Page loads without errors
- [ ] Console shows initialization logs
- [ ] "Dokument erzeugen" button exists and clickable
- [ ] Button click shows console log
- [ ] API call appears in Network tab

### Document Generation
- [ ] Generate with simple text input
- [ ] Generate with template selected
- [ ] Generate with file uploaded
- [ ] Loading overlay appears during generation
- [ ] Document appears in preview after success
- [ ] Word count updates correctly

### Error Handling
- [ ] Try with empty instructions → validation error
- [ ] Try with very long text → handles gracefully
- [ ] Try after session expires → auth error shown

### Other Buttons
- [ ] "Zur Verarbeitung senden" button works
- [ ] "Vorlagen" button opens modal
- [ ] "Löschen" button clears form
- [ ] Export buttons work (DOCX, PDF)

### Regression Testing
- [ ] OAuth login still works
- [ ] Dashboard still loads
- [ ] Assistant page still works
- [ ] Templates page still loads
- [ ] Email page still loads
- [ ] Settings page still loads

---

## Expected Behavior After Fix

### ✅ Working State Indicators

1. **Console logs appear** proving JavaScript executes
2. **Buttons respond to clicks** with console feedback
3. **API calls made** visible in Network tab
4. **Loading states work** (overlay, spinners)
5. **Documents generate successfully** or show clear error
6. **No silent failures** - everything is logged

### ❌ Still Broken Indicators

1. **No console logs** = JavaScript still not executing
2. **"Button NOT FOUND" logs** = DOM structure issue
3. **No API calls in Network** = Request not being sent
4. **500 errors in Network** = Backend issue (separate problem)
5. **Red error box on page** = Initialization failure

---

## Reporting Issues

If problems persist after testing, provide:

1. **Screenshot of browser console** showing all logs
2. **Screenshot of Network tab** showing API requests
3. **Exact steps taken** to reproduce issue
4. **Browser and version** (Chrome 119, Firefox 120, etc.)
5. **Any error messages** visible on page or console
6. **Backend logs** if API calls are failing

---

## Next Steps If Still Broken

### Scenario 1: No Console Logs
→ JavaScript not executing at all
→ Need to investigate Nuxt build/compilation issue

### Scenario 2: Logs Show Buttons NOT FOUND
→ DOM structure mismatch
→ Need to verify HTML template rendering

### Scenario 3: Buttons Work But API Fails
→ Backend integration issue
→ Need to fix `/api/documents/process` endpoint

### Scenario 4: Everything Logs But No Visual Response
→ UI update issue
→ Need to check preview pane rendering logic

---

## Success Criteria

✅ **PASS:** 
- Console shows all expected logs
- Button clicks trigger actions
- API calls are made
- Documents generate OR clear error shown

❌ **FAIL:**
- No console logs at all
- Buttons don't respond
- No API calls made
- Silent failures

---

**Ready to test!** Open https://portal-anwalts.ai/documents with console open.
