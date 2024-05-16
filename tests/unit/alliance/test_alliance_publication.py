import datetime

import pytest
from koza.utils.testing_utils import mock_koza


@pytest.fixture
def source_name():
    return "alliance_publication"


@pytest.fixture
def script():
    return "./src/monarch_ingest/ingests/alliance/publication.py"


@pytest.fixture
def row():
    return {
        "allianceCategory": "Research Article",
        "abstract": "Cytoplasmic dynein and kinesin are both microtubule-based molecular motors but are structurally and evolutionarily unrelated. Under standard conditions, both move with comparable unloaded velocities toward either the microtubule minus (dynein) or plus (most kinesins) end. This similarity is important because it is often implicitly incorporated into models that examine the balance of cargo fluxes in cells and into models of the bidirectional motility of individual cargos. We examined whether this similarity is a robust feature, and specifically whether it persists across the biologically relevant temperature range. The velocity of mammalian cytoplasmic dynein, but not of mammalian kinesin-1, exhibited a break from simple Arrhenius behavior below 15 degrees C-just above the restrictive temperature of mammalian fast axonal transport. In contrast, the velocity of yeast cytoplasmic dynein showed a break from Arrhenius behavior at a lower temperature ( approximately 8 degrees C). Our studies implicate cytoplasmic dynein as a more thermally tunable motor and therefore a potential thermal regulator of microtubule-based transport. Our theoretical analysis further suggests that motor velocity changes can lead to qualitative changes in individual cargo motion and hence net intracellular cargo fluxes. We propose that temperature can potentially be used as a noninvasive probe of intracellular transport.",
        "datePublished": "2016",
        "dateLastModified": "2018-11-13T00:11:00-00:00",
        "crossReferences": [
            {"pages": ["reference"], "id": "SGD:S000185012"},
            {"id": "PMCID:PMC5034348"},
            {"id": "DOI:10.1016/j.bpj.2016.08.006"},
            {"id": "PMID:27653487"},
        ],
        "primaryId": "PMID:27653487",
        "title": "The Effect of Temperature on Microtubule-Based Transport by Cytoplasmic Dynein and Kinesin-1 Motors.",
        "authors": [
            {"authorRank": 1, "referenceId": "PMID:27653487", "name": "Hong W"},
            {"authorRank": 2, "referenceId": "PMID:27653487", "name": "Takshak A"},
            {"authorRank": 3, "referenceId": "PMID:27653487", "name": "Osunbayo O"},
            {"authorRank": 4, "referenceId": "PMID:27653487", "name": "Kunwar A"},
            {"authorRank": 5, "referenceId": "PMID:27653487", "name": "Vershinin M"},
        ],
        "citation": "Hong W, et al. (2016) The Effect of Temperature on Microtubule-Based Transport by Cytoplasmic Dynein and Kinesin-1 Motors. Biophys J 111(6):1287-1294",
        "pages": "1287-1294",
        "MODReferenceTypes": [{"referenceType": "Journal Article", "source": "SGD"}],
        "volume": "111",
        "issueName": "6",
        "resourceAbbreviation": "Biophys J",
        "tags": [{"referenceId": "PMID:27653487", "tagSource": "SGD", "tagName": "inCorpus"}],
    }


@pytest.mark.skip(reason="Will need to be updated for recent Biolink if used")
def test_research_article(mock_koza, source_name, row, script, global_table):
    entities = mock_koza(source_name, row, script, global_table=global_table)
    pub = entities[0]
    assert pub
    assert pub.id == "PMID:27653487"
    assert (
        pub.name
        == "The Effect of Temperature on Microtubule-Based Transport " + "by Cytoplasmic Dynein and Kinesin-1 Motors."
    )


@pytest.mark.skip(reason="Will need to be updated for recent Biolink if used")
@pytest.mark.parametrize("mesh_term", ["MESH:Q000502", "MESH:D002940", "MESH:Q000502", "MESH:D012890"])
def test_mesh_terms(mock_koza, source_name, row, script, global_table, mesh_term):
    row["meshTerms"] = [
        {
            "meshQualfierTerm": "Q000502",
            "referenceId": "PMID:23576957",
        },
        {
            "meshHeadingTerm": "D002940",
            "referenceId": "PMID:23576957",
        },
        {
            "meshQualfierTerm": "Q000502",
            "meshHeadingTerm": "D012890",
            "referenceId": "PMID:23576957",
        },
    ]
    entities = mock_koza(source_name, row, script, global_table=global_table)
    pub = entities[0]
    assert pub
    assert mesh_term in pub.mesh_terms


@pytest.mark.skip(reason="Will need to be updated for recent Biolink if used")
@pytest.mark.parametrize("author", ["Hong W", "Takshak A", "Osunbayo O", "Kunwar A", "Vershinin M"])
def test_research_authors(mock_koza, source_name, row, script, global_table, author):
    entities = mock_koza(source_name, row, script, global_table=global_table)
    pub = entities[0]
    assert author in pub.authors


@pytest.mark.skip(reason="Will need to be updated for recent Biolink if used")
def test_single_xref(mock_koza, source_name, row, script, global_table):
    row["crossReferences"] = [row["crossReferences"][0]]
    entities = mock_koza(source_name, row, script, global_table=global_table)
    pub = entities[0]
    assert pub.xref == ["SGD:S000185012"]


@pytest.mark.skip(reason="Will need to be updated for recent Biolink if used")
@pytest.mark.parametrize(
    "creation_date", ["2021 Jan 23", "2005", "2021-09-24", "2010-09-15T00:00:00.000-05:00", "09, February 2007"]
)
def test_time_parser(mock_koza, source_name, row, script, global_table, creation_date):
    row["datePublished"] = creation_date
    entities = mock_koza(source_name, row, script, global_table=global_table)
    pub = entities[0]
    d = pub.creation_date
    assert isinstance(d, datetime.date) or isinstance(d, datetime.datetime)


@pytest.mark.skip(reason="Will need to be updated for recent Biolink if used")
@pytest.mark.parametrize("creation_date", ["Unknown", "2016 Jul-Aug", "2003 ?%p?\b\bhP\u0007 19", "2000 Dec 14-28"])
def test_notatime_parser(mock_koza, source_name, row, script, global_table, creation_date):
    row["datePublished"] = creation_date
    entities = mock_koza(source_name, row, script, global_table=global_table)
    pub = entities[0]
    # assert pub.creation_date == None or isinstance(pub.creation_date, datetime.datetime)
    d = pub.creation_date
    assert d is None
