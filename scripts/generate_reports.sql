copy (
    select 
        subject_category, 
        subject_namespace,
        subject_taxon,         
        predicate,
        object_category,
        object_namespace,
        object_taxon,
        primary_knowledge_source,
        species_context_qualifier,
        provided_by,
        count(*) as count
    from denormalized_edges 
    group by all
 ) to 'output/qc/edge_report.parquet';

copy (
    select 
        case when id like '%:%' then split_part(id, ':', 1) else null end as namespace,    
        category,
        in_taxon,
        in_taxon_label,
        provided_by,
        count(*) as count
    from nodes
    group by all
) to 'output/qc/node_report.parquet';


copy (
    select 
    split_part(subject, ':', 1) as subject_namespace,
    split_part(original_subject,':', 1) as original_subject_namespace,
    case when subject_nodes.id is not null then subject_nodes.category else null end as subject_category,  
    case when subject_nodes.in_taxon is not null then subject_nodes.in_taxon else null end as subject_in_taxon,
    case when subject_nodes.id is not null then true else false end as subject_node_exists,
    predicate,
    split_part(object, ':', 1) as object_namespace,
    split_part(original_object,':', 1) as original_object_namespace,
    case when object_nodes.id is not null then object_nodes.category else null end as object_category, 
    case when object_nodes.in_taxon is not null then object_nodes.in_taxon else null end as object_in_taxon,  
    case when object_nodes.id is not null then true else false end as object_node_exists,
    primary_knowledge_source,
    dangling_edges.provided_by,
    count(*) as count
    from 'output/qc/monarch-kg-dangling-edges.tsv.gz' as dangling_edges
        left outer join nodes as subject_nodes 
        on subject = subject_nodes.id
        left outer join nodes as object_nodes
        on object = object_nodes.id  
    group by all
) to 'output/qc/dangling_edge_report.parquet';



copy (
    select subject as missing_node, provided_by as edge_ingest, primary_knowledge_source as edge_primary_knowledge_source      
    from 'output/qc/monarch-kg-dangling-edges.tsv.gz'
    where subject not in (select id from nodes)
    union all
    select object as missing_node, provided_by as edge_ingest, primary_knowledge_source as edge_primary_knowledge_source
    from 'output/qc/monarch-kg-dangling-edges.tsv.gz'
    where object not in (select id from nodes)
) to 'output/qc/missing_nodes.parquet';

copy (
    select edge_ingest,
        edge_primary_knowledge_source,
        split_part(missing_node, ':', 1) as namespace,       
        count(*) as count
    from 'output/qc/missing_nodes.parquet'
    group by all
    order by all
) to 'output/qc/missing_nodes_report.parquet';

select * from 'output/qc/missing_nodes_report.parquet' where edge_primary_knowledge_source = 'infores:panther';

copy (
    select *, count(*) as count from
    (
        select 
            provided_by as edge_ingest, 
            primary_knowledge_source as edge_primary_knowledge_source,  
            split_part(original_subject, ':', 1) as original_namespace,
            subject_namespace as namespace,
            subject_taxon as in_taxon
        from denormalized_edges
        where original_subject is not null and original_subject <> ''
        union all
        select 
            provided_by as edge_ingest, 
            primary_knowledge_source as edge_primary_knowledge_source,
            split_part(original_object, ':', 1) as original_namespace,
            object_namespace as namespace,
            object_taxon as in_taxon,
        from denormalized_edges
        where original_object is not null and original_object <> ''
    ) 
    group by all
    order by all
) to 'output/qc/node_normalization_report.parquet';


copy (
    select *, sum(count) as count from
    (
        select 
        provided_by as edge_ingest, 
        primary_knowledge_source as edge_primary_knowledge_source, 
        subject_namespace as namespace,
        subject_category as category,
        subject_taxon as in_taxon,
        count(*) as count 
        from 'output/qc/edge_report.parquet'
        group by all
        union all
        select 
        provided_by as edge_ingest, 
        primary_knowledge_source as edge_primary_knowledge_source, 
        object_namespace as namespace,
        object_category as category,
        object_taxon as in_taxon,
        count(*) as count
        from 'output/qc/edge_report.parquet'
        group by all
    ) 
    group by all
    order by all
) to 'output/qc/node_report.parquet';
 


copy (
    with human_gene_count as (
        select count(distinct human_genes.id) as human_gene_count
        from nodes as human_genes
        where category = 'biolink:Gene' and in_taxon = 'NCBITaxon:9606'
    ),
    ortholog_gene_count as (
        select count(distinct id) as gene_count, in_taxon
        from nodes where category = 'biolink:Gene'
        group by in_taxon
    ),
    ortholog_counts as (
    select 
        non_human_taxon,
        sum(ortholog_count) as ortholog_count
    from (
        select 
            object_taxon as non_human_taxon,
            count(distinct object) as ortholog_count
        from denormalized_edges 
        where subject_taxon = 'NCBITaxon:9606' 
        and subject_category = 'biolink:Gene'
        and object_category = 'biolink:Gene'
        and predicate = 'biolink:orthologous_to'
        group by object_taxon        
        union all
        select 
            subject_taxon as non_human_taxon,
            count(distinct subject) as ortholog_count
        from denormalized_edges 
        where subject_category = 'biolink:Gene'
        and object_category = 'biolink:Gene'
        and object_taxon = 'NCBITaxon:9606' 
        and predicate = 'biolink:orthologous_to'
        group by subject_taxon
    ) as combined_ortholog_counts
    group by non_human_taxon
    )
    select 
        'NCBITaxon:9606' as human_taxon,
        (select human_gene_count from human_gene_count) as human_gene_count,
        ortholog_count,
        -- Calculate the percentage of human genes that have orthologs in the object taxon
        (ortholog_count::float / (select human_gene_count from human_gene_count) * 100) as percentage_of_human_genes_with_orthologs,
        -- Calculate the percentage of orthologs in the object taxon that are human genes
        (ortholog_count::float / (select gene_count from ortholog_gene_count where in_taxon = non_human_taxon) * 100) as percentage_of_non_human_genes_with_orthologs,
        (select gene_count from ortholog_gene_count where in_taxon = non_human_taxon) as non_human_gene_count,
        non_human_taxon
    from ortholog_counts 
) to 'output/qc/human_orthology_coverage.parquet';


-- panther stuff 
-- select * from 'qc/missing_nodes_report.parquet' where edge_primary_knowledge_source = 'infores:panther';
-- select * from 'qc/normalized_node_report.parquet' where edge_primary_knowledge_source = 'infores:panther';
-- create or replace panther as select * from read_csv('AllOrthologs', names=['gene','ortholog', 'type', 'ancestor', 'panther_id'])