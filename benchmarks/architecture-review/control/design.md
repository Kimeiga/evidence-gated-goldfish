# Proposed webhook delivery architecture: clean control design

Status: design proposed for implementation. Product requirements are in `requirements.md`. This is a control artifact with no deliberately planted violation of those requirements, not a claim of perfect security or performance.

## API and persistence

The authenticated API validates the event and destination, then writes the event and one delivery record per eligible endpoint in a single Postgres transaction. It returns `202 Accepted` **only after commit**. On a DB failure or on reaching the configured admission-control limit, it returns a retryable error and does not promise acceptance. The request path contains no process-local queue and no asynchronous post-ack flush. Delivery consumers poll committed rows via an indexed ready-at timestamp.

The API's p95 SLO is 250 ms under bursts of 10,000 events/minute and 100,000 events/day. Before rollout, load tests use the actual event size distribution, a mix of destinations and healthy/unhealthy endpoints, and a database configured like production. The feature does not launch unless admission control and persistence meet that target.

## Worker state and scheduling

Deliveries use durable records and a retry state machine with `pending`, `leased`, `succeeded`, and `exhausted` states. A short DB lease with lease token, attempt deadline and ownership fencing prevents more than one active worker from holding a delivery at a time. A lease that expires without a recorded outcome can be recovered. Actual delivery remains at least once; a crash after sending but before recording success may legitimately produce duplicates.

The `delivery_id` is assigned once when the delivery row is created, and is reused verbatim for every subsequent attempt. Events have monotonic per-endpoint sequence numbers. For each endpoint, workers only lease the earliest unresolved delivery, preserving its event order; other endpoints can run independently. A stalled endpoint blocks only its own later events. A per-tenant scheduler with bounded concurrency prevents one tenant's backlog from consuming all available workers.

The database backlog is durable and bounded by admission control, configurable per-tenant quotas, and autoscaling of worker capacity. The system does not acknowledge events that exceed the safe ingest/storage threshold.

Each outbound request has an explicit DNS resolution deadline, connect timeout of 2 seconds, TLS handshake timeout of 3 seconds, response-header timeout of 5 seconds, and an overall 10-second deadline. Workers retry transient errors for 24 hours using exponential backoff with jitter. On `429`, they honor valid `Retry-After` values, combining them with the per-endpoint budget; invalid values fall back to bounded jittered backoff. The client rate limits per endpoint and records throttling metrics.

## Endpoints and security

Endpoint registration requires HTTPS and resolves each hostname through a controlled resolver; the outbound dialer rejects loopback, link-local, private, multicast, unspecified and known cloud-metadata address destinations at connection time. Connections are pinned to a validated IP for each attempt, with TLS hostname verification intact. All redirects are disabled by default; if later enabled, every redirect target and resolved address must pass the same validation. Destination addresses can change, so validation occurs on every attempt, not only at registration.

Each endpoint has a separately generated HMAC secret and secret version. During rotation, signing can use the current key while the service accepts an explicit overlap period for old receiver verification workflows. The signing input is the exact UTF-8 request bytes and a timestamp, with the payload bytes frozen for the attempt; no model-generated re-serialization occurs after signing. Secret material is stored in a secret-managed encrypted field and excluded from logs.

Endpoint enabled status is read from durable state immediately before each outgoing request. State invalidations and a conservative maximum cache age bound propagation to under 60 seconds, including events queued before the disable action.

## Data schema and rollout

The existing database includes production rows without tenant IDs. First add nullable tenant identifiers and create new write paths, then backfill legacy rows through a verified mapping, dual-read during rolling deployment, verify counts and ownership, and only then add NOT NULL constraints. Workers remain compatible with both schema versions throughout deployment. Forward and rollback compatibility are covered by migration tests.

Every attempt produces an auditable status record (timestamp, endpoint ID, HTTP status class, retry reason, duration) retained for 30 days. Exhausted deliveries retain their final failure status and attempt history; no raw notification payloads, HMAC keys, or authorization tokens appear in logs. Event bodies used for retry are deleted after the 24-hour retry window and need not be available for replay after exhaustion.

## Operations and verification

Per-endpoint counters measure sent, succeeded, rejected, retrying and exhausted deliveries. Histograms track attempt duration and end-to-end delivery latency; gauges track oldest pending age and queue depth. Alerts fire for sustained endpoint failures, growing backlog, aged pending deliveries and lease-recovery spikes. Traces link API acceptance, durable delivery ID, and worker attempts without logging payload data. Tests cover crash-after-commit, lease expiration, concurrent workers, endpoint disable, 429 Retry-After, SSRF address classes/redirects, HMAC rotation, rolling migrations, tenant fairness and per-endpoint order.

## Intentional semantics

This service offers at-least-once delivery, not exactly once. No ordering is promised across endpoints. Ordinary transient failures use capped, jittered exponential backoff. These choices follow the stated requirements.
