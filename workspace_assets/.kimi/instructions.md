# Command Code / Kimi Consumer Guidance

This file is a minimal consumer-specific guidance wrapper.
Refer to the shared canonical consumer protocol at `.pecs/PECS_CONSUMER_PROTOCOL.md` for the authoritative PECS workflow.

Consumer-specific behavior:
- Kimi and Command Code should preserve runtime workspace authority.
- Kimi may use larger projection profiles for architecture-aware reasoning.
- Command Code may use workspace taste data, but PECS runtime topology remains the primary locality source.

Do not duplicate the shared consumer protocol text in this file. Use the protocol document as the authoritative reference for:
- PECS-first query
- canonical PECS query format
- response reporting
- used/not-used reporting
- ignored-reason reporting
- modified files/classes/functions reporting
- completion acknowledgement
- deterministic retrieval priority
