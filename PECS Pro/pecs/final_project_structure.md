# FINAL PECS STRUCTURE

```text
pecs/

  core/
    registry.py
    workspace_scanner.py
    object_model.py

  ingestion/
    chat_ingestion.py

  continuity/
    object_engine.py
    retrieval_engine.py

  runtime/
    final_runtime_core.py
    runtime_cache.py
    live_continuity_daemon.py
    pecs_incremental_update_engine.py
    pecs_runtime_overlay_manager.py

  integrations/
    continue_adapter.py

  tools/
    pecs_testing_console.py

  lite/
    pecs_lite_registry.py
    pecs_lite_runtime_core.py
    pecs_lite_runtime_cache.py
    pecs_lite_continue_adapter.py

  exports/
    exporter.py
```

---

# REMOVE COMPLETELY

Remove from runtime path:

- pecs_user_intent_stabilizer.py
- pecs_architectural_drift_detector.py
- pecs_convergence_advisor.py

---

# REMOVE DUPLICATES

Remove:
- duplicate exporters
- duplicate registries
- duplicate workspace scanners
- duplicate runtime bridges
- duplicate daemons
- duplicate retrieval wrappers
- duplicate Continue adapters

---

# FINAL PECS PRINCIPLES

PECS should:

- reconstruct continuity
- enforce canonical locality
- compact runtime context
- prevent duplicate implementations
- stabilize engineering continuity

PECS should NOT:

- semantically supervise models
- recursively reason
- autonomously arbitrate architecture
- become an agent framework
