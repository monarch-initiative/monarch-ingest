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
    ppi as (
        select subject as gene1, object as gene2 
        from denormalized_edges 
        where predicate = 'biolink:interacts_with' 
        and subject_category = 'biolink:Gene' 
        and object_category = 'biolink:Gene'
        union 
        select object as gene1, subject as gene2
        from denormalized_edges
        where predicate = 'biolink:interacts_with'
    ),
    biological_activity as (
        select subject as gene, object as go_term
        from edges
        where category in ('biolink:MacromolecularMachineToBiologicalProcessAssociation', 'biolink:MacromolecularMachineToMolecularActivityAssociation', 'biolink:MacromolecularMachineToCellularComponentAssociation')
    ),
    ortholog_biological_activity as (
        select orthology.gene, biological_activity.go_term
        from orthology
            join biological_activity on orthology.ortholog = biological_activity.gene
    ),
    ortholog_ppi as (
        select orthology.gene, ppi.gene2 as ppi_partner
        from orthology
            join ppi on orthology.ortholog = ppi.gene1
        union
        select orthology.gene, ppi.gene1 as ppi_partner
        from orthology
            join ppi on orthology.ortholog = ppi.gene2
    ),
    ortholog_phenotype as (
        select orthology.gene, phenotype.phenotype 
        from orthology
            join phenotype on orthology.ortholog = phenotype.gene
        
    ),
    all_annotations as (
        select gene, 'phenotype' as annotation_type from phenotype
        union
        select gene, 'phenotype' as annotation_type from disease
        union
        select gene1 as gene, 'ppi' as annotation_type from ppi
        union
        select gene2 as gene, 'ppi' as annotation_type from ppi
        union
        select gene, 'biological_activity' as annotation_type from biological_activity
    )
    select
        id,
        'phenotype' as type,
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
        case when id in (select gene from all_annotations where annotation_type = 'phenotype') then true
            else false
        end as has_annotation,
        case
            when id in (select gene from ortholog_phenotype) then true
            else false
        end as has_ortholog_annotation
    from nodes
    where category = 'biolink:Gene'
    and in_taxon = 'NCBITaxon:9606'

    union all

    select
        id,
        'ppi' as type,
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
        case when id in (select gene from all_annotations where annotation_type = 'ppi') then true
            else false
        end as has_annotation,
        case
            when id in (select gene from ortholog_ppi) then true
            else false
        end as has_ortholog_annotation
    from nodes
    where category = 'biolink:Gene'
    and in_taxon = 'NCBITaxon:9606'

    union all

    select
        id,
        'biological_activity' as type,
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
        case when id in (select gene from all_annotations where annotation_type = 'biological_activity') then true
            else false
        end as has_annotation,
        case
            when id in (select gene from ortholog_biological_activity) then true
            else false
        end as has_ortholog_annotation
    from nodes
    where category = 'biolink:Gene'
    and in_taxon = 'NCBITaxon:9606'
);

-- count the number of genes with each flag
copy(
select
    count(*) as count,
    type as annotation_type,
    has_annotation,
    has_ortholog,
    has_ortholog_annotation
from gene_connection_flags
where is_protein_coding = true
group by
    type,
    has_annotation,
    has_ortholog,
    has_ortholog_annotation
order by
    type,
    has_annotation desc,
    has_ortholog desc,
    has_ortholog_annotation desc
) to 'output/qc/gene_connection_report.tsv' (delimiter E'\t', header true);
