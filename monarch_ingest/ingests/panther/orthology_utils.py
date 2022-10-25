"""
Utility functions for Panther Orthology data processing
"""
from sys import stderr
from os import sep, remove
from tarfile import (
    open as tar_open,
    ReadError,
    CompressionError,
    TarInfo

)
from datetime import datetime

from typing import Optional, Tuple, List
from io import TextIOWrapper
import logging

logger = logging.getLogger()

_ncbitaxon_catalog = {
    # TODO: may need to further build up this catalog
    #       of species - just starting with the STRING DB list + Dictyostelium
    "HUMAN": "9606",
    "MOUSE": "10090",
    "CANLF": "9615",    # Canis lupus familiaris - domestic dog
    # "FELCA": "9685",  # Felis catus - domestic cat
    "BOVIN": "9913",    # Bos taurus - cow
    "PIG": "9823",      # Sus scrofa - pig
    "RAT": "10116",
    "CHICK": "9031",
    "XENTR": "8364",   # Xenopus tropicalis - tropical clawed frog
    "DANRE": "7955",
    "DROME": "7227",
    "CAEEL": "6239",
    "DICDI": "44689",
    "EMENI": "227321",  # Emericella nidulans (strain FGSC A4 etc.) (Aspergillus nidulans)
    "SCHPO": "4896",
    "YEAST": "4932",
}


ALL_ORTHOLOGS_FILE = "AllOrthologs"
TARGET_SPECIES_ORTHOLOGS = "TargetOrthologs"


def target_taxon(line: Optional[str]) -> bool:
    if not line:
        return False
    line_parts = line.split("\t")
    gene_parts = line_parts[0].split("|")
    ortholog_parts = line_parts[1].split("|")

    if gene_parts[0] in _ncbitaxon_catalog.keys() and ortholog_parts[0] in _ncbitaxon_catalog.keys():
        return True
    else:
        return False


def filter_panther_orthologs_file(
        directory: str = '.',
        source_filename: str = ALL_ORTHOLOGS_FILE,
        target_filename: str = TARGET_SPECIES_ORTHOLOGS,
        number_of_lines: int = 0
) -> bool:
    """
    Filters contents of a Panther orthologs tar.gz archive against the target list of taxa.

    :param directory: str, location of source data file
    :param source_filename: str, source data file name
    :param target_filename: str, target data file name
    :param number_of_lines: int, number of lines parsed; 'all' lines parsed if omitted or set to zero
    :return: bool, True if filtering was successful; False if unsuccessful
    """
    assert source_filename
    assert target_filename
    assert number_of_lines >= 0
    print(
        f"\nBegin file filtering '{number_of_lines if number_of_lines else 'all'}'" +
        f" lines in '{source_filename}' at {datetime.now().isoformat()}. " +
        f"\nPatience! This may take a little awhile!...", file=stderr
    )
    # A standard TAR file with a single entry identical in name to filename
    source_tar_filename: str = f"{source_filename}.tar.gz"
    source_tar_file_path: str = f"{directory}{sep}{source_tar_filename}"
    target_file_path: str = f"{directory}{sep}{target_filename}"
    n: int = 0
    try:
        with tar_open(source_tar_file_path, mode='r') as source_tar_file:
            with open(target_file_path, mode='w', encoding='utf-8') as target_file:
                # first member assumed to be the one and only target member
                member = source_tar_file.next()
                if not member:
                    logger.error(f"filter_file() tar archive '{source_tar_filename}' is empty?")
                    print(
                        f"Failed preprocessing '{source_filename}' at {datetime.now().isoformat()}", file=stderr
                    )
                    return False
                with source_tar_file.extractfile(member) as orthologs_reader:  # io.BufferedReader
                    orthologs_file = TextIOWrapper(orthologs_reader)
                    for line in orthologs_file:
                        if target_taxon(line):
                            print(line, file=target_file, end="")
                            n += 1
                        if number_of_lines and n > number_of_lines:
                            break
    except (ReadError, CompressionError) as e:
        logger.error(f"filter_file() tar file access exception: {str(e)}")
        print(f"Failed preprocessing '{source_filename}' at {datetime.now().isoformat()}", file=stderr)
        return False

    target_tar_filename: str = f"{target_filename}.tar.gz"
    target_tar_file_path: str = f"{directory}{sep}{target_tar_filename}"
    with tar_open(target_tar_file_path, mode='w:gz') as target_tar_file:
        target_tarinfo: TarInfo = target_tar_file.gettarinfo(name=target_file_path, arcname=target_filename)
        with open(target_file_path, mode='rb') as target_file:
            target_tar_file.addfile(target_tarinfo, fileobj=target_file)

    # delete the naked file
    remove(target_file_path)

    print(f"Finished filtering file '{source_filename}' at {datetime.now().isoformat()}", file=stderr)
    return True


def ncbitaxon_by_name(species_tag: str) -> Optional[str]:
    """
    Retrieves the NCBI Taxon ID of a given species, only if we are interested in it...
    :param species_tag:
    """
    if species_tag in _ncbitaxon_catalog:
        return f"NCBITaxon:{_ncbitaxon_catalog[species_tag]}"
    else:
        # ncbitaxon_by_name(): taxon with this species_tag is not of interest to Monarch? Ignoring...
        return None


