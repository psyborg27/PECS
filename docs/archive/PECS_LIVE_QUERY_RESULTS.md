# PECS Live Query Results

## Common Diagnostics

```json
{
  "health": {
    "artifacts_loaded": 6,
    "activated_object_count": 14,
    "touched_file_count": 0,
    "bundle_entry_count": 0,
    "locality_cluster_count": 12,
    "runtime_zone_count": 3,
    "engineering_chain_count": 3
  },
  "diagnostics": {
    "queried_pecs_pro": true,
    "workspace_scan_performed": false,
    "projection_mode": "query_driven"
  }
}
```

## Query 1

**Issue query:** Clipboard paste not working in Notes Module.

### Runtime targets

Returned `runtime_targets` in retrieved order:

```json
[
  {
    "file": "install_workspace_integration.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.228,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 0.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.38,
      "tier_3_validation": 0.667
    },
    "evidence_sources": {
      "tier_0_static": [],
      "tier_1_runtime": [],
      "tier_2_continuity": [
        "continuity_hotspots",
        "engineering_continuity_chain"
      ],
      "tier_3_validation": [
        "accepted_rejected_fix_validation",
        "error_to_object_correlation"
      ]
    },
    "provenance": [
      "accepted_rejected_fix_validation",
      "continuity_hotspots",
      "engineering_continuity_chain",
      "error_to_object_correlation"
    ]
  },
  {
    "file": "workspace_bridge_cli.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.228,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 0.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.38,
      "tier_3_validation": 0.667
    },
    "evidence_sources": {
      "tier_0_static": [],
      "tier_1_runtime": [],
      "tier_2_continuity": [
        "continuity_hotspots",
        "engineering_continuity_chain"
      ],
      "tier_3_validation": [
        "accepted_rejected_fix_validation",
        "error_to_object_correlation"
      ]
    },
    "provenance": [
      "accepted_rejected_fix_validation",
      "continuity_hotspots",
      "engineering_continuity_chain",
      "error_to_object_correlation"
    ]
  },
  {
    "file": "Qt/auto_toc_dialog_rewrite.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.212,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.048,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [
        "canonical_authority_cluster"
      ],
      "tier_3_validation": []
    },
    "provenance": [
      "canonical_authority_cluster",
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "EnhancedPDFViewer.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/__init__.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/auto_toc_dialog_rewrite_next.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/auto_toc_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/bulk_ocr_mapping_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/bulk_page_mapping_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/clipboard_harness.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/colors.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/easyocr_gpu_helper.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/extraction_worker.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/main_app_UI_rewrite.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/main_app_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/main_app_logic_unwired.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/mnist_trainer_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/normalize_tab.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/notes_clipboard.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/notes_module.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/notes_module_v2.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/ocr_module_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/page_mapping_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_page_viewer_with_overlay.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_pages_editor_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_recovery_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_thumbnail_browser.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_viewer_UI.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_viewer_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/portfolio_create_edit_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/replace_toc_pages_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/session_cache.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/session_clipboard_history.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/sticky_note_widget.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/textbox_annotation_widget.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/toc_tree_widget_optionA.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_api.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_export_import.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_manager.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_save.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "app_logging.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "assisted_toc_wizard_qt.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_camlt.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_camlt_v5_dialog_pipeline.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_v2_CASE_ABC.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_v2_CASE_ABC_next.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "autonumberer_qt.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "band_detection_fallback.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "band_overlay_manager.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "bookmark_writer.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  }
]
```

### Secondary neighbors

```json
[]
```

### Evidence fusion projection

