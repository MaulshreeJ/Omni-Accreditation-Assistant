# Validation Error Fix

## Issue
The frontend was showing a Pydantic validation error when running audits. The error occurred because the `AuditResponse` model expected a `grounding` field as a dictionary, but the backend was returning `dimension_grounding` as a list.

## Root Cause
Field name mismatch between:
- **Backend response**: `dimension_grounding` (list), `gaps_identified` (list), `evidence_strength` (dict)
- **Pydantic model**: `grounding` (dict)

## Fix Applied
Updated `accreditation_copilot/api/routers/audit.py` to properly structure the `grounding` field as a dictionary containing all grounding-related data:

```python
grounding={
    "dimension_grounding": standardized.get("dimension_grounding", []),
    "gaps_identified": standardized.get("gaps_identified", []),
    "evidence_strength": standardized.get("evidence_strength", {})
}
```

## Testing
To test the fix:

1. **Start the backend API** (in terminal 1):
   ```bash
   cd accreditation_copilot
   uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend** (in terminal 2):
   ```bash
   cd accreditation_copilot/frontend
   npm run dev
   ```

3. **Test the audit functionality**:
   - Open http://localhost:3000
   - Select a framework (NAAC or NBA)
   - Enter a criterion (e.g., "3.2.1" for NAAC or "C5" for NBA)
   - Click "Run Audit"
   - The audit should complete without validation errors

## Expected Behavior
- ✅ No Pydantic validation errors
- ✅ Audit results display correctly
- ✅ All buttons work (Upload, Voice, Run Audit)
- ✅ Evidence, gaps, and grounding data are properly structured

## Files Modified
- `accreditation_copilot/api/routers/audit.py` - Fixed grounding field structure
