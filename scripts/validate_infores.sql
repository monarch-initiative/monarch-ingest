create or replace view ;


with knowledge_sources as (
    select distinct primary_knowledge_source as knowledge_source, 'primary' as usage, provided_by from edges
    union
    select distinct
        unnest(string_split(aggregator_knowledge_source,'|')) as knowledge_source, 
        'aggregator' as usage, provided_by
    from edges
), 
infores as (select * from read_csv('data/infores/infores_ids.txt', header=false, names=['id']))
select 
    knowledge_source, list(provided_by) as provided_by    
from knowledge_sources
    left join infores on knowledge_sources.knowledge_source = infores.id
where infores.id is null
group by knowledge_source;

