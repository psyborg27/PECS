"""OntologyBuilder — builds the EngineeringOntology from the EngineeringKnowledgeBase.

Consumes the canonical knowledge base to produce a deterministic,
repository-derived engineering vocabulary.  No NLP, embeddings, or
probabilistic inference.
"""

from __future__ import annotations

import re
import logging
from typing import Any, Dict, List, Optional, Set

from pecs_query.knowledge.models import (
    ClassKnowledge,
    EngineeringKnowledgeBase,
    MethodKnowledge,
    ModuleKnowledge,
    PackageKnowledge,
    RuntimeKnowledge,
)
from pecs_query.ontology.models import (
    ConceptRelationshipType,
    EngineeringOntology,
    OntologyConcept,
    OntologyConceptRelationship,
)
from pecs_query.ontology.alias_generator import AliasGenerator, split_identifier

LOG = logging.getLogger(__name__)

# Minimum word length for concept generation
_MIN_CONCEPT_LENGTH = 2


class OntologyBuilder:
    """Builds the ``EngineeringOntology`` from the ``EngineeringKnowledgeBase``.

    Usage::

        builder = OntologyBuilder()
        ontology = builder.build(knowledge_base)
    """

    def __init__(self) -> None:
        self.ontology = EngineeringOntology()
        self._concepts_created: int = 0
        self._relationships_created: int = 0
        self._name_map: Dict[str, Set[str]] = {}  # name → {concept_ids}
        self._pecs_id_to_concepts: Dict[str, Set[str]] = {}  # pecs_id → {concept_ids}

    # ── build ────────────────────────────────────────────────────────────

    def build(
        self,
        kb: EngineeringKnowledgeBase,
    ) -> EngineeringOntology:
        """Build the ontology from a knowledge base."""
        self.ontology = EngineeringOntology()
        self._concepts_created = 0
        self._relationships_created = 0
        self._name_map = {}
        self._pecs_id_to_concepts = {}

        # Phase 1: Create concepts from each knowledge source
        self._build_package_concepts(kb)
        self._build_module_concepts(kb)
        self._build_class_concepts(kb)
        self._build_method_concepts(kb)
        self._build_runtime_concepts(kb)
        self._build_feature_concepts(kb)

        # Phase 2: Build concept relationships
        self._build_synonym_relationships()
        self._build_namespace_relationships(kb)

        # Phase 3: Build PECS_ID index
        self._build_pecs_id_index()

        # Phase 4: Populate diagnostics
        self.ontology.build_diagnostics = {
            "concepts_created": self._concepts_created,
            "relationships_created": self._relationships_created,
            "kb_packages": len(kb.packages),
            "kb_modules": len(kb.modules),
            "kb_classes": len(kb.classes),
            "kb_methods": len(kb.methods),
            "kb_runtime_objects": len(kb.runtime_objects),
        }

        return self.ontology

    # ── concept creation helpers ─────────────────────────────────────────

    def _concept_id_from_name(self, name: str) -> str:
        """Create a deterministic concept_id from a name."""
        return re.sub(r"[^a-z0-9_]", "", name.lower().replace(" ", "_").replace("-", "_"))

    def _register_concept(
        self,
        concept_id: str,
        canonical_name: str,
        aliases: List[str],
        pecs_ids: List[str],
        object_types: List[str],
        provenance: str,
    ) -> str:
        """Create or merge a concept, returning its concept_id."""
        if concept_id in self.ontology.concepts:
            existing = self.ontology.concepts[concept_id]
            # Merge PECS IDs
            existing_pecs = set(existing.engineering_object_ids)
            for pid in pecs_ids:
                if pid and pid not in existing_pecs:
                    existing.engineering_object_ids.append(pid)
                    existing_pecs.add(pid)
            # Merge object types
            for ot in object_types:
                if ot not in existing.object_types:
                    existing.object_types.append(ot)
            # Merge aliases
            for a in aliases:
                if a not in existing.aliases:
                    existing.aliases.append(a)
                    existing_ids = self.ontology.alias_index.setdefault(a, [])
                    if concept_id not in existing_ids:
                        existing_ids.append(concept_id)
            return concept_id

        # Track names for relationship building
        words = split_identifier(canonical_name)
        for word in words:
            if len(word) >= _MIN_CONCEPT_LENGTH:
                self._name_map.setdefault(word, set()).add(concept_id)

        concept = OntologyConcept(
            concept_id=concept_id,
            canonical_name=canonical_name,
            aliases=aliases,
            engineering_object_ids=list(dict.fromkeys(pecs_ids)),
            object_types=list(dict.fromkeys(object_types)),
            confidence=1.0,
            provenance=provenance,
        )
        self.ontology.concepts[concept_id] = concept
        for a in aliases:
            existing_ids = self.ontology.alias_index.setdefault(a, [])
            if concept_id not in existing_ids:
                existing_ids.append(concept_id)
        self._concepts_created += 1

        # Track PECS_ID → concept mapping
        for pid in pecs_ids:
            if pid:
                self._pecs_id_to_concepts.setdefault(pid, set()).add(concept_id)

        return concept_id

    # ── source-specific concept builders ────────────────────────────────

    def _build_package_concepts(self, kb: EngineeringKnowledgeBase) -> None:
        for pkg_name, pkg in kb.packages.items():
            cid = self._concept_id_from_name(pkg_name)
            aliases = AliasGenerator.from_package_name(pkg_name)
            self._register_concept(
                concept_id=cid,
                canonical_name=pkg_name,
                aliases=aliases,
                pecs_ids=pkg.pecs_ids,
                object_types=["package"],
                provenance="package",
            )

    def _build_module_concepts(self, kb: EngineeringKnowledgeBase) -> None:
        for pecs_id, mod in kb.modules.items():
            name = mod.module_path.split(".")[-1] if mod.module_path else pecs_id
            cid = self._concept_id_from_name(name)
            aliases = AliasGenerator.from_pecs_id(pecs_id)
            if mod.module_path:
                aliases.extend(AliasGenerator.from_module_path(mod.module_path))
            self._register_concept(
                concept_id=cid,
                canonical_name=name,
                aliases=aliases,
                pecs_ids=[pecs_id],
                object_types=["module"],
                provenance="module",
            )

    def _build_class_concepts(self, kb: EngineeringKnowledgeBase) -> None:
        for pecs_id, cls in kb.classes.items():
            name = cls.class_name
            cid = self._concept_id_from_name(name)
            aliases = AliasGenerator.from_class_name(name)
            self._register_concept(
                concept_id=cid,
                canonical_name=name,
                aliases=aliases,
                pecs_ids=[pecs_id],
                object_types=["class"],
                provenance="class",
            )

    def _build_method_concepts(self, kb: EngineeringKnowledgeBase) -> None:
        for pecs_id, method in kb.methods.items():
            name = method.method_name
            cid = self._concept_id_from_name(name)
            aliases = AliasGenerator.from_method_name(name)
            self._register_concept(
                concept_id=cid,
                canonical_name=name,
                aliases=aliases,
                pecs_ids=[pecs_id],
                object_types=["method", "function"],
                provenance="method",
            )

    def _build_runtime_concepts(self, kb: EngineeringKnowledgeBase) -> None:
        for pecs_id, rt in kb.runtime_objects.items():
            name = rt.canonical_name or pecs_id.split(".")[-1]
            cid = self._concept_id_from_name(name)
            aliases = AliasGenerator.from_pecs_id(pecs_id)
            self._register_concept(
                concept_id=cid,
                canonical_name=name,
                aliases=aliases,
                pecs_ids=[pecs_id],
                object_types=[rt.node_type],
                provenance="runtime",
            )

    def _build_feature_concepts(self, kb: EngineeringKnowledgeBase) -> None:
        """Register feature IDs from registry as concepts."""
        for pkg_name, pkg in kb.packages.items():
            if pkg.is_user_facing:
                cid = self._concept_id_from_name(pkg_name)
                # Concept may already exist from _build_package_concepts.
                # This call adds feature provenance metadata.
                if cid in self.ontology.concepts:
                    existing = self.ontology.concepts[cid]
                    if "feature" not in existing.provenance:
                        existing.provenance = f"{existing.provenance},feature"
                    if pkg.feature_id and pkg.feature_id not in existing.metadata:
                        existing.metadata["feature_id"] = pkg.feature_id

    # ── relationships ────────────────────────────────────────────────────

    def _add_relationship(
        self,
        source: str,
        target: str,
        rel_type: str,
        evidence: str,
        confidence: float = 1.0,
    ) -> None:
        rel = OntologyConceptRelationship(
            source_concept_id=source,
            target_concept_id=target,
            relationship_type=rel_type,
            evidence=evidence,
            confidence=confidence,
        )
        self.ontology.concept_relationships.append(rel)
        self._relationships_created += 1

    def _build_synonym_relationships(self) -> None:
        """Create synonym relationships between concepts that share PECS_IDs."""
        for pid, concept_ids in self._pecs_id_to_concepts.items():
            ids = list(concept_ids)
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    self._add_relationship(
                        source=ids[i],
                        target=ids[j],
                        rel_type=ConceptRelationshipType.SAME_AS,
                        evidence="alias_overlap",
                        confidence=0.8,
                    )

    def _build_namespace_relationships(
        self, kb: EngineeringKnowledgeBase
    ) -> None:
        """Create parent/child and contains relationships from namespaces.

        For every pair of concepts where one name contains the other as a
        prefix, create a PARENT/CHILD or CONTAINS/BELONGS_TO relationship.
        """
        seen: Set[tuple] = set()
        for word, concept_ids in self._name_map.items():
            ids = list(concept_ids)
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    key = (ids[i], ids[j])
                    if key in seen:
                        continue
                    seen.add(key)
                    # Direct prefix overlap → RELATED
                    self._add_relationship(
                        source=ids[i],
                        target=ids[j],
                        rel_type=ConceptRelationshipType.RELATED,
                        evidence="name_prefix",
                        confidence=0.5,
                    )

    # ── PECS_ID index ────────────────────────────────────────────────────

    def _build_pecs_id_index(self) -> None:
        """Build the reverse PECS_ID → concept_ids index."""
        for concept_id, concept in self.ontology.concepts.items():
            for pid in concept.engineering_object_ids:
                self.ontology.pecs_id_index.setdefault(pid, []).append(concept_id)


def build_ontology(kb: EngineeringKnowledgeBase) -> EngineeringOntology:
    """One-shot convenience: build the ontology from a knowledge base."""
    builder = OntologyBuilder()
    return builder.build(kb)
