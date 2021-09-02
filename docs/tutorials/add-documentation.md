### Document Ingest

The documentation for an ingest should reflect both the decision-making process that led to the output, and the output itself. 

Begin by copying the `source.md` file to the documentation folder, renaming it to match the ingest name and adding it to `mkdocs.yaml` in the root.

This is a great time to look over the columns in the ingest file and consider what biolink classes are appropriate to represent them and what fields are available to populate on each.

Some helpful resources:
    * [Biolink Documentation](https://biolink.github.io/biolink-model/)
    * [List of Biolink Associations](https://biolink.github.io/biolink-model/docs/Association)
    * Use a Jupyter Notebook with [Biolink Model Toolkit]() to do things like `get_element_by_mapping('RO:0002410')`
    * For ingests migrating from Dipper, check out the [documentation](https://dipper.readthedocs.io/en/latest/sources.html) and [source code](https://github.com/monarch-initiative/dipper/tree/master/dipper/sources)
 

