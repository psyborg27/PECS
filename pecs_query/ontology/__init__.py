"""Engineering Ontology package — deterministic repository-derived engineering vocabulary.

The ontology provides the canonical engineering vocabulary used by the
Engineering Object Resolution stage.  It is built entirely from existing
PECS artifacts without NLP, embeddings, or probabilistic inference.
"""

from pecs_query.ontology.models import (
    EngineeringOntology,
    OntologyConcept,
    OntologyConceptRelationship,
    OntologyStatistics,
)
from pecs_query.ontology.alias_generator import AliasGenerator
from pecs_query.ontology.builder import OntologyBuilder
from pecs_query.ontology.queries import OntologyQueryAPI

__all__ = [
    "EngineeringOntology",
    "OntologyConcept",
    "OntologyConceptRelationship",
    "OntologyStatistics",
    "AliasGenerator",
    "OntologyBuilder",
    "OntologyQueryAPI",
]
