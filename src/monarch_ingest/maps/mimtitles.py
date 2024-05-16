

from koza.cli_utils import koza_app

from loguru import logger

source_name = "mimtitles"
row = koza_app.get_row(source_name)
map = koza_app.get_map(source_name)


###
# From OMIM
#  An asterisk (*) before an entry number indicates a gene.
#
# A number symbol (#) before an entry number indicates that it is a descriptive entry,
# usually of a phenotype, and does not represent a unique locus. The reason for the use
# of the number symbol is given in the first paragraph of he entry. Discussion of any gene(s)
# related to the phenotype resides in another entry(ies) as described in the first paragraph.
#
# A plus sign (+) before an entry number indicates that the entry contains the description of
# a gene of known sequence and a phenotype.
#
# A percent sign (%) before an entry number indicates that the entry describes a confirmed
# mendelian phenotype or phenotypic locus for which the underlying molecular basis is not known.
#
# No symbol before an entry number generally indicates a description of a phenotype for which
# the mendelian basis, although suspected, has not been clearly established or that the separateness
# of this phenotype from that in another entry is unclear.
#
# A caret (^) before an entry number means the entry no longer exists because it was removed
# from the database or moved to another entry as indicated.
###

if row['Prefix'] == 'Asterisk':
    map[row['MIM Number']] = 'gene'

elif row['Prefix'] == 'NULL':
    map[row['MIM Number']] = 'suspected'

elif row['Prefix'] == 'Number Sign':
    map[row['MIM Number']] = 'disease'

elif row['Prefix'] == 'Percent':
    map[row['MIM Number']] = 'heritable_phenotypic_marker'

elif row['Prefix'] == 'Plus':
    map[row['MIM Number']] = 'gene'

elif row['Prefix'] == 'Caret':  # moved|removed|split -> moved twice
    map[row['MIM Number']] = 'obsolete'

    # populating a dict from an omim to a set of omims
    # Not sure we'll need this so commenting out for now
    # map['replaced by'] = []
    #
    # if row['Preferred Title; symbol'][:9] == 'MOVED TO ':
    #    token = row['Preferred Title; symbol'].split(' ')
    #    title_symbol = token[2]

    #    if not re.match(r'^[0-9]{6}$', title_symbol):
    #        logger.error(f"Report malformed omim replacement {title_symbol}")
    #        # clean up ones I know about

    #        if title_symbol[0] == '{' and title_symbol[7] == '}':
    #            title_symbol = title_symbol[1:7]
    #            logger.info(f"Repaired malformed omim replacement {title_symbol}")

    #        if len(title_symbol) == 7 and title_symbol[6] == ',':
    #            title_symbol = title_symbol[:6]
    #            logger.info(f"Repaired malformed omim replacement {title_symbol}")

    #    if len(token) > 3:
    #        map['replaced by'] = [title_symbol, token[4]]

    #    else:
    #        map['replaced by'] = [title_symbol]

else:
    logger.error(f"Unknown OMIM type line {row['omim_id']}")
