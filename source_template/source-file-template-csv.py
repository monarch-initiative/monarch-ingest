from biolink_model_pydantic.model import Gene
from koza.manager.data_collector import write
from koza.manager.data_provider import inject_curie_cleaner, inject_row

# You've got 'NCBI_Gene:' and you want 'NCBIGene:'? clean it up.
curie_cleaner = inject_curie_cleaner()

# The source name is used for reading and writing
source_name = "gene-information"

# inject a single row from the source
row = inject_row(source_name)

# create your entities
gene = Gene(
    id='somethingbase:'+row['ID'],
    name=row['Name']
)

# populate any additional optional properties
if row['xrefs']:
    gene.xrefs = [curie_cleaner.clean(xref) for xref in row['xrefs']]

# remember to supply the source name as the first argument, followed by entities
write(source_name, gene)
