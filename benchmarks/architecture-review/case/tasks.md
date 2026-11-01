# Proposed implementation tasks

- [ ] T1. Add the request handler and process-local queue. Return 202 immediately after enqueue.
- [ ] T2. Add a 30-second background Postgres flush timer.
- [ ] T3. Add one FIFO worker and retry failed items by appending to queue tail.
- [ ] T4. Add the outbound HTTP client with default redirects and default timeouts.
- [ ] T5. Generate a new delivery UUID at each attempt; use a 100 ms retry on 429.
- [ ] T6. Add callback endpoint registration; validate HTTPS URL prefix.
- [ ] T7. Configure deployment-wide signing secret with timestamp.
- [ ] T8. Gate delivery by enabled status only when initially enqueued.
- [ ] T9. Add non-null tenant_id columns; release without backfill.
- [ ] T10. Delete finished retry records at 24 hours.
- [ ] T11. Log payloads and global traffic counters.
- [ ] T12. Unit tests: event payload JSON serialization, HMAC function shape, and 202 response on successful queue append.
