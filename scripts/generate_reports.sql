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
    select distinct missing_node
    from 'output/qc/missing_nodes.parquet' 
    where split_part(missing_node, ':', 1) in (select distinct split_part(id,':',1) from nodes where provided_by = 'phenio_nodes')
    order by missing_node
) to 'output/qc/missing_phenio_nodes.tsv' (format 'csv', delimiter E'\t', header false);

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
    select * exclude count, sum(count) as count from
    (
        select 
        provided_by as edge_ingest, 
        primary_knowledge_source as edge_primary_knowledge_source, 
        subject_namespace as namespace,
        subject_category as category,
        subject_taxon as in_taxon,
        sum(count) as count 
        from 'output/qc/edge_report.parquet'
        group by all
        union all
        select 
        provided_by as edge_ingest, 
        primary_knowledge_source as edge_primary_knowledge_source, 
        object_namespace as namespace,
        object_category as category,
        object_taxon as in_taxon,
        sum(count) as count
        from 'output/qc/edge_report.parquet'
        group by all
    ) 
    group by all
    order by all
) to 'output/qc/node_usage_report.parquet';
 


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


copy (
with knowledge_source_usage as (
    select primary_knowledge_source as knowledge_source, 
            'primary' as usage, 
            provided_by from edges            
    union all
    select unnest(aggregator_knowledge_source) as knowledge_source, 
        'aggregator' as usage, provided_by
    from edges
)
select knowledge_source_usage.*, 
  case when information_resource.id is not null then true else false end as infores_exists,
  count(*) as count
from knowledge_source_usage 
left outer join information_resource 
             on knowledge_source_usage.knowledge_source = information_resource.id
group by all
) to 'output/qc/knowledge_source_usage_report.parquet';

copy (
select knowledge_source 
from 'output/qc/knowledge_source_usage_report.parquet' 
where infores_exists = false) to 'output/qc/invalid_infores.tsv' (format 'csv', delimiter E'\t', header false);

-- This is meant to generate the classic 3 circle venn diagram of human genes, orthologs and phenotypes

copy(
with orthology as (
    select subject as gene, object as ortholog 
    from edges 
    where predicate = 'biolink:orthologous_to'
    union 
    select object as gene, subject as ortholog 
    from edges 
    where predicate = 'biolink:orthologous_to'
),
phenotype as (
    select subject as gene, object as phenotype 
    from edges 
    where predicate = 'biolink:has_phenotype'
),
disease as (
    select subject as gene, object as disease 
    from denormalized_edges
    where subject_category = 'biolink:Gene' and object_category = 'biolink:Disease' 
),
ortholog_phenotype as (
    select orthology.gene, phenotype.phenotype 
    from orthology
        join phenotype on orthology.ortholog = phenotype.gene
),
gene_connection_flags as (
    select 
        id, 
        case 
            when type = 'SO:0001217' then true 
            else false 
        end as is_protein_coding,
        case 
            when id in (select gene from orthology) then true 
            else false 
        end as has_ortholog,
        case 
            when id in (select gene from phenotype) then true 
            else false 
        end as has_phenotype,
        case 
            when id in (select gene from disease) then true 
            else false 
        end as has_disease,
        case when id in (select gene from phenotype union select gene from disease) then true 
            else false 
        end as has_phenotype_or_disease,
        case 
            when id in (select gene from ortholog_phenotype) then true 
            else false 
        end as has_ortholog_phenotype
    from nodes 
    where category = 'biolink:Gene' 
    and in_taxon = 'NCBITaxon:9606'
)
select 
    count(*) as count,
    is_protein_coding,
    has_phenotype_or_disease,
    has_ortholog,
    has_ortholog_phenotype    
from gene_connection_flags
where is_protein_coding = true
group by 
    is_protein_coding,    
    has_phenotype_or_disease,
    has_ortholog,
    has_ortholog_phenotype
order by is_protein_coding desc,      
    has_phenotype_or_disease desc,
    has_ortholog desc,
    has_ortholog_phenotype desc
) to 'output/qc/gene_connection_report.tsv' (format 'csv', delimiter E'\t', header true);
