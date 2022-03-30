from typing import Optional
from biolink_model_pydantic.model import LifeStage

# Zebrafish (ZFIN) life stages (https://zfin.org/zf_info/zfbook/stages/)
# are things like "Segmentation:10-13 somites" and "Hatching:Long-pec"

# Mouse (MGI) life stages are the Theiler stages of embryonic development, e.g. TS27

# Drosophila fly stages (if given) are things like "embryonic stage 10"


def get_life_stage(db: str, ncbi_taxon_id: str, stage_term: str, source: str) -> Optional[LifeStage]:
    if not stage_term:
        return None
    else:
        # TODO: do we need to have a better mapping of stage_term's onto their proper CURIE?
        # Pre-pend the namespace and replace spaces with underscores?
        stage_term_id = f"{db}:{stage_term.replace(' ','_')}"
        life_stage = LifeStage(id=stage_term_id, in_taxon=ncbi_taxon_id, source=source)
        return life_stage
