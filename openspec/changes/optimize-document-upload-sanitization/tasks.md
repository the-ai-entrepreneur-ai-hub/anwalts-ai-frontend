## 1. Analysis
- [x] 1.1 Trace current upload flow (FastAPI endpoints, `upload_processor`, documents page integration) and document sanitization gaps.
- [ ] 1.2 Capture baseline upload latency for representative files (text, PDF) to compare after optimization.

## 2. Backend Updates
- [x] 2.1 Refine `upload_processor` sanitization pipeline to guarantee redacted content is stored/retrieved while keeping raw bytes isolated.
- [x] 2.2 Adjust FastAPI upload/preview endpoints to return sanitized excerpts and avoid redundant disk reads.
- [x] 2.3 Extend backend tests (or add new ones) covering sanitization fidelity and multi-request reuse without reprocessing.

## 3. Frontend Updates
- [x] 3.1 Rework Documents page upload binding so sanitized preview and metadata from the API replace any direct file reads.
- [x] 3.2 Fix "Empty All"/"Leeren" action to clear file input, upload metadata, previews, and prompt context across UI state stores.
- [ ] 3.3 Add lightweight component/store tests (or end-to-end checks) validating the clear action and sanitized preview messaging.

## 4. Validation & Handoff
- [ ] 4.1 Exercise end-to-end upload → sanitize → generate flow with mixed PII samples to confirm redaction and performance budget.
- [ ] 4.2 Update relevant docs/playbooks with new behavior and share results with stakeholders.
