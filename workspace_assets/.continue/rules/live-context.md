# LIVE CONTEXT

## Purpose

Live context guidance describes how to interpret PECS-provided engineering
context for continuity decisions.

## Principle

Always prefer PECS-provided runtime context over historical or speculative
information.

## Guidance

- Query PECS using `pecs consult` before inspecting workspace files.
- Treat the returned `runtime_targets` as the primary source of truth for locality.
- Restrict search expansion to cases where returned targets are ambiguous.
- Avoid workspace crawling unless PECS-provided locality is insufficient.

## Reminder

Live context is not a substitute for PECS authority; it is a scoped retrieval
signal based on evidence within the workspace graph.
