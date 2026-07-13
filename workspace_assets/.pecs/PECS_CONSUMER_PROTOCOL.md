# PECS Consumer Protocol

This document defines the shared canonical workflow for all supported PECS consumer agents:
- Copilot
- Continue
- Kimi
- Command Code

## Core Protocol

1. Construct a canonical PECS query.
   - Include consumer identity, model identity, query source, and projection profile hints.
   - Preserve the consumer-specific query source value: `copilot`, `continue`, `kimi`, or `commandcode`.

2. Query PECS before broad workspace search.
   - Use the stateless PECS-LITE query path first.
   - Do not perform unnecessary repository-wide search until PECS locality projection is available.

3. Record the exact PECS query.
   - Persist the query text in the consumer runtime event or telemetry payload.
   - Include the query source and model identity inputs.

4. Report the PECS response or response identifier.
   - Preserve the returned PECS-LITE projection schema.
   - If the projection contains a response identifier, include it in the consumer report.

5. Report whether the PECS response was used.
   - Indicate whether the projection guided subsequent analysis or edits.
   - If the response was not used, record the reason.

6. Report modified artifacts.
   - List modified files.
   - List modified classes.
   - List modified methods/functions.

7. Report completion status.
   - Indicate whether the consumer completed the task.
   - When applicable, emit a final completion event or acknowledgement.

8. Avoid unnecessary workspace search after authoritative PECS ownership.
   - Respect runtime locality authority from PECS-provided projections.
   - Only fall back to broader search if PECS is insufficient or inapplicable.

## Consumer Guidance

- Use this shared protocol as the authoritative consumer workflow.
- Consumer-specific configuration assets should only contain the minimal guidance needed for that agent and should reference this document.
- Do not duplicate the full protocol text in multiple files.

## Installation

This file is installed into the target workspace at `.pecs/PECS_CONSUMER_PROTOCOL.md`.
Consumer instructions should reference that path.
