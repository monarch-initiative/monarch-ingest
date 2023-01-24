#!/bin/sh
curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field-type": {
    "name": "text",
    "class": "solr.TextField",
    "positionIncrementGap": "100",
    "indexAnalyzer": {
      "tokenizer": {
        "class": "solr.StandardTokenizerFactory"
      },
      "filters": [
        {
          "class": "solr.WordDelimiterGraphFilterFactory",
          "generateWordParts":"1",
          "generateNumberParts":"1",
          "catenateWords":"1",
          "catenateNumbers":"1",
          "catenateAll":"1",
          "splitOnCaseChange":"0",
          "preserveOriginal":"1",
          "splitOnNumerics":"0"
        },
        { "class": "solr.FlattenGraphFilterFactory" },
        { "class": "solr.ASCIIFoldingFilterFactory" },
        { "class": "solr.LowerCaseFilterFactory" },
        { "class": "solr.KeywordMarkerFilterFactory", "protected":"protwords.txt" },
        { "class": "solr.EnglishMinimalStemFilterFactory" },
        { "class": "solr.RemoveDuplicatesTokenFilterFactory" }
      ]
    },
    "queryAnalyzer" : {
      "tokenizer": {
        "class": "solr.StandardTokenizerFactory"
      },
      "filters": [
        { "class": "solr.StopFilterFactory", "ignoreCase":"true", "words":"stopwords.txt" },
        { "class": "solr.WordDelimiterGraphFilterFactory",
          "generateWordParts":"1",
          "generateNumberParts":"1",
          "catenateWords":"0",
          "catenateNumbers":"0",
          "catenateAll":"1",
          "splitOnCaseChange":"0",
          "preserveOriginal":"1",
          "splitOnNumerics":"0"
        }
        { "class": "solr.ASCIIFoldingFilterFactory" },
        { "class": "solr.LowerCaseFilterFactory" },
        { "class": "solr.KeywordMarkerFilterFactory", "protected":"protwords.txt" },
        { "class": "solr.EnglishMinimalStemFilterFactory" },
        { "class": "solr.RemoveDuplicatesTokenFilterFactory" }
      ]
    }
  }
}' http://localhost:8983/solr/entity/schema

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-field-type": {
      "name": "autocomplete",
      "class": "solr.TextField",
      "positionIncrementGap": "100",
      "indexAnalyzer": {
        "tokenizer": { "class": "solr.StandardTokenizerFactory" },
        "filters": [
          { "class": "solr.ASCIIFoldingFilterFactory" },
          { "class": "solr.LowerCaseFilterFactory" },
          {
            "class": "solr.EdgeNGramFilterFactory",
            "minGramSize": "1",
            "maxGramSize": "25"
          }
        ]
      },
      "queryAnalyzer": {
        "tokenizer": { "class": "solr.StandardTokenizerFactory" },
        "filters": [
          { "class": "solr.ASCIIFoldingFilterFactory" },
          { "class": "solr.LowerCaseFilterFactory" }
        ]
      }
    }
}' http://localhost:8983/solr/entity/schema
