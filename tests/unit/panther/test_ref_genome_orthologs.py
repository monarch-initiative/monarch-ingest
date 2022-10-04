"""
Unit tests for Panther Gene Orthology relationships ingest
"""
import pytest


@pytest.fixture
def source_name():
    """
    :return: string source name of Panther Gene Orthology relationships ingest
    """
    return "panther_ref_genome_orthologs"


@pytest.fixture
def script():
    """
    :return: string path to Panther Gene Orthology relationships ingest script
    """
    return "./monarch_ingest/ingests/panther/ref_genome_orthologs.py"


# The results expected is only distinguished by the above
# distinct Ortholog gene ID's, hence, indexed in that manner
result_expected = {
    # Test complete Panther records
    # (defective records do not get passed through to the result_expected)
    "RGD:1564893": [
        "HGNC:11477",
        "NCBITaxon:9606",
        "NCBITaxon:10116",
        "biolink:orthologous_to",
        "RO:HOM0000017",
        "PANTHER.FAMILY:PTHR12434",
    ],
    "ZFIN:ZDB-GENE-040625-156": [
        "HGNC:11477",
        "NCBITaxon:9606",
        "NCBITaxon:7955",
        "biolink:orthologous_to",
        "RO:HOM0000017",
        "PANTHER.FAMILY:PTHR12434",
    ],
    "WB:WBGene00007022": [
        "HGNC:11477",
        "NCBITaxon:9606",
        "NCBITaxon:6239",
        "biolink:orthologous_to",
        "RO:HOM0000017",
        "PANTHER.FAMILY:PTHR12434",
    ],
    "POMBASE:SPAC20G8.06": [
        "ZFIN:ZDB-GENE-040915-1",
        "NCBITaxon:7955",
        "NCBITaxon:4896",
        "biolink:orthologous_to",
        "RO:HOM0000017",
        "PANTHER.FAMILY:PTHR13162",
    ],
    "FB:FBgn0052971": [
        "HGNC:11477",
        "NCBITaxon:9606",
        "NCBITaxon:7227",
        "biolink:orthologous_to",
        "RO:HOM0000017",
        "PANTHER.FAMILY:PTHR12434",
    ],
    "FB:FBgn0040339": [
        "HGNC:11477",
        "NCBITaxon:9606",
        "NCBITaxon:7227",
        "biolink:orthologous_to",
        "RO:HOM0000017",
        "PANTHER.FAMILY:PTHR12434",
    ],
    "MGI:98446": [
        "HGNC:11477",
        "NCBITaxon:9606",
        "NCBITaxon:10090",
        "biolink:orthologous_to",
        "RO:HOM0000017",
        "PANTHER.FAMILY:PTHR12434",
    ],
    "NCBIGene:395772": [  # CHICK 'GeneID'
        "HGNC:6445",
        "NCBITaxon:9606",
        "NCBITaxon:9031",   # Gallus gallus
        "biolink:orthologous_to",
        "RO:HOM0000017",
        "PANTHER.FAMILY:PTHR45616",
    ],
    "ENSEMBL:ENSSSCG00000002799": [  # PIG 'GeneID'
        "MGI:2442402",
        "NCBITaxon:10090",
        "NCBITaxon:9823",   # Sus scrofa
        "biolink:orthologous_to",
        "RO:HOM0000017",
        "PANTHER.FAMILY:PTHR13162",
    ],
    "ENSEMBL:AN4965.2": [  # Aspergillus
        "MGI:2442402",
        "NCBITaxon:10090",
        "NCBITaxon:227321",   # Emericella nidulans (strain FGSC A4 etc.)
        "biolink:orthologous_to",
        "RO:HOM0000017",
        "PANTHER.FAMILY:PTHR13162",
    ]
}


def assert_association(data):

    assert data

    association = data[0]

    assert association
    assert association.object in result_expected.keys()

    # The test data mostly has the same human 'gene' subject
    # but is distinguished by the 'object' orthology gene id
    # hence the result_expected dictionary is now indexed thus...
    assert association.subject == result_expected[association.object][0]
    assert association.predicate == result_expected[association.object][3]

    # Evidence is a list
    assert result_expected[association.object][5] in association.has_evidence

    assert association.primary_knowledge_source == "infores:panther"
    assert "infores:monarchinitiative" in association.aggregator_knowledge_source


