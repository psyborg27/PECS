# Command Code Consumer Guidance

This file is a minimal consumer-specific guidance wrapper.
Refer to the shared canonical consumer protocol at `.pecs/PECS_CONSUMER_PROTOCOL.md` for the authoritative PECS workflow.

Command Code-specific behavior:
- Query PECS before relying on workspace taste data.
- Preserve runtime workspace authority from PECS locality projections.
- Use taste files only for stylistic or continuity preferences, not as the primary source of runtime topology.

Do not duplicate the shared consumer protocol text in this file. Use the protocol document as the authoritative reference for:
- PECS-first query
- canonical query format
- response reporting
- used/not-used reporting
- ignored-reason reporting
- modified files/classes/functions reporting
- completion acknowledgement
- deterministic retrieval priority
