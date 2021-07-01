from koza.converter.biolink_converter import (
    phaf2gene,
    phaf2gene_pheno_association,
    phaf2phenotype,
)
from koza.manager.data_collector import write
from koza.manager.data_provider import inject_row, inject_translation_table

source_name = "gene-to-phenotype"

translation_table = inject_translation_table()
row = inject_row(source_name)

gene = phaf2gene(row, "POMBASE:", "NCBITaxon:")
phenotype = phaf2phenotype(row)
association = phaf2gene_pheno_association(
    row, gene, phenotype, translation_table.resolve_term("has phenotype")
)

write(source_name, gene, phenotype, association)
