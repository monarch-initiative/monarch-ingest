### Testing

You may want to start with the test template within `source_template`

##### Basic fixtures

Initially, set up your basic fixtures, taking care to set the correct source name and location for the transform code.

```python
import pytest
from koza.koza_runner import get_translation_table


@pytest.fixture
def tt():
    return get_translation_table("monarch_ingest/translation_table.yaml", None)

# This name must match the ingest name in the transform code
@pytest.fixture
def source_name():
    return "something-to-somethingelse"

# This is the location of the transform code
@pytest.fixture
def script():
    return "./monarch_ingest/somethingbase/something2somethingelse.py"
```


##### A map, if necessary

Some ingests will depend on one or more maps, that fixture can be set up here. Note that this fixture must return a map of maps, and that the inner maps will map from an ID to a dictionary representing column headers and values. 

In the example below, a map is created that maps from a big concatenated natural key (as the ID) for ZP to a single column (called `iri`) that contains the ZP ID. 

This map is then placed into the map cache under the name `eqe2zp`
```python
@pytest.fixture
def map_cache():
    eqe2zp = {
        "0-0-ZFA:0000042-PATO:0000638-0-0-0": {"iri": "ZP:0004225"},
        "BSPO:0000112-BFO:0000050-ZFA:0000042-PATO:0000638-0-0-0": {
            "iri": "ZP:0011243"
        },
        "BSPO:0000000-BFO:0000050-ZFA:0000823-PATO:0000642-BSPO:0000007-BFO:0000050-ZFA:0000823": {
            "iri": "ZP:0000157"
        },
    }
    return {"eqe2zp": eqe2zp}
```


##### Fixtures for test data

Create a fixture that returns a dictionary to represent a single row. As a matter of strategy, this row should probably represent a fairly basic row being ingested. 

One trick so that you don't have to manually convert from the imput format to a python dictionary format is to run your ingest with a debugger and set a breakpoint just after a row has been injected. If you want a more specific piece of data, check out conditional breakpoints. 

````python
@pytest.fixture
def basic_row():
    return {
        "ID": "341492416",
        "Gene Symbol": "pax2a",
        "Gene ID": "ZDB-GENE-990415-8",
         #...
        "Fish Environment ID": "ZDB-GENOX-041102-1385",
        "Publication ID": "ZDB-PUB-970210-19",
        "Figure ID": "ZDB-FIG-120307-8",
    }
````


##### Fixture for transforming a single row

This sets up a fixture you can call more than once to independently test different attributes

```python
@pytest.fixture
def basic_g2p(mock_koza, source_name, basic_row, script, map_cache, tt):
    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        map_cache=map_cache,
        translation_table=tt,
    )
```


##### Test the basics of the ingest

Confirm that entities are created matching the expectations on the row

```python
# A simple end-to-end test is to confirm that the IDs are set on
def test_gene(basic_g2p):
    gene = basic_g2p[0]
    assert gene
    assert gene.id == "ZFIN:ZDB-GENE-990415-8"


def test_phenotypic_feature(basic_g2p):
    phenotypic_feature = basic_g2p[1]
    assert phenotypic_feature
    assert phenotypic_feature.id == "ZP:0004225"


def test_association(basic_g2p):
    association = basic_g2p[2]
    assert association
    assert association.subject == "ZFIN:ZDB-GENE-990415-8"
    assert association.object == "ZP:0004225"
    assert association.publications
    assert association.publications[0] == "ZFIN:ZDB-PUB-970210-19"
```


##### Test against an alternate row

For any branching within the transform code, it's a good idea to test against all of the paths through the code. It's possible to set conditional breakpoints to find real examples in the code that will hit each code path, but it may be more practical to modify the basic row as a new fixture

The example below creates a row with additional columns filled in.

```python
@pytest.fixture
def postcomposed(mock_koza, source_name, basic_row, script, map_cache, tt):

    basic_row["Affected Structure or Process 1 subterm ID"] = "BSPO:0000112"
    basic_row["Post-composed Relationship ID"] = "BFO:0000050"
    basic_row["Affected Structure or Process 1 superterm ID"] = "ZFA:0000042"

    return mock_koza(
        source_name,
        iter([basic_row]),
        script,
        map_cache=map_cache,
        translation_table=tt,
    )
```


##### Parameterized tests 

Mixing [parameterization](https://docs.pytest.org/en/6.2.x/parametrize.html) and fixtures changes the approach a little. In this case it makes more sense to alter the row using a parameter and then create the entities within the same method.  

The test below is intended to confirm that when the tag column has any of the specified values, the row will be ignored (confirmed because no entities are created).

```python
@pytest.mark.parametrize("tag", ["normal", "exacerbated", "ameliorated"])
def test_excluded_tags(mock_koza, source_name, basic_row, script, map_cache, tt, tag):
    basic_row["Phenotype Tag"] = tag
    entities = mock_koza(
        source_name,
        iter([basic_row]),
        script,
        map_cache=map_cache,
        translation_table=tt,
    )
    assert len(entities) == 0
```
