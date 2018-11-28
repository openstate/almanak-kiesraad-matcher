# Almanak-Kiesraad Election Matcher

This repository contains code for tools which can match and validate entries from the goverment's '[Almanak](https://almanak.overheid.nl/)' with election candidate list and election results.

## Purpose
The Almanak should provide a complete and correct list of the people who have a representative role in the Dutch government. However, the data contains a lot of errors in its data and is incomplete, at the moment of writing _(November 2018)_.
This tool applies various rules in a probabilistic manner to point out what data is highly likely to be incorrect, by comparing the data entries per Almanak person which applied as a candidate for the previous elections and election results.
The tool supports checking municipality councillors (_gemeenteraadsleden_) and States-Provincial members _(Provinciale Statenleden)_. 
The main script can output all errors per municipality and province present in the almanak.
 
In the Python folder we currently have the following file structure:
 - main.py: The start script
 - import_data
    - ImportAlmanak.py: Collects relevant information from the Almanak dataset
    - ImportCandidates.py: Collects relevant information from the Kiesraad Candidate files
    - ImportProvinceAlmanak.py: Collects relevant information from the Almanak dataset
    - CreatePartyMapping.py: Political party names are written differently in the datasets, this script creates a mapping between the two
 - matching
    - CheckSeats.py: Check if an equal amount of members are registered in the Almanak as there are actually elected
    - ErrorChecking.py: Compares Almanak data entries with Election data and map the entries which are potentially about the same person
    - AssignScore.py: Assign a score to the potential matches, based on the number of features that are similar or almost similar
 - results
    - CreateErrorStats.py: Output the amount of errors in the Almanak dataset, per municipality or in total
    - CreateGraphs.py: Contains a number of functions to create plots
    - ExportDataset.py: Contains a number of helper functions to manipulate the output of the matching script to create a desired data view 
 - validation
    - MappingValidation.py: 
    - ValidateBestTwo.py: Includes an algorithm which applies the Simulation Optimization principle on feature weights on a validated dataset to obtain an optimal scoring model
    - CreateFinalDataSets.py
    - ScoreWorks.py:  
    
## Important links
 - [Almanak homepage](https://almanak.overheid.nl/)
 - [Almanak datasets](https://almanak.overheid.nl/archive/)
 - [Kiesraad datasets](https://data.overheid.nl/data/dataset?maintainer_facet=http://standaarden.overheid.nl/owms/terms/Kiesraad)
 - [Official source code repo](https://github.com/openstate/almanak-kiesraad-matcher/)

## Install and usage

 - Run main.py for starting the matching algorithms
 - The export directory contains the result files

## Author

Bas Hendrikse ([@bas_hendrikse](https://twitter.com/bas_hendrikse))

## Copyright and license

The Almanak-Kiesraad Matcher is licensed under CC0.