# PECS Consultation Policy

## Purpose
Recommend whether PECS consultation should be optional or mandatory for downstream consumers.

## Options
A. Optional
B. Mandatory Query + Optional Reliance
C. Mandatory Query + Mandatory Reliance

## Recommendation
**Mandatory Query + Optional Reliance**

## Justification

### Why mandatory query?
- PECS is the evidence source for runtime/locality authority and continuity accountability.
- Even if the consumer does not ultimately rely on PECS, issuing a query provides observability and consistent telemetry.
- In the current architecture, the projection path is the practical evidence interface and should be invoked for all sessions.

### Why optional reliance?
- The downstream model may still need to decide not to fully rely on PECS evidence when it is insufficient or incomplete.
- The current `engineering_continuity_state.json` export is under-fused and should not be treated as the sole authoritative source.
- Consumers need the flexibility to combine PECS evidence with other reasoning or fallback search when appropriate.

### What this policy means
- All consumers must issue a PECS query for every request.
- The query shall be documented in `PECS Status`.
- Reliance on PECS evidence is optional and should be explicitly reported in `Relying On PECS`.
- If the query fails or evidence is incomplete, the consumer may fall back to alternate reasoning or minimal context, but must still record the fallback.

## Policy Rationale

### Full observability
- Requiring the query ensures the system can audit whether PECS has been consulted.
- It prevents silent bypass and preserves the ability to detect integration drift.

### Evidence quality
- Mandatory reliance would be premature while `engineering_continuity_state.json` is still effectively `Chat -> Authority`.
- Optional reliance allows continued use of PECS evidence without overstating its canonical completeness.

### Future-proofing
- As continuity export improves, this policy can migrate toward stronger reliance without changing the query obligation.
- The hybrid model supports incremental improvement: projection-first now, continuity-first later.

## Policy Implementation Notes

1. `PECS Status` must show `queried_pegs: true` for all consumers.
2. `Relying On PECS` must specify whether the consumer actually trusted PECS evidence for decisions.
3. `fallback_reason` must be populated if the consumer did not rely on PECS or if PECS evidence was incomplete.
4. `artifact_writes` must remain 0 for projection consumers.

## Recommendation Summary
- Chosen policy: **B. Mandatory Query + Optional Reliance**
- This preserves PECS consultation and observability while recognizing current evidence gaps.
- It avoids overcommitting to the under-fused continuity export.