```json
{
  "schema": "pecs.evidence_fusion.v1",
  "deterministic": true,
  "weights": {
    "tier_0_static": 0.2,
    "tier_1_runtime": 0.35,
    "tier_2_continuity": 0.25,
    "tier_3_validation": 0.2
  },
  "ranked_files": [
    {
      "file": "install_workspace_integration.py",
      "fused_score": 0.228,
      "tier_scores": {
        "tier_0_static": 0.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.38,
        "tier_3_validation": 0.667
      },
      "tier_sources": {
        "tier_0_static": [],
        "tier_1_runtime": [],
        "tier_2_continuity": [
          "continuity_hotspots",
          "engineering_continuity_chain"
        ],
        "tier_3_validation": [
          "accepted_rejected_fix_validation",
          "error_to_object_correlation"
        ]
      },
      "provenance": [
        "accepted_rejected_fix_validation",
        "continuity_hotspots",
        "engineering_continuity_chain",
        "error_to_object_correlation"
      ]
    },
    {
      "file": "workspace_bridge_cli.py",
      "fused_score": 0.228,
      "tier_scores": {
        "tier_0_static": 0.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.38,
        "tier_3_validation": 0.667
      },
      "tier_sources": {
        "tier_0_static": [],
        "tier_1_runtime": [],
        "tier_2_continuity": [
          "continuity_hotspots",
          "engineering_continuity_chain"
        ],
        "tier_3_validation": [
          "accepted_rejected_fix_validation",
          "error_to_object_correlation"
        ]
      },
      "provenance": [
        "accepted_rejected_fix_validation",
        "continuity_hotspots",
        "engineering_continuity_chain",
        "error_to_object_correlation"
      ]
    },
    {
      "file": "Qt/auto_toc_dialog_rewrite.py",
      "fused_score": 0.212,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.048,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [
          "canonical_authority_cluster"
        ],
        "tier_3_validation": []
      },
      "provenance": [
        "canonical_authority_cluster",
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "EnhancedPDFViewer.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/__init__.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/auto_toc_dialog_rewrite_next.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/auto_toc_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/bulk_ocr_mapping_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/bulk_page_mapping_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/clipboard_harness.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/colors.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/easyocr_gpu_helper.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/extraction_worker.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/main_app_UI_rewrite.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/main_app_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/main_app_logic_unwired.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/mnist_trainer_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/normalize_tab.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/notes_clipboard.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/notes_module.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/notes_module_v2.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/ocr_module_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/page_mapping_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_page_viewer_with_overlay.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_pages_editor_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_recovery_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_thumbnail_browser.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_viewer_UI.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_viewer_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/portfolio_create_edit_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/replace_toc_pages_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/session_cache.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/session_clipboard_history.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/sticky_note_widget.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/textbox_annotation_widget.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/toc_tree_widget_optionA.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_api.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_export_import.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_manager.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_save.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "app_logging.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "assisted_toc_wizard_qt.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_camlt.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_camlt_v5_dialog_pipeline.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_v2_CASE_ABC.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_v2_CASE_ABC_next.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "autonumberer_qt.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "band_detection_fallback.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "band_overlay_manager.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "bookmark_writer.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    }
  ]
}
```

### Engineering continuity evidence

```json
{
  "schema": "pecs.engineering_continuity_projection.v1",
  "active_engineering_chains": [],
  "accepted_locality_scores": {},
  "rejected_locality_scores": {},
  "runtime_confirmed_locality_scores": {},
  "continuity_survivability_scores": {},
  "locality_authority_scores": {},
  "duplicate_shadow_scores": {},
  "dead_execution_path_scores": {},
  "topology_mismatch_scores": {},
  "runtime_confirmed_locality": false,
  "locality_authority_confidence": 0.0,
  "continuity_survivability_confidence": 0.0,
  "duplicate_shadow_suspicion": 0.0,
  "dead_execution_path_suspicion": 0.0,
  "topology_mismatch_suspicion": 0.0,
  "has_high_confidence_continuity": false
}
```

### Active continuity snapshot

```json
{
  "active_topology_zone": "overlay_pipeline",
  "active_runtime_zones": [
    "locality",
    "overlay_pipeline",
    "topology"
  ],
  "active_context_size": 14,
  "locality_cluster_count": 12,
  "runtime_confirmation_density": 0.0,
  "engineering_chain_count": 3
}
```

### Ownership locality

- `PECS_ID:Qt.main_app_UI_rewrite`

### Advisory and diagnostics

- `wrapper_warning`: False
- `execution_depth`: deep

---

## Query 2

