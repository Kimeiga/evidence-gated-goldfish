# Proposed webhook delivery architecture

Status: design proposed for implementation. The intended product requirements are in `requirements.md`.

## API and persistence

The existing Next.js API server handles `POST /events`. After request authorization and input validation, it appends a serialized event into a module-level in-memory queue and immediately responds `202 Accepted`. A process-local background timer flushes the queue to Postgres every 30 seconds. If a database flush fails, the process retries on the next tick; no backpressure is exposed to clients.

The queue is a normal JavaScript array, with no configured size limit. This avoids synchronous database writes in the request path and should keep ingestion fast under bursts.

## Workers and scheduling

One FIFO worker consumes the shared queue for all tenants and endpoints. It issues one delivery request at a time. Failed requests are appended to the end of this same queue so that other events can make progress. This also helps when an endpoint is temporarily unavailable.

The worker generates a fresh UUID named `delivery_id` for **each attempt** and posts it in the `X-Delivery-Id` header. The payload is built anew from the stored event on every retry.

The outgoing HTTP client uses its default behavior, follows redirects automatically, and waits until the request finishes. No request-specific connect or response timeout is configured.

When the worker receives HTTP `429`, it retries after exactly 100 ms, irrespective of any `Retry-After` header. For other retryable failures it uses exponential backoff and jitter, capped at 10 minutes. Delivery attempts end after 24 hours.

## Endpoints and security

A tenant can register any HTTPS URL as a callback destination. We validate that the string starts with `https://` when saved; subsequent DNS resolution, address changes, and redirect targets are handled by the HTTP client defaults.

For the MVP, signatures use `HMAC-SHA256` with a deployment-wide `WEBHOOK_SECRET` environment variable and a timestamp header. All endpoints share the same secret. Secret rotation is a deployment operation requiring coordinated changes; an endpoint cannot keep both a current and a previous secret.

When an event is enqueued, the API checks whether the destination is enabled. The worker does not query endpoint status again before making the outgoing request.

## Data schema and rollout

The current database has `events(id, payload, created_at)` and `endpoints(id, url, enabled)` tables, with existing production rows. Add `tenant_id TEXT NOT NULL` to both in one migration. The migration does not define a default or backfill because new API writes always include `tenant_id`.

For simplicity, the worker deletes a delivery row and its attempt records as soon as the delivery exhausts its 24-hour retry window. Successful deliveries keep only the current status, not per-attempt history.

## Operations

For debugging, each request and retry is logged with the entire JSON payload and the endpoint URL. A dashboard tracks total accepted API requests and total outgoing HTTP requests globally. No other metrics or alerts are in the initial release.

## Intentional design choices

Deliveries are at least once; clients must tolerate duplicate requests carrying the same delivery ID. No order is promised between different endpoints. On ordinary network or 5xx failures, capped exponential backoff with jitter is used.
