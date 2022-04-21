### Configure Ingest

1. Make a directory for your ingest, using the source of the data as the name.  
Format: 

2. Add data sources to `download.yaml`
```yaml
# <source>
-
  url: https://<source>.com/downloads/somedata.txt 
  local_name: data/<source>/somedata.txt
  tag: <source>_<ingest>                             
```
For example:
```yaml
# mgi
-
  url: http://www.informatics.jax.org/downloads/reports/MRK_Reference.rpt
  local_name: data/mgi/MRK_Reference.rpt
  tag: mgi_publication_to_gene   
```  
> **Note:** Your data will now be included in `make download`, and downloaded to the appropriate subdir in `data/`

3. Copy the template:
```bash
cp source_template/* monarch_ingest/<source>
```

4. Edit `metadata.yaml`:  
    * Update the description, rights link, url, etc and then add your source_file

5. Edit the source file yaml

    * Match the columns or required fields with what's available in the file to be ingested
        * If it's an ingest that exists in [Dipper](https://dipper.readthedocs.io/en/latest/sources.html), check out what Dipper does.
        * Check the [Biolink Model](https://biolink.github.io/biolink-model/) documation to look at what you can capture
        * If what we need from an ingest can't be captured in the model yet, [make a new Biolink issue](https://github.com/biolink/biolink-model/issues)
    * Set the header properties
        * If there is no header at all, set `header: False`
        * If there are comment lines before the header, count them and set `skip_lines: {n}`
    
**Next step:  [Adding documentation](Document.md)**
