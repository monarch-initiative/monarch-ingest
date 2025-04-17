create or replace table disease_phenotypes_and_treatments as 
select 
    id, 
    name, 
    has_phenotype_count as direct_phenotype_count, 
    has_phenotype as direct_phenotype, 
    has_phenotype_label as direct_phenotype_label, 
    treats_count, 
    treats, 
    treats_label, 
    in_clinical_trials_for_count, 
    in_clinical_trials_for, 
    in_clinical_trials_for_label, 
    applied_to_treat_count, 
    applied_to_treat, 
    applied_to_treat_label,
    any_treatment_count,
    any_treatment,
    any_treatment_label,
    case when applied_to_treat_count > 0 
         or treats_count > 0 
         or in_clinical_trials_for_count > 0 
         then 1 else 0 end as has_any_treatment,
    from denormalized_nodes 
    where 
        (applied_to_treat_count > 0 
         or treats_count > 0 
         or in_clinical_trials_for_count > 0) 
      and 'rare' in subsets
      and category = 'biolink:Disease' 
;
copy (select * from disease_phenotypes_and_treatments) to 'output/qc/disease_phenotypes_and_treatments_report.tsv';

-- relies on hpo ic score generation from scripts/after_download.sh
create or replace table disease_ic_score as select * from 'output/qc/hp.ics.tsv' ;

create or replace table disease_histopheno_tall as 
select 
    subject as disease, 
    subject_label as disease_label, 
    nodes.id as grouping_phenotype, 
    replace(replace(lower(replace(nodes.name, ' ', '_')), 'abnormality_of_',''),'the_','')  as grouping_phenotype_label,
    mean(information_content) as mean_ic,
    max(information_content) as max_ic,
    count(distinct object) as phenotype_count
from nodes
  join denormalized_edges
    on nodes.id in object_closure
  join disease_ic_score
    on disease_ic_score.id = object
where subject_category = 'biolink:Disease'
  and nodes.id in (
    'HP:0000924', -- skeletal_system = "UPHENO:0002964"  # "HP:0000924"
    'HP:0000707', -- nervous_system = "UPHENO:0004523"  # "HP:0000707"
    'HP:0000152', -- head_neck = "UPHENO:0002764"  # "HP:0000152"
    'HP:0001574', -- integument = "UPHENO:0002635"  # "HP:0001574"
    'HP:0000478', -- eye = "UPHENO:0003020"  # "HP:0000478"
    'HP:0001626', -- cardiovascular_system = "UPHENO:0080362"  # "HP:0001626"
    'HP:0001939', -- metabolism_homeostasis = "HP:0001939"  # ??? No uPheno parent
    'HP:0000119', -- genitourinary_system = "UPHENO:0002642"  # "HP:0000119"
    'HP:0025031', -- digestive_system = "UPHENO:0002833"  # "HP:0025031"
    'HP:0002664', -- neoplasm = "HP:0002664"  # ??? No uPheno parent
    'HP:0001871', -- blood = "UPHENO:0004459"  # "HP:0001871"
    'HP:0002715', -- immune_system = "UPHENO:0002948"  # "HP:0002715"
    'HP:0000818', -- endocrine = "UPHENO:0003116"  # "HP:0000818"
    'HP:0003011', -- musculature = "UPHENO:0002816"  # "HP:0003011"
    'HP:0002086', -- respiratory = "UPHENO:0004536"  # "HP:0002086"
    'HP:0000598', -- ear = "HP:0000598"  # UPHENO:0002903
    'HP:0003549', -- connective_tissue = "UPHENO:0002712"  # "HP:0003549"
    'HP:0001197', -- prenatal_or_birth = "UPHENO:0075949"  # "HP:0001197"
    'HP:0001507', -- growth = "UPHENO:0049874"  # "HP:0001507"
    'HP:0000769'  -- breast = "UPHENO:0003013"  # "HP:0000769"
  )
group by all;
copy (select * from disease_histopheno_tall) to 'output/qc/disease_histopheno_tall.tsv';

create or replace table disease_histopheno_breadth as
select disease, 
       disease_label, 
       sum(mean_ic) as histopheno_sum_of_mean_ic_across_systems,
       sum(max_ic) as histopheno_sum_of_max_ic_across_systems,     
from disease_histopheno_tall
group by all;
copy (select * from disease_histopheno_breadth) to 'output/qc/disease_histopheno_breadth_report.tsv';

create or replace table disease_histopheno as
PIVOT (select * EXCLUDE (grouping_phenotype) from disease_histopheno_tall)
ON grouping_phenotype_label
USING sum(phenotype_count) as phenotype_count, 
      mean(mean_ic) as mean_ic, -- not totally sure about this 
      max(max_ic) as max_ic; -- not totally sure about this
copy (select * from disease_histopheno) to 'output/qc/disease_histopheno.tsv';


create or replace table disease_phenotype_with_descendants as
select 
    denormalized_nodes.id as id, 
    denormalized_nodes.name as name,
    count(distinct denormalized_edges.object) as descendant_phenotype_count,
    max(information_content) as descendant_phenotype_max_ic,
    mean(information_content) as descendant_phenotype_mean_ic,
    string_agg(distinct denormalized_edges.object, '|') as descendant_phenotypes,
    string_agg(distinct denormalized_edges.object_label, '|') as descendant_phenotype_labels,
from denormalized_nodes
    join denormalized_edges on subject = denormalized_nodes.id and predicate = 'biolink:has_phenotype'
    join disease_ic_score on disease_ic_score.id = object
where denormalized_nodes.category = 'biolink:Disease'  
group by all;
copy (select * from disease_phenotype_with_descendants) to 'output/qc/disease_phenotype_with_descendants.tsv'
;

create or replace table mondo_rare_report as 
select denormalized_nodes.id as id, 
       denormalized_nodes.name as name,
       disease_phenotypes_and_treatments.direct_phenotype_count as direct_phenotype_count,
       disease_phenotype_with_descendants.descendant_phenotype_count as descendant_phenotype_count,
       disease_phenotype_with_descendants.descendant_phenotype_max_ic as descendant_phenotype_max_ic,
       disease_phenotype_with_descendants.descendant_phenotype_mean_ic as descendant_phenotype_mean_ic,       
       disease_phenotypes_and_treatments.any_treatment_count as drug_any_treatment_count,
       disease_histopheno_breadth.histopheno_sum_of_mean_ic_across_systems as histopheno_sum_of_mean_ic_across_systems,
       disease_histopheno_breadth.histopheno_sum_of_max_ic_across_systems as histopheno_sum_of_max_ic_across_systems,
       disease_histopheno.* EXCLUDE (disease_histopheno.disease, 
                                     disease_histopheno.disease_label)                                              
from denormalized_nodes
     left outer join disease_phenotype_with_descendants
       on denormalized_nodes.id = disease_phenotype_with_descendants.id
     left outer join disease_phenotypes_and_treatments
       on disease_phenotypes_and_treatments.id = denormalized_nodes.id
     left outer join disease_histopheno
       on disease_histopheno.disease = denormalized_nodes.id
     left outer join disease_histopheno_breadth
       on disease_histopheno_breadth.disease = denormalized_nodes.id
where category = 'biolink:Disease'
  and 'rare' in denormalized_nodes.subsets;  
copy (select * from mondo_rare_report) to 'output/qc/mondo_rare_report.tsv';

describe table mondo_rare_report;