# Webhook delivery feature: product and engineering requirements

The existing product accepts events from authenticated tenant clients and forwards event notifications to registered HTTPS destinations. Its users must be able to inspect delivery attempts, disable endpoints, and reason about whether their data will be delivered.

R1. A successful `202 Accepted` response means the event has been durably recorded. A process crash immediately after acknowledgment must not lose it.

R2. Delivery is **at least once**, not exactly once. Every retry of the same event to the same destination carries a stable `delivery_id` so that receivers can deduplicate. Duplicate deliveries are acceptable; newly generated delivery IDs on retries are not.

R3. Deliveries to any **one endpoint** preserve event creation order, including retries. No ordering between different endpoints is promised.

R4. Support 100,000 events/day, bursts of 10,000 events/min, and multiple independent tenants. A tenant with a stalled receiver must not prevent a healthy tenant's events from being delivered.

R5. Honor per-endpoint rate limits and HTTP `Retry-After` on `429`. Retry transient failures for up to 24 hours with bounded backoff and jitter.

R6. Destination URLs are untrusted. Prevent callbacks to local, link-local, private, and cloud metadata addresses, including via DNS resolution and redirects.

R7. Authenticate deliveries using per-endpoint HMAC secrets that can be rotated without downtime. Sign the actual request bytes and include a timestamp.

R8. Disabling an endpoint must stop new outgoing requests to it within 60 seconds, including previously queued events.

R9. Retain delivery attempt status/history for 30 days for inspection. Do not record unredacted notification payloads or secrets in logs.

R10. Database migrations must not break existing endpoints or pending deliveries during rolling deployment.

R11. Ingestion p95 latency must remain under 250 ms at the stated burst rate. Shed load cleanly rather than acknowledging events that may disappear.

R12. Operators need per-endpoint delivery success/failure counts, oldest pending age, retry volume, and alerts on sustained failure or backlog growth.

Out of scope: receiver-side HMAC verification, exactly-once delivery, cross-endpoint event ordering, and replaying historical payloads after the 24-hour retry period.
