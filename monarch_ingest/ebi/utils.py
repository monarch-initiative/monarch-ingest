"""
Utility methods for EBI ingests
"""

#
# Gene to Phenotype Ingest utility methods
#


@staticmethod
def _get_consequence_predicate(consequence):
    #
    # Original Dipper map (based on original G2P terms?).
    # TODO: Note that the original list is orthogonal, but the new mapping is not,
    #       hence there now is an overlap between the two consequence types?
    #
    # consequence_map = {
    #     'has_molecular_consequence': [
    #         '5_prime or 3_prime UTR mutation',
    #         'all missense/in frame',
    #         'cis-regulatory or promotor mutation',
    #         'part of contiguous gene duplication'
    #     ],
    #     'has_functional_consequence': [
    #         'activating',
    #         'dominant negative',
    #         'increased gene dosage',
    #         'loss of function'
    #     ]
    # }
    consequence_map = {
        'has_molecular_consequence': [
            '5_prime or 3_prime UTR mutation',
            'altered gene product structure',
            'cis-regulatory or promotor mutation',
            'increased gene product level'
        ],
        'has_functional_consequence': [
            'altered gene product structure',
            'altered gene product structure',
            'increased gene product level',
            'absent gene product'
        ]
    }
    consequence_type = 'uncertain'
    for typ, typ_list in consequence_map.items():
        if consequence in typ_list:
            consequence_type = typ

    return consequence_type
