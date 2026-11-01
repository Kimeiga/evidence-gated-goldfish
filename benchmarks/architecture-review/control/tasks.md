# Proposed implementation tasks

- [ ] T1. Implement atomic event and delivery persistence before 202, admission control, and burst load tests.
- [ ] T2. Add the durable delivery state machine, leases, ownership fencing, crash recovery and fixed delivery ID.
- [ ] T3. Add per-endpoint order and tenant fair scheduling; cap worker concurrency and backlog.
- [ ] T4. Add request deadlines, retries, Retry-After and endpoint rate limiting.
- [ ] T5. Add SSRF-resistant outbound connector and tests of DNS, IP classes and redirects.
- [ ] T6. Add per-endpoint HMAC signing, exact payload bytes and key rotation.
- [ ] T7. Add endpoint disable propagation and queued delivery cancellation checks.
- [ ] T8. Add nullable-migrate/backfill/dual-read/enforce rollout and rollback tests.
- [ ] T9. Add 30-day redacted attempt history with 24-hour payload retention.
- [ ] T10. Add delivery metrics, alerts, tracing and E2E negative tests.
