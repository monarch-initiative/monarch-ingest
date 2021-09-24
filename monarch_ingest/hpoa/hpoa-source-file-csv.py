from biolink_model_pydantic.model import Attribute, Disease, PhenotypicFeature, Predicate, DiseaseToPhenotypicFeatureAssociation
from koza.manager.data_collector import write
from koza.manager.data_provider import inject_curie_cleaner, inject_row, inject_map, inject_translation_table
import uuid

# You've got 'NCBI_Gene:' and you want 'NCBIGene:'? clean it up.
curie_cleaner = inject_curie_cleaner()
eco2go = inject_map("eco2go")

# The source name is used for reading and writing
source_name = "hpoa"

# inject a single row from the source
row = inject_row(source_name)
translation_table = inject_translation_table()

#
# # create your entities
# DatabaseID	DiseaseName	Qualifier	HPO_ID	Reference	Evidence	Onset	Frequency	Sex	Modifier	Aspect	Biocuration

disease = Disease(
    id=row['DatabaseID']
)

phenotypic_feature = PhenotypicFeature(
    id=row['HPO_ID']
)

association = DiseaseToPhenotypicFeatureAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=disease.id,
    predicate=Predicate.has_phenotype,
    object=phenotypic_feature.id,
    relation=translation_table.resolve_term("has phenotype"),
    publications=[row["Reference"]],
    qualifiers=[row["Evidence"]],
    
)



# gene = Gene(
#     id='somethingbase:'+row['ID'],
#     name=row['Name']
# )
#
# # populate any additional optional properties
# if row['xrefs']:
#     gene.xrefs = [curie_cleaner.clean(xref) for xref in row['xrefs']]
#
# # remember to supply the source name as the first argument, followed by entities
# write(source_name, gene)
