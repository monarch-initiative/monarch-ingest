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
    "WormBase:WBGene00007022": [
        "HGNC:11477",
        "NCBITaxon:9606",
        "NCBITaxon:6239",
        "biolink:orthologous_to",
        "RO:HOM0000017",
        "PANTHER.FAMILY:PTHR12434",
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
}


def assert_association(data):

    association = data[0]

    assert association
    assert association.object in result_expected.keys()

    # The test data mostly has the same human 'gene' subject
    # but is distinguished by the 'object' orthology gene id
    # hence the result_expected dictionary is now indexed thus...
    assert association.subject == result_expected[association.object][0]
    assert association.predicate == result_expected[association.object][3]
    assert association.relation == result_expected[association.object][4]

    # Evidence is a list
    assert result_expected[association.object][5] in association.has_evidence

    assert "infores:panther" in association.source


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
def well_behaved_record_3(mock_koza, source_name, script, global_table):
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


def test_well_behaved_record_3(well_behaved_record_3):
    data = well_behaved_record_3
    assert_association(data)


@pytest.fixture
def well_behaved_record_4(mock_koza, source_name, script, global_table):
    row = {
        "Gene": "HUMAN|HGNC=11477|UniProtKB=Q6GZX4",
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


def test_well_behaved_record_4(well_behaved_record_4):
    data = well_behaved_record_4
    assert_association(data)


@pytest.fixture
def well_behaved_record_5(mock_koza, source_name, script, global_table):
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


def test_well_behaved_record_5(well_behaved_record_5):
    data = well_behaved_record_5
    assert_association(data)


@pytest.fixture
def well_behaved_record_6(mock_koza, source_name, script, global_table):
    row = {
        "Gene": "HUMAN|HGNC=11477|UniProtKB=Q6GZX4",
        "Ortholog": "DROME|FlyBase=FBgn0040339|",
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


def test_well_behaved_record_6(well_behaved_record_6):
    data = well_behaved_record_6
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


# Issue 244 - Panther filtering of namespaces
#
# "Gene" seems to be the gene symbol
# "GeneID" seems to be Entrez Gene ID => map onto the NCBIGene: namespace
# "Gene_ORFName" is the gene orf name from a transcript in Uniprot
# "Gene_OrderedLocusName" Is a gene ordered locus name
#
# We need to map the Prefixes to their canonical prefix if possible and identify namespaces to omit.
# Monarch preferred namespaces:
# https://docs.google.com/spreadsheets/d/1XrljI1Dk2Tg0teJSbQls5Iq_KCGXMCdyWvqAMfMgJ-M/edit#gid=136453094

@pytest.fixture
def geneid_gene_spec_string(mock_koza, source_name, script, global_table):
    row = {
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


def test_geneid_gene_spec_string(geneid_gene_spec_string):
    assert len(geneid_gene_spec_string) == 0
