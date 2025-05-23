create or replace view gene_connection_flags as (
    
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
        
    )
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
);

-- count the number of genes with each flag
copy(
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
) to 'output/qc/gene_connection_report.tsv';
