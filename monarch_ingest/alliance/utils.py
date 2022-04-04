from typing import Optional


def get_data(entry, path) -> Optional[str]:
    """
    Given a dot delimited JSON tag path,
    returns the value of the field in the entry.

    :param entry:
    :param path:
    :return: str value of the given path into the entry
    """
    if path in entry:
        return entry[path]
    else:
        return None


# NCBI Taxon Id mapping onto database
# TODO: what about 'one-to-many' db to multiple taxa?
_taxon_by_db = {
    "ZFIN": "7955"
}


def get_taxon(db) -> Optional[str]:
    global _taxon_by_db
    if db in _taxon_by_db:
        return _taxon_by_db[db]
    else:
        return None

# Zebrafish (ZFIN) life stages (https://zfin.org/zf_info/zfbook/stages/)
# are things like "Segmentation:10-13 somites" and "Hatching:Long-pec"

# Mouse (MGI) life stages are the Theiler stages of embryonic development, e.g. TS27

# Drosophila fly stages (if given) are things like "embryonic stage 10"

#
# This LifeStage heuristic code is deprecated
# (Alliance schema formatted data has mapped the required life stage terms)
#
# def get_life_stage(db: str, ncbi_taxon_id: str, stage_term: str, source: str) -> Optional[LifeStage]:
#     if not stage_term:
#         return None
#     else:
#         # Pre-pend the namespace and replace spaces with underscores?
#         stage_term_id = f"{db}:{stage_term.replace(' ','_')}"
#         life_stage = LifeStage(id=stage_term_id, name=stage_term, in_taxon=ncbi_taxon_id, source=source)
#         return life_stage