**Issue query:** Cmd+A selects all notes instead of all text in active frame.

### Runtime targets

Returned `runtime_targets` in retrieved order:

```json
[
  {
    "file": "install_workspace_integration.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.228,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 0.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.38,
      "tier_3_validation": 0.667
    },
    "evidence_sources": {
      "tier_0_static": [],
      "tier_1_runtime": [],
      "tier_2_continuity": [
        "continuity_hotspots",
        "engineering_continuity_chain"
      ],
      "tier_3_validation": [
        "accepted_rejected_fix_validation",
        "error_to_object_correlation"
      ]
    },
    "provenance": [
      "accepted_rejected_fix_validation",
      "continuity_hotspots",
      "engineering_continuity_chain",
      "error_to_object_correlation"
    ]
  },
  {
    "file": "workspace_bridge_cli.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.228,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 0.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.38,
      "tier_3_validation": 0.667
    },
    "evidence_sources": {
      "tier_0_static": [],
      "tier_1_runtime": [],
      "tier_2_continuity": [
        "continuity_hotspots",
        "engineering_continuity_chain"
      ],
      "tier_3_validation": [
        "accepted_rejected_fix_validation",
        "error_to_object_correlation"
      ]
    },
    "provenance": [
      "accepted_rejected_fix_validation",
      "continuity_hotspots",
      "engineering_continuity_chain",
      "error_to_object_correlation"
    ]
  },
  {
    "file": "Qt/auto_toc_dialog_rewrite.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.212,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.048,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [
        "canonical_authority_cluster"
      ],
      "tier_3_validation": []
    },
    "provenance": [
      "canonical_authority_cluster",
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "EnhancedPDFViewer.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/__init__.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/auto_toc_dialog_rewrite_next.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/auto_toc_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/bulk_ocr_mapping_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/bulk_page_mapping_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/clipboard_harness.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/colors.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/easyocr_gpu_helper.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/extraction_worker.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/main_app_UI_rewrite.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/main_app_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/main_app_logic_unwired.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/mnist_trainer_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/normalize_tab.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/notes_clipboard.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/notes_module.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/notes_module_v2.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/ocr_module_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/page_mapping_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_page_viewer_with_overlay.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_pages_editor_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_recovery_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_thumbnail_browser.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_viewer_UI.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_viewer_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/portfolio_create_edit_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/replace_toc_pages_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/session_cache.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/session_clipboard_history.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/sticky_note_widget.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/textbox_annotation_widget.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/toc_tree_widget_optionA.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_api.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_export_import.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_manager.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_save.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "app_logging.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "assisted_toc_wizard_qt.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_camlt.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_camlt_v5_dialog_pipeline.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_v2_CASE_ABC.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_v2_CASE_ABC_next.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "autonumberer_qt.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "band_detection_fallback.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "band_overlay_manager.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "bookmark_writer.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  }
]
```

### Secondary neighbors

```json
[]
```

### Evidence fusion projection

