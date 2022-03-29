from biolink_model_pydantic.model import LifeStage


def get_life_stage(species, stage_term) -> LifeStage:
    # TODO: need to have a better mapping of stage_term onto a proper CURIE?
    life_stage = LifeStage(id=stage_term, in_taxon=species)
    return life_stage
