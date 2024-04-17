from koza.cli_runner import get_koza_app
from source_translation import source_map

from biolink_model.datamodel.pydanticmodel_v2 import Gene

koza_app = get_koza_app("alliance_gene")
taxon_labels = koza_app.get_map("taxon-labels")

while (row := koza_app.get_row()) is not None:

    # curie prefix as source?
    gene_id = row["basicGeneticEntity"]["primaryId"]

    # Not sure if Alliance will stick with this prefix for Xenbase, but for now...
    gene_id = gene_id.replace("DRSC:XB:", "Xenbase:")

    source = source_map[gene_id.split(":")[0]]

    if "name" not in row.keys():
        row["name"] = row["symbol"]

    in_taxon = row["basicGeneticEntity"]["taxonId"]
    if in_taxon in taxon_labels.keys():
        in_taxon_label = taxon_labels[in_taxon]['label']
    else:
        if in_taxon == "NCBITaxon:10090":
            in_taxon_label = "Mus musculus"
        elif in_taxon == "NCBITaxon:7955":
            in_taxon_label = "Danio rerio"
        elif in_taxon == "NCBITaxon:10116":
            in_taxon_label = "Rattus norvegicus"
        elif in_taxon == "NCBITaxon:6239":
            in_taxon_label = "Caenorhabditis elegans"
        elif in_taxon == "NCBITaxon:7227":
            in_taxon_label = "Drosophila melanogaster"
        elif in_taxon == "NCBITaxon:8355":
            in_taxon_label = "Xenopus laevis"
        elif in_taxon == "NCBITaxon:8364":
            in_taxon_label = "Xenopus tropicalis"
        elif in_taxon == "NCBITaxon:4932":
            in_taxon_label = "Saccharomyces cerevisiae"
        elif in_taxon == "NCBITaxon:559292":
            in_taxon_label = "Saccharomyces cerevisiae S288C"
        else:
            raise ValueError(f"Can't find taxon name for: {in_taxon}")

    gene = Gene(
        id=gene_id,
        symbol=row["symbol"],
        name=row["symbol"],
        full_name=row["name"].replace("\r",""), # Replacement to remove stray carriage returns in XenBase files
        # No place in the schema for gene type (SO term) right now
        # type=row["soTermId"],
        in_taxon=[in_taxon],
        in_taxon_label=in_taxon_label,
        provided_by=[source]
    )

    if row["basicGeneticEntity"]["crossReferences"]:
        gene.xref = [
            koza_app.curie_cleaner.clean(xref["id"])
            for xref in row["basicGeneticEntity"]["crossReferences"]
        ]
    if "synonyms" in row["basicGeneticEntity"].keys():
        # more handling for errant carriage returns
        gene.synonym = [synonym.replace("\r","") for synonym in row["basicGeneticEntity"]["synonyms"] ]

    koza_app.write(gene)
