"""Tests for monarch_ingest.utils.export_utils — pure functions, no mocking needed."""

from monarch_ingest.utils.export_utils import camel_to_snake, get_fields, DEFAULT_FIELDS, DISEASE_TO_PHENOTYPE_APPENDS, GENE_TO_GENE_APPENDS


class TestCamelToSnake:
    def test_basic_camel_case(self):
        assert camel_to_snake("CamelCase") == "camel_case"

    def test_multi_word(self):
        assert camel_to_snake("DiseaseToPhenotypicFeatureAssociation") == "disease_to_phenotypic_feature_association"

    def test_single_word_lowercase(self):
        assert camel_to_snake("gene") == "gene"

    def test_single_word_capitalized(self):
        assert camel_to_snake("Gene") == "gene"

    def test_already_snake_case(self):
        assert camel_to_snake("already_snake") == "already_snake"

    def test_abbreviation(self):
        assert camel_to_snake("HTMLParser") == "html_parser"

    def test_trailing_abbreviation(self):
        assert camel_to_snake("getHTTP") == "get_http"


class TestGetFields:
    def test_default_fields(self):
        fields = get_fields("biolink:SomeAssociation")
        assert fields == DEFAULT_FIELDS

    def test_default_fields_returns_copy(self):
        """get_fields should return a copy, not mutate DEFAULT_FIELDS."""
        fields1 = get_fields("biolink:SomeAssociation")
        fields1.append("extra_field")
        fields2 = get_fields("biolink:SomeAssociation")
        assert "extra_field" not in fields2
        assert len(fields2) == len(DEFAULT_FIELDS)

    def test_gene_to_gene_interaction_appends(self):
        fields = get_fields("biolink:PairwiseGeneToGeneInteraction")
        for appended in GENE_TO_GENE_APPENDS:
            assert appended in fields

    def test_gene_to_gene_homology_appends(self):
        fields = get_fields("biolink:GeneToGeneHomologyAssociation")
        for appended in GENE_TO_GENE_APPENDS:
            assert appended in fields

    def test_disease_to_phenotype_solr_style_appends(self):
        """The disease-to-phenotype branch checks for a Solr-style 'category:"biolink:..."'
        substring. This is likely dead code since current callers pass bare category strings,
        but we document the behavior here."""
        fields = get_fields('category:"biolink:DiseaseToPhenotypicFeatureAssociation"')
        for appended in DISEASE_TO_PHENOTYPE_APPENDS:
            assert appended in fields

    def test_disease_to_phenotype_bare_category_does_not_append(self):
        """Bare biolink category does NOT trigger disease-to-phenotype appends
        because the code checks for the Solr-style substring."""
        fields = get_fields("biolink:DiseaseToPhenotypicFeatureAssociation")
        for appended in DISEASE_TO_PHENOTYPE_APPENDS:
            assert appended not in fields
