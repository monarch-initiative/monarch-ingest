##########################################
# STRING ingest utility functions
##########################################
from typing import Dict, List

#
# Mapping of STRING evidence type score fields to evidence & conclusion codes (with definitions)
#
#
# "neighborhood" score, (computed from the inter-gene nucleotide count) - ECO:0000044: SEQUENCE SIMILARITY EVIDENCE.
# A sequence similarity analysis may involve a gene or a gene product, and it could be based on similarity
# to a single other gene or to a group of other genes.
#
# "fusion" score (derived from fused proteins in other species)
# - ECO:0000124: FUSION PROTEIN LOCALIZATION EVIDENCE.
# A type of protein localization evidence resulting from the fusion of a protein of interest
# to a labeling protein which has enzymatic activity or fluorescence properties.
#
# "cooccurrence" score of the phyletic profile (derived from similar absence/presence patterns of genes)
# ECO:0000080:PHYLOGENETIC EVIDENCE.
# A type of similarity that indicates common ancestry.
#
# "coexpression" score (derived from similar pattern of mRNA expression measured by DNA arrays and similar technologies)
# ECO:0000075: GENE EXPRESSION SIMILARITY EVIDENCE.
# A type of phenotypic similarity evidence that is based on the
# categorization of genes by the similarity of expression profiles.
#
# "experimental" score (derived from experimental data, such as, affinity chromatography)
# ECO:0000006: EXPERIMENTAL EVIDENCE.
# experimental evidence: A type of evidence that is the output of a scientific procedure
# performed to make a discovery, test a hypothesis, or demonstrate a known fact.
#
# "database" score (derived from curated data of various databases)
# ECO:0007636: CURATOR INFERENCE FROM DATABASE.
# A type of curator inference from authoritative resource based
# on information located in a queryable database and is optimized for computers.
#
# "textmining" score (derived from the co-occurrence of gene/protein names in abstracts)
# ECO:0007833: CURATOR INFERENCE FROM AUTHORITATIVE SOURCE USED IN AUTOMATIC ASSERTION.
# A type of curator inference from authoritative source that is used in an automatic assertion.

EVIDENCE_CODE_MAPPINGS = {
    "neighborhood": "ECO:0000044",
    "fusion": "ECO:0000124",
    "cooccurence": "ECO:0000080",
    "coexpression": "ECO:0000075",
    "experimental": "ECO:0000006",
    "database": "ECO:0007636",
    "textmining": "ECO:0007833"
}


def map_evidence_codes(row: Dict) -> List[str]:
    eco_mappings: List[str] = list()
    for evidence_type in EVIDENCE_CODE_MAPPINGS.keys():
        if int(row[evidence_type]) > 0:
            eco_mappings.append(EVIDENCE_CODE_MAPPINGS[evidence_type])

    return eco_mappings

