class CONFIG:
    # ---- Municipality Config ----
    # File path Almanak
    # FILEPATH_ALMANAK = './data/almanak/20180903_gemeenten.xml'
    FILEPATH_ALMANAK = 'https://almanak.overheid.nl/archive/exportOO_gemeenten.xml'

    # File paths election
    filepathsResultsGR2018 = './data/EML/GR2018/*/?esultaat_??2018_*.eml.xml'
    filepathsResultsGR2014 = './data/EML/GR2014/*/?esultaat_??2014_*.eml.xml'
    filepathsResultsHER2012 = './data/EML/HER2012/*/?esultaat_??2012_*.eml.xml'
    filepathsResultsHER2013 = './data/EML/HER2013/*/?esultaat_??2013_*.eml.xml'
    filepathsResultsHER2014 = './data/EML/HER2014/*/?esultaat_??2014_*.eml.xml'
    filepathsResultsHER2015 = './data/EML/HER2015/*/?esultaat_??2015_*.eml.xml'
    filepathsResultsHER2016 = './data/EML/HER2016/*/?esultaat_??2016_*.eml.xml'
    filepathsResultsHER2017 = './data/EML/HER2017/*/?esultaat_??2017_*.eml.xml'
    FILE_PATHS_RESULTS = [filepathsResultsGR2018, filepathsResultsHER2017, filepathsResultsHER2016,
                          filepathsResultsHER2015,
                          filepathsResultsHER2014, filepathsResultsGR2014, filepathsResultsHER2013,
                          filepathsResultsHER2012]

    filepathsCandidatesGR2018 = './data/EML/GR2018/*/?andidatenlijsten_??2018_*.eml.xml'
    filepathsCandidatesGR2014 = './data/EML/GR2014/*/?andidatenlijsten_??2014_*.eml.xml'
    filepathsCandidatesHER2012 = './data/EML/HER2012/*/?andidatenlijsten_??2012_*.eml.xml'
    filepathsCandidatesHER2013 = './data/EML/HER2013/*/?andidatenlijsten_??2013_*.eml.xml'
    filepathsCandidatesHER2014 = './data/EML/HER2014/*/?andidatenlijsten_??2014_*.eml.xml'
    filepathsCandidatesHER2015 = './data/EML/HER2015/*/?andidatenlijsten_??2015_*.eml.xml'
    filepathsCandidatesHER2016 = './data/EML/HER2016/*/?andidatenlijsten_??2016_*.eml.xml'
    filepathsCandidatesHER2017 = './data/EML/HER2017/*/?andidatenlijsten_??2017_*.eml.xml'
    FILE_PATHS_CANDIDATES = [filepathsCandidatesGR2018, filepathsCandidatesHER2017, filepathsCandidatesHER2016,
                             filepathsCandidatesHER2015, filepathsCandidatesHER2014, filepathsCandidatesGR2014,
                             filepathsCandidatesHER2013, filepathsCandidatesHER2012]


    filepathsExcludedGR2018 = './data/EML/GR2018/*/_*.txt'
    filepathsExcludedGR2014 = './data/EML/GR2014/*/_*.txt'
    filepathsExcludedHER2012 = './data/EML/HER2012/*/_*.txt'
    filepathsExcludedHER2013 = './data/EML/HER2013/*/_*.txt'
    filepathsExcludedHER2014 = './data/EML/HER2014/*/_*.txt'
    filepathsExcludedHER2015 = './data/EML/HER2015/*/_*.txt'
    filepathsExcludedHER2016 = './data/EML/HER2016/*/_*.txt'
    filepathsExcludedHER2017 = './data/EML/HER2017/*/_*.txt'
    FILE_PATHS_EXCLUDED = [filepathsExcludedGR2018, filepathsExcludedHER2017, filepathsExcludedHER2016,
                           filepathsExcludedHER2015, filepathsExcludedHER2014, filepathsExcludedGR2014,
                           filepathsExcludedHER2013, filepathsExcludedHER2012]

    # Namespaces
    NS_CANDIDATES_LIST = {
        "def": "urn:oasis:names:tc:evs:schema:eml",
        "ns2": "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0", "ns3": "urn:oasis:names:tc:ciq:xsdschema:xNL:2.0",
        "ns4": "http://www.w3.org/2000/09/xmldsig#", "ns5": "urn:oasis:names:tc:evs:schema:eml:ts",
        "ns6": "http://www.kiesraad.nl/extensions", "ns7": "http://www.kiesraad.nl/reportgenerator",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "schemaLocation": "urn:oasis:names:tc:evs:schema:eml 230-candidatelist-v5-0.xsd http://www.kiesraad.nl/extensions kiesraad-eml-extensions.xsd"}

    NS_RESULTS = {
        "def": "urn:oasis:names:tc:evs:schema:eml", "ds": "http://www.w3.org/2000/09/xmldsig#",
        "kr": "http://www.kiesraad.nl/extensions", "rg": "http://www.kiesraad.nl/reportgenerator",
        "xal": "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0", "xnl": "urn:oasis:names:tc:ciq:xsdschema:xNL:2.0"
    }
    NS_ALMANAK = {"p": "https://almanak.overheid.nl/static/schema/oo/export/2.4.0"}

    # SCORING_WEIGHTS = {"gender": 40,
    #                    "last_name": 50,
    #                    "discount_combined_name": 25,
    #                    "initial": 20,
    #                    "first_letter": 20,
    #                    "party": 40,
    #                    "lv_ln_multiplier": 3,
    #                    "lv_in_multiplier": 6}
    # SCORING_WEIGHTS = {"first_letter": 7.864320000000005, "discount_combined_name": 0.04642275147320185, "lv_ln_multiplier": 0.02448074784719628, "lv_in_multiplier": 8.640000000000004, "last_name": 0.04951760157141529, "gender": 0.031691265005705786, "initial": 7.864320000000005, "party": 0.20890238162940827}
    SCORING_WEIGHTS = {"gender": 0.002722258935367514, "last_name": 0.00425352958651174, "discount_combined_name": 0.0039876839873547575, "initial": 7.864320000000005, "first_letter": 7.864320000000005, "party": 0.022430722428870505, "lv_ln_multiplier": 0.0021028802277066098, "lv_in_multiplier": 8.640000000000004}

    # ----- Province config -----
    # FILEPATH_ALMANAK_PROVINCE = './data/almanak/20180903_provincies.xml'
    FILEPATH_ALMANAK_PROVINCE = 'https://almanak.overheid.nl/archive/exportOO_provincies.xml'
    NS_ALMANAK_PROVINCE = {"p": "https://almanak.overheid.nl/static/schema/oo/export/2.4.3"}
    FILE_PATH_EXCLUDED_PROVINCE = './data/EML/PS2015/*/_*.txt'
    FILE_PATH_CANDIDATES_PROVINCE = './data/EML_PS/PS2015/*/?andidatenlijsten_??2015_*.eml.xml'
    FILE_PATH_RESULTS_PROVINCE = './data/EML_PS/PS2015/*/?esultaat_??2015_*.eml.xml'
