from biolink_model_pydantic.model import (
    Disease,
    DiseaseToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
)
from koza.manager.data_collector import write
from koza.manager.data_provider import inject_row, inject_translation_table
import uuid

# You've got 'NCBI_Gene:' and you want 'NCBIGene:'? clean it up.
#curie_cleaner = inject_curie_cleaner()

# The source name is used for reading and writing
source_name = "phenotype-hpoa"

translation_table = inject_translation_table()
# inject a single row from the source
row = inject_row(source_name)

# create your entities
phenotype = PhenotypicFeature(id=row["HPO_ID"])
disease = Disease(id=row["DatabaseID"])

association = DiseaseToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=disease.id,
        predicate=Predicate.has_phenotype,
        object=phenotype.id,
        relation=translation_table.resolve_term("has phenotype"),
        publications=[row["Reference"]],
#       evidence_type=[row["Evidence"]],
        onset_qualifier=[row["Onset"]],
    )
if row["Frequency"] != '':
      association.frequency_qualifier = row["Frequency"]

# populate any additional optional properties

# remember to supply the source name as the first argument, followed by entities
write(source_name, disease, phenotype, association)
#except:
#    print("Error!")

