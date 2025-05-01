# Multiomics Knowledge Provider Ingest

This module transforms drug-related data from the Multiomics Knowledge Provider into Biolink Model compliant nodes and edges for the Monarch knowledge graph.

## Data Sources

The data comes from:
- Clinical trials data (v2.7.2): https://db.systemsbiology.net/gestalt/KG/clinical_trials_kg_v2.7.2.tsv
- Drug approvals data (v0.3.7): https://db.systemsbiology.net/gestalt/KG/drug_approvals_kg_v0.3.7.tsv

## Data Processing

The ingest process:
1. Downloads the raw multiomics data using `monarch_ingest/download.yaml` configuration
2. Transforms drug entities (Chemical, SmallMolecule, MolecularMixture) using Biolink Model
3. Processes edges between drugs and diseases with proper predicates:
   - `biolink:treats`
   - `biolink:approved_for_treatment`
   - `biolink:in_clinical_trial_for`

## Usage

The multiomics ingest is integrated into the standard Monarch ingest pipeline:

```
# Download multiomics data
poetry run ingest download --ingest multiomics

# Run the transform
poetry run ingest transform

# Merge the KG
poetry run ingest merge

# Generate closures
poetry run ingest closure
```

## File Structure

- `clinical_trials.py`: Transforms clinical trials data
- `drug_approvals.py`: Transforms drug approvals data
- `*.yaml`: Configuration files for the different data components

## Notes

This implementation replaces the previous grep-based filtering in the `after_download.sh` script with proper Python-based transformation, enabling better validation, filtering, and error handling.