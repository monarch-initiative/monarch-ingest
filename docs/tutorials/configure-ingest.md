### Configure Ingest

##### Add the file to download.yaml

Edit download.yaml to add entries for any files that need to be downloaded. 
The local name should put the file in subdirectory named for the source.

##### Create the directory

```bash
mkdir monarch_ingest/somethingbase
```

##### Copy the template

```bash
cp source_template/* monarch_ingest/somethingbase
```

##### Edit metadata.yaml

Update the description, rights link, url, etc and then add your source_file

##### Edit the source file yaml

* match the columns or required fields up with what's available in the file to be ingested
    * If it's an ingest that exists in [Dipper](https://dipper.readthedocs.io/en/latest/sources.html), check out what Dipper does.
    * Check the [Biolink Model](https://biolink.github.io/biolink-model/) documation to look at what you can capture
    * If what we need from an ingest can't be captured in the model yet, [make a new Biolink issue](https://github.com/biolink/biolink-model/issues)
* Set the header properties
    * If there is no header at all, set `header: False`
    * If there are comment lines before the header, count them and set `skip_lines: {n}`
    
##### Next

[Begin documentation](add-documentation.md)
