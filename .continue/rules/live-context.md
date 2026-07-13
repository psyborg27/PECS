# LIVE CONTEXT

## Purpose

Live context documentation describes the current runtime view and the signals that should guide continuity decisions.

## Principle

Always prefer active runtime state and PECS-provided locality guidance over historical or speculative information.

## Guidance

- Use `.pecs/active_context.json` and `.pecs/locality_index.json` to identify active runtime targets.
- Treat live context as the first source of truth for locality.
- Restrict search expansion to cases where returned PECS targets are ambiguous or stale.
- Avoid workspace crawling unless runtime-confirmed locality is unavailable.

## Reminder

Live context is not a substitute for runtime authority; it is a scoped retrieval signal.