@pytest.fixture
def well_behaved_record_1(mock_koza, source_name, script, global_table):
    row = {
        "Gene": "HUMAN|HGNC=11477|UniProtKB=Q6GZX4",  # species1|DB=id1|protdb=pdbid1
        "Ortholog": "RAT|RGD=1564893|UniProtKB=Q6GZX2",  # species2|DB=id2|protdb=pdbid2
        "Type of ortholog": "LDO",  # [LDO, O, P, X ,LDX]  see: localtt
        "Common ancestor for the orthologs": "Euarchontoglires",  # unused
        "Panther Ortholog ID": "PTHR12434",  # panther_id
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_well_behaved_record_1(well_behaved_record_1):
    data = well_behaved_record_1
    assert_association(data)


@pytest.fixture
def well_behaved_record_2(mock_koza, source_name, script, global_table):
    row = {
        "Gene": "HUMAN|HGNC=11477|UniProtKB=Q6GZX4",
        "Ortholog": "DANRE|ZFIN=ZDB-GENE-040625-156|UniProtKB=Q6GZX1",
        "Type of ortholog": "LDO",
        "Common ancestor for the orthologs": "Euteleostomi",
        "Panther Ortholog ID": "PTHR12434",
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_well_behaved_record_2(well_behaved_record_2):
    data = well_behaved_record_2
    assert_association(data)


@pytest.fixture
def well_behaved_record_3(mock_koza, source_name, script, global_table):
    row = {
        #
        "Gene": "HUMAN|HGNC=11477|UniProtKB=Q6GZX4",
        "Ortholog": "DROME|FlyBase=FBgn0040339|",
        "Type of ortholog": "LDO",  # a different type of orthology ...
        "Common ancestor for the orthologs": "Bilateria",
        "Panther Ortholog ID": "PTHR12434",
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_well_behaved_record_3(well_behaved_record_3):
    data = well_behaved_record_3
    assert_association(data)


@pytest.fixture
def well_behaved_flybase_record(mock_koza, source_name, script, global_table):
    row = {
        "Gene": "HUMAN|HGNC=11477|UniProtKB=Q6GZX4",
        "Ortholog": "DROME|FlyBase=FBgn0052971|UniProtKB=Q6GZX0",
        "Type of ortholog": "O",
        "Common ancestor for the orthologs": "Bilateria",
        "Panther Ortholog ID": "PTHR12434",
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_well_behaved_flybase_record(well_behaved_flybase_record):
    data = well_behaved_flybase_record
    assert_association(data)


@pytest.fixture
def well_behaved_wormbase_record(mock_koza, source_name, script, global_table):
    row = {
        "Gene": "HUMAN|HGNC=11477|UniProtKB=Q6GZX4",
        # Remaps 'WormBase' prefix to 'WB'
        "Ortholog": "CAEEL|WormBase=WBGene00007022|UniProtKB=Q197F5",
        "Type of ortholog": "LDO",
        "Common ancestor for the orthologs": "Bilateria",
        "Panther Ortholog ID": "PTHR12434",
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_well_behaved_wormbase_record(well_behaved_wormbase_record):
    data = well_behaved_wormbase_record
    assert_association(data)


@pytest.fixture
def well_behaved_pombase_record(mock_koza, source_name, script, global_table):
    row = {
        "Gene": "DANRE|ZFIN=ZDB-GENE-040915-1|UniProtKB=A1A5H6",
        # Remapped prefix 'PomBase' to 'POMBASE' (as in Biolink Model)
        "Ortholog": "SCHPO|PomBase=SPAC20G8.06|UniProtKB=P87112",
        "Type of ortholog": "LDO",
        "Common ancestor for the orthologs": "Opisthokonts",
        "Panther Ortholog ID": "PTHR13162"
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_well_behaved_pombase_record(well_behaved_pombase_record):
    data = well_behaved_pombase_record
    assert_association(data)


@pytest.fixture
def odd_mgi_gene_id_record(mock_koza, source_name, script, global_table):
    row = {
        "Gene": "HUMAN|HGNC=11477|UniProtKB=Q15528",
        "Ortholog": "MOUSE|MGI=MGI=98446|UniProtKB=Q62276",
        "Type of ortholog": "LDO",
        "Common ancestor for the orthologs": "Euarchontoglires",
        "Panther Ortholog ID": "PTHR12434",
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_odd_mgi_gene_id_record(odd_mgi_gene_id_record):
    data = odd_mgi_gene_id_record
    assert_association(data)


@pytest.fixture
def pig_gene_id_record(mock_koza, source_name, script, global_table):
    row = {
        "Gene": "MOUSE|MGI=MGI=2442402|UniProtKB=Q6ZQ08",
        "Ortholog": "PIG|Ensembl=ENSSSCG00000002799|UniProtKB=I3LIC6",
        "Type of ortholog": "LDO",
        "Common ancestor for the orthologs": "Eutheria",
        "Panther Ortholog ID": "PTHR13162",
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_pig_gene_id_record(pig_gene_id_record):
    data = pig_gene_id_record
    assert_association(data)


@pytest.fixture
def aspergillus_gene_id_record(mock_koza, source_name, script, global_table):
    row = {
        "Gene": "MOUSE|MGI=MGI=2442402|UniProtKB=Q6ZQ08",
        "Ortholog": "EMENI|EnsemblGenome=AN4965.2|UniProtKB=Q5B3B5",
        "Type of ortholog": "LDO",
        "Common ancestor for the orthologs": "Opisthokonts",
        "Panther Ortholog ID": "PTHR13162",
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_aspergillus_gene_id_record(aspergillus_gene_id_record):
    data = aspergillus_gene_id_record
    assert_association(data)


@pytest.fixture
def aardvark_is_not_a_species_record(mock_koza, source_name, script, global_table):
    row = {
        # Non-target species ("AARDvark, lol")
        "Gene": "HUMAN|HGNC=11477|UniProtKB=Q15528",
        "Ortholog": "AARDV|AVD=98446|UniProtKB=Q62276",
        "Type of ortholog": "LDO",
        "Common ancestor for the orthologs": "Euarchontoglires",
        "Panther Ortholog ID": "PTHR12434",
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_aardvark_is_not_a_species_record(aardvark_is_not_a_species_record):
    assert len(aardvark_is_not_a_species_record) == 0


@pytest.fixture
def empty_gene_record(mock_koza, source_name, script, global_table):
    row = {
        # Empty gene (or ortholog) spec entry
        "Gene": "",
        "Ortholog": "MOUSE|MGI=MGI=98446|UniProtKB=Q62276",
        "Type of ortholog": "LDO",
        "Common ancestor for the orthologs": "Euarchontoglires",
        "Panther Ortholog ID": "PTHR12434",
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_empty_gene_record(empty_gene_record):
    assert len(empty_gene_record) == 0


@pytest.fixture
def ill_formed_gene_spec_string(mock_koza, source_name, script, global_table):
    row = {
        # Ill formed Gene spec string
        "Gene": "HUMAN|HGNC=11477&UniProtKB=Q15528",  # species1|DB=id1|protdb=pdbid1
        "Ortholog": "MOUSE|MGI=MGI=98446|UniProtKB=Q62276",  # species2|DB=id2|protdb=pdbid2
        "Type of ortholog": "LDO",  # [LDO, O, P, X ,LDX]  see: localtt
        "Common ancestor for the orthologs": "Euarchontoglires",  # unused
        "Panther Ortholog ID": "PTHR12434",  # panther_id
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_ill_formed_gene_spec_string(ill_formed_gene_spec_string):
    assert len(ill_formed_gene_spec_string) == 0


@pytest.fixture
def gene_prefix_gene_spec_string(mock_koza, source_name, script, global_table):
    row = {
        # Monarch Ingest Issue 244 - Ignore 'Gene' (gene symbol) prefixes
        # since they are transcript gene predictions not mappable to a reference genome?
        "Gene": "HUMAN|HGNC=6216|UniProtKB=O75449",
        "Ortholog": "CHICK|Gene=KATNA1|UniProtKB=Q1HGK7",
        "Type of ortholog": "LDO",
        "Common ancestor for the orthologs": "Amniota",
        "Panther Ortholog ID": "PTHR23074"
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_gene_prefix_gene_spec_string(gene_prefix_gene_spec_string):
    assert len(gene_prefix_gene_spec_string) == 0


@pytest.fixture
def geneid_prefix_gene_spec_string(mock_koza, source_name, script, global_table):
    row = {
        # Monarch Ingest Issue 244 - 'GeneID' namespace maps onto NCBIGene
        "Gene": "HUMAN|HGNC=6445|UniProtKB=P08729",
        "Ortholog": "CHICK|GeneID=395772|UniProtKB=O93532",
        "Type of ortholog": "LDO",
        "Common ancestor for the orthologs": "Amniota",
        "Panther Ortholog ID": "PTHR45616"
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_geneid_prefix_gene_spec_string(geneid_prefix_gene_spec_string):
    data = geneid_prefix_gene_spec_string
    assert_association(data)


@pytest.fixture
def gene_orfname_prefix_gene_spec_string(mock_koza, source_name, script, global_table):
    row = {
        # Monarch Ingest Issue 244 - Ignore 'Gene_ORFName' prefixes
        # since they are transcript predictions not mappable to a reference genome
        "Gene": "CHICK|Gene_ORFName=RCJMB04_19l3|UniProtKB=Q5ZJA3",
        "Ortholog": "DANRE|ZFIN=ZDB-GENE-121214-325|UniProtKB=E7F704",
        "Type of ortholog": "O",
        "Common ancestor for the orthologs": "Euteleostomi",
        "Panther Ortholog ID": "PTHR19232"
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_gene_orfname_prefix_gene_spec_string(gene_orfname_prefix_gene_spec_string):
    assert len(gene_orfname_prefix_gene_spec_string) == 0


@pytest.fixture
def gene_orderedlocusname_prefix_gene_spec_string(mock_koza, source_name, script, global_table):
    row = {
        # Monarch Ingest Issue 244 - Ignore 'Gene_OrderedLocusName' prefixes
        # since the Panther ref genome data uses this namespace for ARATH, ECOLI and CHICK...
        # but the latter, only a small number of identical entries in one Panther family: PTHR13068)
        "Gene": "HUMAN|HGNC=24258|UniProtKB=Q96E29",
        "Ortholog": "CHICK|Gene_OrderedLocusName=CGI-12|UniProtKB=Q5ZJC8",
        "Type of ortholog": "LDO",
        "Common ancestor for the orthologs": "Amniota",
        "Panther Ortholog ID": "PTHR13068"
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_gene_orderedlocusname_gene_spec_string(gene_orderedlocusname_prefix_gene_spec_string):
    assert len(gene_orderedlocusname_prefix_gene_spec_string) == 0


# TODO: The scientific value of EnsemblGenome entries requires closer review.
#       (Note: the required recoding to sort of handle them sensibly will be slightly tricky...
#              see https://github.com/monarch-initiative/monarch-ingest/issues/244#issuecomment-1117905786)
@pytest.fixture
def ensemblgenome_prefix_gene_spec_string(mock_koza, source_name, script, global_table):
    row = {
        # Ignore 'EnsemblGenome' prefixes for now since they are
        # protein predictions of uncharacterized proteins
        "Gene": "DANRE|ZFIN=ZDB-GENE-090112-5|UniProtKB=E9QCN7",
        "Ortholog": "DICDI|EnsemblGenome=DDB_G0277073|UniProtKB=Q550K4",
        "Type of ortholog": "O",
        "Common ancestor for the orthologs": "Unikonts",
        "Panther Ortholog ID": "PTHR21324"
    }
    return mock_koza(
        name=source_name,
        data=iter([row]),
        transform_code=script,
        global_table=global_table,
    )


def test_ensemblgenome_prefix_gene_spec_string(ensemblgenome_prefix_gene_spec_string):
    assert len(ensemblgenome_prefix_gene_spec_string) == 0
