# Almanak-Kiesraad Matcher

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
    - MappingValidation.py: Helper functions to collect a (random) sample and let the user validate the correctness of matches by presenting it on a textual user interface
    - ValidateBestTwo.py: Includes an algorithm which applies the Simulation Optimization principle on feature weights on a validated dataset to obtain an optimal scoring model
    - CreateFinalDataSets.py: Remove validated incorrect matches from the dataset
    - ScoreWorks.py: Validate if the new weights do not change the order of the validated dataset
 - visualization
    - Contains files to visualize the results from the Almanak-Kiesraad Matcher on an interactive map of the Netherlands
 
## Important links
 - [Almanak homepage](https://almanak.overheid.nl/)
 - [Almanak datasets](https://almanak.overheid.nl/archive/)
 - [Kiesraad datasets](https://data.overheid.nl/data/dataset?maintainer_facet=http://standaarden.overheid.nl/owms/terms/Kiesraad)
 - [Official source code repo](https://github.com/openstate/almanak-kiesraad-matcher/)

## Install and usage

 - Add the Kiesraad EML datasets to the data directory. Follow the structure: data/EML/GR[year] or data/EML/HER[year] for municipalities and data/EML_PS/PS[year] for provinces. Or configure the path in CONFIG.py.
```bash
# download all EK, TK, PS and GR elections (curl CKAN REST API to get EML datasets, jq convert to usable JSON array, jq filter set, xargs curl download)
curl -gsSf 'https://data.overheid.nl/data/api/3/action/package_search?q=EML&facet.field=[%22res_format%22,%22maintainer%22]&fq=res_format:%22ZIP%22+maintainer:%22http://standaarden.overheid.nl/owms/terms/Kiesraad%22&rows=100' --compressed \
 | jq '.result.results|map({title,modified:.modified|split("-")|reverse|join("-")} as $b|.resources[]|{url,created:.created[0:10],short:.url|split("/")[-1][:-4]|split("_")[-1][-10:]|ascii_upcase} + $b)|sort_by(.created)' \
 | jq 'map(select(([.short[0:2]]|inside(["EK","TK","PS","GR"])) and (.short[2:6]|tonumber) > 2012))[].url' -r \
 | xargs -I '{url}' curl -gsSfOL '{url}'

# unzip GR and GR_HER:
for f in $(ls *GR201?.zip); do D="data/EML/${f:(-10):6}";mkdir -p "$D";unzip "$f" '*/[Rr]esultaat*.eml.xml' '*/[Kk]andidatenlijsten*.eml.xml' '*/_*.txt' -d "$D"; done
for f in $(ls *GR201?????.zip); do D="data/EML/HER${f:(-12):4}";mkdir -p "$D";unzip "$f" '*/[Rr]esultaat*.eml.xml' '*/[Kk]andidatenlijsten*.eml.xml' '*/_*.txt' -d "$D"; done
# unzip EK, TK and PS:
for f in $(ls *[ETP][KS]201?.zip); do D="data/EML_${f:(-10):2}/${f:(-10):6}";mkdir -p "$D";unzip "$f" '*[Rr]esultaat*.eml.xml' '*[Kk]andidatenlijsten*.eml.xml' '*_*.txt' -d "$D"; done

# fix Zundert, that has a UTF-8 byte order mark (BOM) (\uFEFF = \xEFBBBF in UTF-8) but with latin1 \xE8 (è) inside :(
sed $'1s/^\uFEFF//' 'data/EML/GR2018/11 Noord-Brabant/Kandidatenlijsten_GR2018_Zundert.eml.xml' | iconv -f latin1 -t utf-8 > tmp.xml
mv tmp.xml 'data/EML/GR2018/11 Noord-Brabant/Kandidatenlijsten_GR2018_Zundert.eml.xml'

# convert latin1 filename \xE2 (â) to UTF-8
mv $'data/EML_PS/PS2015/02 Frysl\xE2n' $'data/EML_PS/PS2015/02 Frysl\uE2n'
# or: convmv -f iso-8859-1 -t utf-8 data/EML_PS/PS2015/* --notest
```
 - Install the requirements:
```bash
pip install -r requirements.txt
```
 - Run main.py for starting the matching algorithms
 - The export directory contains the result files

## Author

Bas Hendrikse ([@bas_hendrikse](https://twitter.com/bas_hendrikse))

## Copyright and license

The Almanak-Kiesraad Matcher is licensed under CC0.