```json
{
  "schema": "pecs.evidence_fusion.v1",
  "deterministic": true,
  "weights": {
    "tier_0_static": 0.2,
    "tier_1_runtime": 0.35,
    "tier_2_continuity": 0.25,
    "tier_3_validation": 0.2
  },
  "ranked_files": [
    {
      "file": "install_workspace_integration.py",
      "fused_score": 0.228,
      "tier_scores": {
        "tier_0_static": 0.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.38,
        "tier_3_validation": 0.667
      },
      "tier_sources": {
        "tier_0_static": [],
        "tier_1_runtime": [],
        "tier_2_continuity": [
          "continuity_hotspots",
          "engineering_continuity_chain"
        ],
        "tier_3_validation": [
          "accepted_rejected_fix_validation",
          "error_to_object_correlation"
        ]
      },
      "provenance": [
        "accepted_rejected_fix_validation",
        "continuity_hotspots",
        "engineering_continuity_chain",
        "error_to_object_correlation"
      ]
    },
    {
      "file": "workspace_bridge_cli.py",
      "fused_score": 0.228,
      "tier_scores": {
        "tier_0_static": 0.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.38,
        "tier_3_validation": 0.667
      },
      "tier_sources": {
        "tier_0_static": [],
        "tier_1_runtime": [],
        "tier_2_continuity": [
          "continuity_hotspots",
          "engineering_continuity_chain"
        ],
        "tier_3_validation": [
          "accepted_rejected_fix_validation",
          "error_to_object_correlation"
        ]
      },
      "provenance": [
        "accepted_rejected_fix_validation",
        "continuity_hotspots",
        "engineering_continuity_chain",
        "error_to_object_correlation"
      ]
    },
    {
      "file": "Qt/auto_toc_dialog_rewrite.py",
      "fused_score": 0.212,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.048,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [
          "canonical_authority_cluster"
        ],
        "tier_3_validation": []
      },
      "provenance": [
        "canonical_authority_cluster",
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "EnhancedPDFViewer.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/__init__.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/auto_toc_dialog_rewrite_next.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/auto_toc_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/bulk_ocr_mapping_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/bulk_page_mapping_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/clipboard_harness.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/colors.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/easyocr_gpu_helper.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/extraction_worker.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/main_app_UI_rewrite.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/main_app_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/main_app_logic_unwired.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/mnist_trainer_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/normalize_tab.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/notes_clipboard.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/notes_module.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/notes_module_v2.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/ocr_module_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/page_mapping_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_page_viewer_with_overlay.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_pages_editor_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_recovery_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_thumbnail_browser.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_viewer_UI.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_viewer_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/portfolio_create_edit_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/replace_toc_pages_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/session_cache.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/session_clipboard_history.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/sticky_note_widget.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/textbox_annotation_widget.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/toc_tree_widget_optionA.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_api.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_export_import.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_manager.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_save.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "app_logging.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "assisted_toc_wizard_qt.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_camlt.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_camlt_v5_dialog_pipeline.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_v2_CASE_ABC.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_v2_CASE_ABC_next.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "autonumberer_qt.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "band_detection_fallback.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "band_overlay_manager.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "bookmark_writer.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    }
  ]
}
```

### Engineering continuity evidence

```json
{
  "schema": "pecs.engineering_continuity_projection.v1",
  "active_engineering_chains": [],
  "accepted_locality_scores": {},
  "rejected_locality_scores": {},
  "runtime_confirmed_locality_scores": {},
  "continuity_survivability_scores": {},
  "locality_authority_scores": {},
  "duplicate_shadow_scores": {},
  "dead_execution_path_scores": {},
  "topology_mismatch_scores": {},
  "runtime_confirmed_locality": false,
  "locality_authority_confidence": 0.0,
  "continuity_survivability_confidence": 0.0,
  "duplicate_shadow_suspicion": 0.0,
  "dead_execution_path_suspicion": 0.0,
  "topology_mismatch_suspicion": 0.0,
  "has_high_confidence_continuity": false
}
```

### Active continuity snapshot

```json
{
  "active_topology_zone": "overlay_pipeline",
  "active_runtime_zones": [
    "locality",
    "overlay_pipeline",
    "topology"
  ],
  "active_context_size": 14,
  "locality_cluster_count": 12,
  "runtime_confirmation_density": 0.0,
  "engineering_chain_count": 3
}
```

### Ownership locality

- `PECS_ID:Qt.main_app_UI_rewrite`

### Advisory and diagnostics

- `wrapper_warning`: False
- `execution_depth`: deep

---

## Query 3

**Issue query:** Notes Module modularization and ownership extraction.

### Runtime targets

Returned `runtime_targets` in retrieved order:

