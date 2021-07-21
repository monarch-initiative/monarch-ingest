from biolink_model_pydantic.model import Gene
from koza.manager.data_provider import inject_row, inject_curie_cleaner
from koza.manager.data_collector import write

curie_cleaner = inject_curie_cleaner()

source_name = 'gene-information'

row = inject_row(source_name)

# curie prefix as source?
source = row['basicGeneticEntity']['primaryId'].split(':')[0]

if 'name' not in row.keys():
    row['name'] = row['symbol']

gene = Gene(
    id=row['basicGeneticEntity']['primaryId'],
    symbol=row['symbol'],
    name=row['name'],
    in_taxon=row['basicGeneticEntity']['taxonId'],
    source=source,
)

if row['basicGeneticEntity']['crossReferences']:
    gene.xrefs = [curie_cleaner.clean(xref['id']) for xref in row['basicGeneticEntity']['crossReferences']]
if 'synonyms' in row['basicGeneticEntity'].keys():
    gene.synonym = row['basicGeneticEntity']['synonyms']

write(source_name, gene)
