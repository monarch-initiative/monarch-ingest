function processAdd(cmd) {
    var doc = cmd.solrDoc;
    var frequency_qualifier = doc.getFieldValue("frequency_qualifier");
    var has_quotient = doc.getFieldValue("has_quotient");

    if (has_quotient) {
        doc.setField("frequency_computed_sortable_float", has_quotient);
    } else if (frequency_qualifier) {
        var floatValue = mapHpIdToFloat(frequency_qualifier);
        doc.setField("frequency_computed_sortable_float", floatValue);
    }

    return cmd;
}

function mapHpIdToFloat(frequency_qualifier) {
    // Mapping HP IDs to float values
    switch (frequency_qualifier) {
        case "HP:0040280":
            return 1.0;
        case "HP:0040281":
            return 0.8;
        case "HP:0040282":
            return 0.3;
        case "HP:0040283":
            return 0.05;
        case "HP:0040284":
            return 0.01;
        default:
            return 0.0; // Default value if HP ID not found
    }
}

function finish() {
    logger.info("Finished processing");
}

function processCommit() {
    logger.info("process commit");
}