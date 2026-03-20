# Implementation Plan: FutureBuilder Widget

Status: Proposed

## Overview

Provide a `FutureBuilder` widget for Pythra that encapsulates background work execution and safe main-thread dispatching. The widget should accept a callable, Future, or task-like object, run it on a framework-managed worker pool, and deliver snapshot updates to a declarative `builder` on the main Qt thread. The goal is to offer a Flutter-like developer experience while hiding Qt threading details.

## Goals

- Offer a simple, declarative API familiar to Flutter developers.
- Encapsulate thread management and `QTimer.singleShot` dispatching.
- Handle lifecycle events (rebuilds, disposal) safely and deterministically.
- Provide robust error reporting and cancellation semantics.

## High-level API (developer-facing)

- `FutureBuilder(future=..., builder=..., initialData=None, key=None, retry_policy=None)`
- `future` accepts: a zero-arg callable, a `concurrent.futures.Future`, or a framework Task wrapper.
- `builder(context, snapshot)` is invoked on the main thread whenever snapshot state changes.
- `Snapshot` exposes: `connectionState` (NONE/WAITING/ACTIVE/DONE), `data`, `error`, convenience booleans like `hasData`/`hasError`.

Note: Implementation details below — do not include code in this document.

## Internal Design

- Threading: use a single framework-managed `ThreadPoolExecutor` (configurable max workers). Tasks submitted by `FutureBuilder` are executed on this pool. Pool may live on a module-level singleton that can be configured or replaced for tests.
- Dispatch: results, errors, and snapshot transitions must be marshalled to the main Qt thread using `QTimer.singleShot(0, callback)` (abstracted behind a small helper in core to keep testing/mocking simple).
- Task lifecycle: each `FutureBuilder` instance tracks the currently active task and a unique task id token. When a task completes, the token is compared to the current active token to avoid stale updates.
- Cancellation: on `dispose` (widget unmount) the active task is marked cancelled; any incoming results from cancelled tasks are ignored. If underlying futures support cancellation, attempt to cancel; otherwise drop results on arrival.
- Rebuild semantics: if `future` parameter changes identity between builds, cancel previous task and start the new one. If the same `future` is passed, continue observing it.

## Snapshot Transitions

- Initial state: `connectionState = NONE` (or WAITING if `initialData` absent and task started immediately).
- When a task is submitted: `connectionState = WAITING`.
- On first partial progress (if supported): `connectionState = ACTIVE`.
- On success: `connectionState = DONE`, `data` populated.
- On failure: `connectionState = DONE`, `error` populated.

## Error Handling & Retry

- Exceptions raised by the callable are captured and exposed on the snapshot's `error` field.
- Provide optional `retry_policy` param to support simple retry/backoff behavior (configurable max retries, backoff strategy). Keep retry support pluggable and minimal for v1.

## Testing Strategy

- Unit tests (fast, deterministic):
  - Snapshot state machine tests (NONE→WAITING→DONE, error cases).
  - Main-thread dispatching: verify `builder` always runs on the Qt thread via a mocked dispatcher.
  - Cancellation: ensure disposed widgets ignore late results.
  - Identity change: ensure new `future` cancels previous work.
  - Thread-pool saturation: simulate many concurrent builders and assert pool limits enforced.
- Integration tests (UI-level):
  - Example app using `FutureBuilder` to fetch mock data; verify loading→success UI transitions.
  - Error display and retry flows.
- Performance tests:
  - Measure throughput and latency under load for common case (short-lived tasks) and long blocking calls.

## Documentation & Examples

- Update docs to include:
  - High-level explanation and best practices (when to use `FutureBuilder` vs `State.run_async`).
  - Example patterns (one-shot fetch, retry flows, cancellation on navigation).
  - Migration notes for existing code that uses manual `threading` + `QTimer`.
- Add a short demo in `docs/` and an example under `src/demo` showing typical usage.

## Acceptance Criteria

- Feature exposes the documented API and snapshot model.
- Builder always runs on the main Qt thread; no direct Qt calls are required from user code.
- Tasks are executed on a configurable worker pool and obey cancellation and identity-change rules.
- Unit and integration tests present and passing in CI.
- Documentation and a small demo/example are available.

## Timeline & Milestones (suggested)

- Week 0 (Design) — 1–2 days: finalize API and snapshot model; review with maintainers.
- Week 1 (Core infra) — 2–3 days: implement thread-pool abstraction and main-thread dispatcher helper.
- Week 2 (Widget) — 3–4 days: implement `FutureBuilder` lifecycle and snapshot management.
- Week 3 (Tests & Docs) — 2–3 days: write unit/integration tests and documentation examples.
- Week 4 (QA & Perf) — 2–3 days: performance tuning, edge-case fixes, finalize release notes.

## Risks & Mitigations

- Risk: Long-running blocking calls could starve the worker pool. Mitigation: sensible default pool size and clear docs recommending `async` or `to_thread` for extreme cases.
- Risk: Incorrect main-thread dispatch could cause race conditions. Mitigation: centralize dispatch helper and add unit tests that assert thread affinity.
- Risk: Memory leaks from tasks referencing widget state after disposal. Mitigation: token-based stale-result checks and strict disposal cancellation semantics.

## Next Steps (short-term)

1. Review API draft with maintainers and agree on `Snapshot` fields and `future` accepted types.
2. Implement thread-pool helper and dispatcher abstraction (small module).  
3. Implement `FutureBuilder` lifecycle tests first (TDD).  

---
Created for: FutureBuilder feature proposal and implementation planning.
