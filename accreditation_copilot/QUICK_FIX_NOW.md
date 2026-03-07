# QUICK FIX - DO THIS NOW

## The Problem
Your backend is still running the OLD code with cached 0% results.

## The Solution (30 seconds)

### Step 1: Close Backend Window
Find the window titled "Backend API" and close it (or press Ctrl+C in it)

### Step 2: Run This File
Double-click: `accreditation_copilot\RESTART_BACKEND.bat`

### Step 3: Wait 5 Seconds
Let the backend start up

### Step 4: Refresh Browser
Press Ctrl+F5 in your browser (hard refresh)

### Step 5: Click "Run Audit"
You should now see:
- ✅ Confidence: ~15-20% (not 0%)
- ✅ Coverage: 100% (not 0%)
- ✅ Status: Partial (not Weak)
- ✅ Recommendations showing

## What You'll See

**Evidence Section:**
- Greenfield_MissingEvidence_SSR.pdf
- Riverton_Bplus_SSR.pdf
- Real scores (0.928, 0.457, etc.)

**Gap Analysis:**
- Specific gaps identified
- Recommendations to improve from B+ to A+

**Recommendations Will Include:**
- Increase research funding documentation
- Add more externally funded projects
- Document funding agencies properly
- Provide comprehensive data for all metrics

## Why It's Still Showing 0%

The backend is using CACHED results from before the fix. Once you restart it, the cache is cleared and it will use the NEW fixed code.

## If It Still Doesn't Work

1. Check if backend window shows errors
2. Make sure you're using the venv (should see "(venv)" in the window)
3. Try closing ALL Python windows and run RESTART_BACKEND.bat again

The fix is done - you just need to restart the backend!
