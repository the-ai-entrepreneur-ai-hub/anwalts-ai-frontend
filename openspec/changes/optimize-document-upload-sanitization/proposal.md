## Why
- Uploaded documents currently surface raw personal information because sanitization output is not consistently propagated through the backend endpoints and document composer pipeline.
- "Empty All" on the Documents page fails to clear uploaded artifacts, leaving stale previews/metadata that reintroduce sensitive text and confuse subsequent uploads.
- Upload performance relies on blocking file operations and redundant parsing, producing noticeable lag during multi-MB uploads.

## What Changes
- Verify and fix the upload processor so the sanitized text becomes the single source of truth for downstream consumers (preview, AI prompt context, document generation) while keeping raw files quarantined.
- Harden the sanitization layer with targeted pattern coverage and fast-path guards so common German legal identifiers (addresses, IBAN, phone/email) are redacted without adding latency.
- Update FastAPI upload endpoints to surface sanitized snippets/metadata and to short-circuit expensive re-processing on subsequent reads.
- Align the Nuxt Documents page upload widget with the backend contract, ensure "Empty All" clears file state, previews, and cached metadata, and surface clear UI cues when redaction succeeds.
- Back the changes with unit/integration coverage for sanitization fidelity and UI clearing logic, plus lightweight timing checks to guard against regressions.

## Impact
- Restores compliance-critical PII scrubbing for uploaded documents and keeps the legal workflow trustworthy.
- Streamlines upload UX by eliminating lingering state and keeping interactions under existing latency budgets.
- Imposes minimal risk on adjacent systems because changes stay within the upload processor, related API routes, and documents page UI.