# Entries with Gene/Orthology identifier namespaces
# with 'None' values below, are filtered out during ingest
_db_to_curie = {
    "FlyBase": "FB",
    "Ensembl": "ENSEMBL",
    "EnsemblGenome": "ENSEMBL",  # TODO: review and fix this later?
    "PomBase": "POMBASE",
    "WormBase": "WB",  # Wormbase supports 'WormBase:' but alliancegenome.org and identifiers.org supports 'WB:'
    "GeneID": "NCBIGene",          # seems to be Entrez Gene ID => map onto the NCBIGene: namespace
    "Gene": None,                  # seems to be the gene symbol - we ignore it for now?
    "Gene_ORFName": None,          # is the gene orf name from a transcript in Uniprot - we ignore it for now?
    "Gene_OrderedLocusName": None  # is a gene ordered locus name - we ignore it for now?
}


def get_biolink_curie_prefix(db_prefix: str) -> Optional[str]:
    """
    :param db_prefix: original database namespace identifier
    :return: Biolink Model compliant canonical CURIE namespace prefix
    """
    if db_prefix in _db_to_curie:
        return _db_to_curie[db_prefix]
    else:
        return db_prefix


def parse_gene_id(gene_id_spec: str) -> Optional[str]:
    """
    Parse out the Protein identifier
    :param gene_id_spec: is assumed to be of form 'UniProtKB=<object_id>'
    """
    if not gene_id_spec:
        raise RuntimeError(f"parse_gene_id(): Empty 'gene_id_spec'? Ignoring...")

    spec_part = gene_id_spec.split("=")

    if len(spec_part) == 2:
        # Map DB to Biolink Model canonical CURIE namespace
        prefix = get_biolink_curie_prefix(spec_part[0])

        if not prefix:
            raise RuntimeError(
                f"parse_gene_id(): Namespace '{spec_part[0]}' is not mappable to a canonical namespace? Ignoring..."
            )
        return f"{prefix}:{spec_part[1]}"

    elif len(spec_part) == 3 and spec_part[1] == "MGI":
        # Odd special case of MGI
        # (is this the only one like this? Logger errors
        #  trapped by the RuntimeError below should answer this...)
        return f"{spec_part[1]}:{spec_part[2]}"

    else:
        raise RuntimeError(
            f"parse_gene_id(): Error parsing '{str(gene_id_spec)}'? Ignoring..."
        )


def parse_gene(gene_entry: str) -> Optional[Tuple[str, str]]:
    """
    Captures a gene identifier from the Panther ref_genome record.

    :param gene_entry: string "species1|DB=id1|protdb=pdbid1" of descriptors describing the target gene
    """

    if not gene_entry:
        raise RuntimeError("parse_gene(): Empty 'gene_entry' argument?. Ignoring...")

    try:
        species, gene_spec, _ = gene_entry.split("|")
    except ValueError:
        raise RuntimeError(
            f"parse_gene(): Gene entry field '{str(gene_entry)}' has incorrect format. Ignoring..."
        )

    # get the NCBI Taxonomic identifier
    ncbitaxon_id = ncbitaxon_by_name(species)

    # Quietly ignore a species we don't know about? Only complain in debug mode though (otherwise...)
    if not ncbitaxon_id:
        raise RuntimeError(
            f"parse_gene(): Taxon '{str(species)}' in gene entry "
            f"'{str(gene_entry)}' is not in target list. Ignoring..."
        )

    # get the gene identifier
    gene_id = parse_gene_id(gene_spec)

    # Quietly ignore a gene identifier we can't parse out? Only complain in debug mode though (otherwise...)
    if not gene_id:
        raise RuntimeError(
            f"parse_gene(): Gene identifier in gene entry '{str(gene_entry)}' cannot be parsed. Ignoring..."
        )

    return ncbitaxon_id, gene_id


# TODO: probably overkill... how do I discriminate between LDO and O?
# _predicate_by_orthology_type = {
#     "LDO": {  # least diverged ortholog
#         "predicate": Predicate.orthologous_to,
#         "mapping": "RO:HOM0000017"
#     },
#     "O": {
#         "predicate": Predicate.orthologous_to,
#         "mapping": "RO:HOM0000017"
#     },
#     # Starting PANTHER 15.0, paralogs (P), horizontal gene transfer (X) and
#     # least diverged horizontal gene transfer (LDX) are no longer included in the file.
#
#     # "P": {
#     #     "predicate": Predicate.paralogous_to,
#     #     "mapping": "RO:0001025"
#     # },
#     # "X": {
#     #     "predicate": Predicate.xenologous_to,
#     #     "mapping": "RO:0002326"
#     # },
#     # "LDX": {
#     #     "predicate": Predicate.acts_upstream_of,
#     #     "mapping": "RO:0002263"
#     # }
# }

# def lookup_predicate(orthology_type: str = None) -> Optional[Tuple[str, Any]]:
#     """
#     Maps an orthology_type onto an appropriate predicate and relation term.
#
#     :param orthology_type: string code of orthology_type to be mapped { LDO, O, P, X, LDX }
#     :return: tuple(Predicate.name, mapping to relation) if available; None otherwise
#     """
#     if orthology_type and orthology_type in _predicate_by_orthology_type:
#         entry = _predicate_by_orthology_type[orthology_type]
#     else:
#         logger.error(f"Encountered unknown type of orthology '{str(orthology_type)}'?")
#         return None
#
#     return entry["predicate"], entry["mapping"]
