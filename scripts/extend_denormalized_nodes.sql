


   create or replace table denormalized_nodes_in_clinical_trials_for as
    select nodes.id,
    string_agg(distinct in_clinical_trials_for_edges.subject, '|') as in_clinical_trials_for,
    string_agg(distinct in_clinical_trials_for_edges.subject_label, '|') as in_clinical_trials_for_label,
    count (distinct in_clinical_trials_for_edges.subject) as in_clinical_trials_for_count,
    from nodes
      left outer join denormalized_edges as in_clinical_trials_for_edges
        on nodes.id = in_clinical_trials_for_edges.object
           and in_clinical_trials_for_edges.predicate = 'biolink:in_clinical_trials_for'
    where nodes.category = 'biolink:Disease'
    group by all
;



   create or replace table denormalized_nodes_treats as
    select nodes.id,
    string_agg(distinct treats_edges.subject, '|') as treats,
    string_agg(distinct treats_edges.subject_label, '|') as treats_label,
    count (distinct treats_edges.subject) as treats_count,
    from nodes
      left outer join denormalized_edges as treats_edges
        on nodes.id = treats_edges.object
           and treats_edges.predicate = 'biolink:treats'
    where nodes.category = 'biolink:Disease'
    group by all
;


create or replace table denormalized_nodes_applied_to_treat as
    select nodes.id,
    string_agg(distinct applied_to_treat_edges.subject, '|') as applied_to_treat,
    string_agg(distinct applied_to_treat_edges.subject_label, '|') as applied_to_treat_label,
    count (distinct applied_to_treat_edges.subject) as applied_to_treat_count,
    from nodes
      left outer join denormalized_edges as applied_to_treat_edges
        on nodes.id = applied_to_treat_edges.object
           and applied_to_treat_edges.predicate = 'biolink:applied_to_treat'
    where nodes.category = 'biolink:Disease'
    group by all
;

create or replace table denormalized_nodes_any_treatment as
select nodes.id,
string_agg(distinct denormalized_edges.subject, '|') as any_treatment,
string_agg(distinct denormalized_edges.subject_label, '|') as any_treatment_label,
count (distinct denormalized_edges.subject) as any_treatment_count,
from nodes
  left outer join denormalized_edges
    on nodes.id = denormalized_edges.object
       and denormalized_edges.predicate in ('biolink:treats', 
                                            'biolink:applied_to_treat', 
                                            'biolink:in_clinical_trials_for')
where nodes.category = 'biolink:Disease'
group by all;

create or replace table denormalized_nodes as 
select  denormalized_nodes.*,          
        denormalized_nodes_applied_to_treat.* EXCLUDE (denormalized_nodes_applied_to_treat.id),
        denormalized_nodes_in_clinical_trials_for.* EXCLUDE (denormalized_nodes_in_clinical_trials_for.id), 
        denormalized_nodes_treats.* EXCLUDE (denormalized_nodes_treats.id),
        denormalized_nodes_any_treatment.* EXCLUDE (denormalized_nodes_any_treatment.id)
from denormalized_nodes 
     left outer join denormalized_nodes_treats on denormalized_nodes_treats.id = denormalized_nodes.id
     left outer join denormalized_nodes_applied_to_treat on denormalized_nodes_applied_to_treat.id = denormalized_nodes.id
     left outer join denormalized_nodes_in_clinical_trials_for on denormalized_nodes_in_clinical_trials_for.id = denormalized_nodes.id
     left outer join denormalized_nodes_any_treatment on denormalized_nodes_any_treatment.id = denormalized_nodes.id;

create or replace table denormalized_nodes as
select * REPLACE (string_split(subsets,'|') as subsets) from denormalized_nodes;

