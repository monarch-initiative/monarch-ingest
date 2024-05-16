"""
Some functions to assist parsing of BioGRID fields.
"""

from typing import List, Optional

from loguru import logger


def get_gene_id(raw_id: str) -> str:
    """
    Parse in the specified gene identifier.

    :param raw_id: str, raw BioGRID input string (a pseudo-CURIE)
    :return:
    """
    gid = raw_id.replace("entrez gene/locuslink:", "NCBIGene:").replace("uniprot/swiss-prot:", "UniProtKB:")

    return gid


EVIDENCE_CODE_MAPPINGS = {
    # See also BioGRID definitions at https://wiki.thebiogrid.org/doku.php/experimental_systems
    "experimental": "ECO:0000006",
    "two hybrid": "ECO:0000024",
    "affinity chromatography technology": "ECO:0000079",
    "genetic interference": "ECO:0000011",
    "pull down": "ECO:0000025",  # not totally sure about this one
    "enzymatic study": "ECO:0000005",
    "x-ray crystallography": "ECO:0001823",
    "far western blotting": "ECO:0000076",
    "fluorescent resonance energy transfer": "ECO:0001048",
    "imaging technique": "ECO:0000324",  # not totally sure about this one
    "protein complementation assay": "ECO:0006256",  # not totally sure about this one
    "biochemical": "ECO:0000172",  # not totally sure about this one
}


def get_evidence(methods: str) -> Optional[List[str]]:
    """
    Parse in the specified interaction detection methods as a kind of evidence indication.

    :param methods: str, pipe ('|') delimited string of BioGRID interaction detection method encodings.
    :return: List[str], evidence codes
    """
    evidence_codes: List[str] = list()
    if methods:
        for method in methods.split("|"):
            # Sanity check...
            if not method:
                continue
            # databaseName:identifier(methodName)
            method = method.rstrip(")").split('(')[-1]
            if method not in EVIDENCE_CODE_MAPPINGS.keys():
                err_msg = (
                    f"Unknown interaction detection method '{method}'. "
                    + "Assigning default code ECO:0000006 == 'experimental evidence', the ECO root."
                )
                logger.warning(err_msg)
                EVIDENCE_CODE_MAPPINGS[method] = "ECO:0000006"

            evidence_codes.append(EVIDENCE_CODE_MAPPINGS[method])

    return evidence_codes if evidence_codes else None


def get_publication_ids(pub_ids: str) -> List[str]:
    """
    Parse the publication field.
    Simpleminded assumptions:
    - Just parse PMID's that have CURIEs of form 'pubmed:#######'
    - Not sure if this field is multivalued in practice (the column name implies that),
     but if so, one might expect it to be pipe ('|') delimited (if the "Alt IDs*" columns are an indication)

    :param pub_ids: str, raw input column from BioGRID
    :return: List[str], of PMIDs
    """
    publications: List[str] = [pmid.replace("pubmed", "PMID") for pmid in pub_ids.split("|")]
    return publications