```json
[
  {
    "file": "install_workspace_integration.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.228,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 0.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.38,
      "tier_3_validation": 0.667
    },
    "evidence_sources": {
      "tier_0_static": [],
      "tier_1_runtime": [],
      "tier_2_continuity": [
        "continuity_hotspots",
        "engineering_continuity_chain"
      ],
      "tier_3_validation": [
        "accepted_rejected_fix_validation",
        "error_to_object_correlation"
      ]
    },
    "provenance": [
      "accepted_rejected_fix_validation",
      "continuity_hotspots",
      "engineering_continuity_chain",
      "error_to_object_correlation"
    ]
  },
  {
    "file": "workspace_bridge_cli.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.228,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 0.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.38,
      "tier_3_validation": 0.667
    },
    "evidence_sources": {
      "tier_0_static": [],
      "tier_1_runtime": [],
      "tier_2_continuity": [
        "continuity_hotspots",
        "engineering_continuity_chain"
      ],
      "tier_3_validation": [
        "accepted_rejected_fix_validation",
        "error_to_object_correlation"
      ]
    },
    "provenance": [
      "accepted_rejected_fix_validation",
      "continuity_hotspots",
      "engineering_continuity_chain",
      "error_to_object_correlation"
    ]
  },
  {
    "file": "Qt/auto_toc_dialog_rewrite.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.212,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.048,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [
        "canonical_authority_cluster"
      ],
      "tier_3_validation": []
    },
    "provenance": [
      "canonical_authority_cluster",
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "EnhancedPDFViewer.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/__init__.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/auto_toc_dialog_rewrite_next.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/auto_toc_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/bulk_ocr_mapping_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/bulk_page_mapping_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/clipboard_harness.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/colors.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/easyocr_gpu_helper.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/extraction_worker.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/main_app_UI_rewrite.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/main_app_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/main_app_logic_unwired.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/mnist_trainer_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/normalize_tab.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/notes_clipboard.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/notes_module.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/notes_module_v2.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/ocr_module_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/page_mapping_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_page_viewer_with_overlay.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_pages_editor_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_recovery_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_thumbnail_browser.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_viewer_UI.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/pdf_viewer_logic.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/portfolio_create_edit_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/replace_toc_pages_dialog.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/session_cache.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/session_clipboard_history.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/sticky_note_widget.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/textbox_annotation_widget.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "Qt/toc_tree_widget_optionA.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_api.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_export_import.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_manager.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "annotation_save.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "app_logging.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "assisted_toc_wizard_qt.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_camlt.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_camlt_v5_dialog_pipeline.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_v2_CASE_ABC.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "auto_toc_v2_CASE_ABC_next.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "autonumberer_qt.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "band_detection_fallback.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "band_overlay_manager.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  },
  {
    "file": "bookmark_writer.py",
    "evidence": "evidence_fusion",
    "base_confidence": 0.2,
    "is_active": false,
    "tier_scores": {
      "tier_0_static": 1.0,
      "tier_1_runtime": 0.0,
      "tier_2_continuity": 0.0,
      "tier_3_validation": 0.0
    },
    "evidence_sources": {
      "tier_0_static": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ],
      "tier_1_runtime": [],
      "tier_2_continuity": [],
      "tier_3_validation": []
    },
    "provenance": [
      "dependency_topology",
      "filesystem_structure",
      "import_topology"
    ]
  }
]
```

### Secondary neighbors

```json
[]
```

### Evidence fusion projection

```json
{
  "schema": "pecs.evidence_fusion.v1",
  "deterministic": true,
  "weights": {
    "tier_0_static": 0.2,
    "tier_1_runtime": 0.35,
    "tier_2_continuity": 0.25,
    "tier_3_validation": 0.2
  },
  "ranked_files": [
    {
      "file": "install_workspace_integration.py",
      "fused_score": 0.228,
      "tier_scores": {
        "tier_0_static": 0.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.38,
        "tier_3_validation": 0.667
      },
      "tier_sources": {
        "tier_0_static": [],
        "tier_1_runtime": [],
        "tier_2_continuity": [
          "continuity_hotspots",
          "engineering_continuity_chain"
        ],
        "tier_3_validation": [
          "accepted_rejected_fix_validation",
          "error_to_object_correlation"
        ]
      },
      "provenance": [
        "accepted_rejected_fix_validation",
        "continuity_hotspots",
        "engineering_continuity_chain",
        "error_to_object_correlation"
      ]
    },
    {
      "file": "workspace_bridge_cli.py",
      "fused_score": 0.228,
      "tier_scores": {
        "tier_0_static": 0.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.38,
        "tier_3_validation": 0.667
      },
      "tier_sources": {
        "tier_0_static": [],
        "tier_1_runtime": [],
        "tier_2_continuity": [
          "continuity_hotspots",
          "engineering_continuity_chain"
        ],
        "tier_3_validation": [
          "accepted_rejected_fix_validation",
          "error_to_object_correlation"
        ]
      },
      "provenance": [
        "accepted_rejected_fix_validation",
        "continuity_hotspots",
        "engineering_continuity_chain",
        "error_to_object_correlation"
      ]
    },
    {
      "file": "Qt/auto_toc_dialog_rewrite.py",
      "fused_score": 0.212,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.048,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [
          "canonical_authority_cluster"
        ],
        "tier_3_validation": []
      },
      "provenance": [
        "canonical_authority_cluster",
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "EnhancedPDFViewer.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/__init__.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/auto_toc_dialog_rewrite_next.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/auto_toc_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/bulk_ocr_mapping_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/bulk_page_mapping_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/clipboard_harness.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/colors.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/easyocr_gpu_helper.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/extraction_worker.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/main_app_UI_rewrite.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/main_app_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/main_app_logic_unwired.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/mnist_trainer_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/normalize_tab.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/notes_clipboard.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/notes_module.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/notes_module_v2.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/ocr_module_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/page_mapping_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_page_viewer_with_overlay.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_pages_editor_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_recovery_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_thumbnail_browser.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_viewer_UI.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/pdf_viewer_logic.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/portfolio_create_edit_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/replace_toc_pages_dialog.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/session_cache.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/session_clipboard_history.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/sticky_note_widget.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/textbox_annotation_widget.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "Qt/toc_tree_widget_optionA.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_api.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_export_import.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_manager.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "annotation_save.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "app_logging.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "assisted_toc_wizard_qt.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_camlt.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_camlt_v5_dialog_pipeline.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_v2_CASE_ABC.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "auto_toc_v2_CASE_ABC_next.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "autonumberer_qt.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "band_detection_fallback.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "band_overlay_manager.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    },
    {
      "file": "bookmark_writer.py",
      "fused_score": 0.2,
      "tier_scores": {
        "tier_0_static": 1.0,
        "tier_1_runtime": 0.0,
        "tier_2_continuity": 0.0,
        "tier_3_validation": 0.0
      },
      "tier_sources": {
        "tier_0_static": [
          "dependency_topology",
          "filesystem_structure",
          "import_topology"
        ],
        "tier_1_runtime": [],
        "tier_2_continuity": [],
        "tier_3_validation": []
      },
      "provenance": [
        "dependency_topology",
        "filesystem_structure",
        "import_topology"
      ]
    }
  ]
}
```

### Engineering continuity evidence

```json
{
  "schema": "pecs.engineering_continuity_projection.v1",
  "active_engineering_chains": [],
  "accepted_locality_scores": {},
  "rejected_locality_scores": {},
  "runtime_confirmed_locality_scores": {},
  "continuity_survivability_scores": {},
  "locality_authority_scores": {},
  "duplicate_shadow_scores": {},
  "dead_execution_path_scores": {},
  "topology_mismatch_scores": {},
  "runtime_confirmed_locality": false,
  "locality_authority_confidence": 0.0,
  "continuity_survivability_confidence": 0.0,
  "duplicate_shadow_suspicion": 0.0,
  "dead_execution_path_suspicion": 0.0,
  "topology_mismatch_suspicion": 0.0,
  "has_high_confidence_continuity": false
}
```

### Active continuity snapshot

```json
{
  "active_topology_zone": "overlay_pipeline",
  "active_runtime_zones": [
    "locality",
    "overlay_pipeline",
    "topology"
  ],
  "active_context_size": 14,
  "locality_cluster_count": 12,
  "runtime_confirmation_density": 0.0,
  "engineering_chain_count": 3
}
```

### Ownership locality

- `PECS_ID:Qt.main_app_UI_rewrite`

### Advisory and diagnostics

- `wrapper_warning`: False
- `execution_depth`: deep

---
