from lxml import etree
import re
import glob
from CONFIG import CONFIG
import urllib.request

class ImportAlmanak:

    def __init__(self):
        self.almanak_municipality_data = []
        self.ictu_codes_incorrect = []
        self.parser = etree.XMLParser(ns_clean=True)

    def import_all(self):
        self.parse_almanak()
        for filepath in CONFIG.FILE_PATHS_RESULTS:
            self.add_file_names(filepath, 'results')

        for filepath in CONFIG.FILE_PATHS_CANDIDATES:
            self.add_file_names(filepath, 'candidate')

        return self.almanak_municipality_data

    # ============== Extract fields from Allmanak data to dicts ============== #
    # ----------- Data structure -------- #
    '''
    almanak_municipality_data: [{
        municipality_name: String,
        municipality_code: String,
        numberSeats: String,
        party_data: [{
            partyName: String,
            numberSeats: String
            }, ...],
        raadsleden: Array (etree Elements)
    }, ...]
    ictu_codes_incorrect: Array (String)
    '''

    # ---------------------------------- #
    def parse_almanak(self):
        almanak_path = CONFIG.FILEPATH_ALMANAK
        if '://' in almanak_path:
            almanak_path = urllib.request.urlopen(CONFIG.FILEPATH_ALMANAK)
        # Parse data from Allmanak xml file to etree elementTree
        xml_almanak = etree.parse(almanak_path, self.parser)
        # The xpath gives us all valid Dutch municipalities (e.g. 380 in total in September 2018)
        for municipality in xml_almanak.xpath(
                '//p:overheidsorganisaties/p:gemeenten/p:gemeente[not(p:eindDatum) and p:type="Gemeente"]',
                namespaces=CONFIG.NS_ALMANAK):
            municipality_name = municipality.xpath('./p:naam/text()', namespaces=CONFIG.NS_ALMANAK)[0]
            seats_in_municipality = municipality.xpath('./p:totaalZetels/text()', namespaces=CONFIG.NS_ALMANAK)
            municipality_code = municipality.xpath('./p:ictuCode/p:ictuCode/text()', namespaces=CONFIG.NS_ALMANAK)

            municipality_data = {}
            if "Gemeente " in municipality_name:
                municipality_name = municipality_name.replace("Gemeente ", "")
            municipality_data['municipalityName'] = municipality_name

            if len(seats_in_municipality) > 0:
                municipality_data['numberSeats'] = seats_in_municipality[0]
            else:
                print('ERROR: ' + municipality_name + ' does not have a total number of seats registered.')

            if len(municipality_code) > 0:
                municipality_data['municipalityCode'] = municipality_code[0][1:]
            else:
                self.ictu_codes_incorrect.append(municipality_name)

            party_data = []
            for party in municipality.xpath('.//p:zetel', namespaces=CONFIG.NS_ALMANAK):
                party_data.append({'partyName': party.xpath('./p:partij/text()', namespaces=CONFIG.NS_ALMANAK)[0],
                                   'numberSeats': party.xpath('./p:aantal/text()', namespaces=CONFIG.NS_ALMANAK)[0]})

            municipality_data['partyData'] = party_data
            municipality_data['raadsleden'] = municipality.xpath(
                './/p:functie[./p:naam = "Raadslid"]/p:medewerkers/p:medewerker', namespaces=CONFIG.NS_ALMANAK)
            self.almanak_municipality_data.append(municipality_data)

    # =========== Map election file names to municipality data from Allmanak ============ #

    # ----------- Data structure -------- #
    '''
    mncp_names_do_not_match: List (String)
    '''
    # ---------------------------------- #

    mncp_names_do_not_match = []

    # Add filepaths for each election Results file to the corresponding municipality from the Allmanak
    def add_file_names(self, file_paths, file_type):
        ns_prefix = ''
        file_field = ''
        ns = None
        if file_type == 'results':
            ns_prefix = 'kr'
            ns = CONFIG.NS_RESULTS
            file_field = 'resultFileName'
        if file_type == 'candidate':
            ns_prefix = 'ns6'
            ns = CONFIG.NS_CANDIDATES_LIST
            file_field = 'candidateFileName'

        # Load each file which comply to the given file path, find the unique municipality identifier
        # and match with the Allmanak municipality code (ictu code). If not found, match based on the name.
        for file in glob.glob(file_paths):
            with open(file, 'rb') as f:
                eml_read = etree.parse(f, self.parser)
                municipality_code_id = eml_read.xpath('//' + ns_prefix + ':ElectionDomain/@Id', namespaces=ns)
                municipality_code_name = eml_read.xpath('//' + ns_prefix + ':ElectionDomain/text()', namespaces=ns)
                found = False
                found_name = False

                for municipality in self.almanak_municipality_data:
                    if not municipality.get(file_field) and municipality.get('municipalityCode') == \
                            municipality_code_id[0]:
                        municipality[file_field] = f.name
                        found = True
                    # ---- This check is to collect incorrect municipality names, but is not required further ---- #
                    if municipality.get('municipalityName') == municipality_code_name[0]:
                        found_name = True

                if not found:
                    for municipality in self.almanak_municipality_data:
                        if not municipality.get(file_field) and municipality.get('municipalityName') == \
                                municipality_code_name[0]:
                            municipality[file_field] = f.name
                            self.ictu_codes_incorrect.append(municipality.get('municipalityName'))

                # TODO Check the latest file, if present, now iterates over all files, also old ones
                if not found_name and municipality_code_name[0] not in self.mncp_names_do_not_match:
                    self.mncp_names_do_not_match.append(municipality_code_name[0])


    def find_missing_election_files(self, almanak_municipality_data):
        missing_result_files = []
        missing_cndt_files = []
        missing_both_files = []

        for mncp in almanak_municipality_data:
            elct_yr_res = re.findall('\d+(?=/)', mncp.get('resultFileName'))[0] if mncp.get('resultFileName') else None
            elct_yr_can = re.findall('\d+(?=/)', mncp.get('candidateFileName'))[0] if mncp.get(
                'candidateFileName') else None

            if elct_yr_res and elct_yr_can:
                if elct_yr_can > elct_yr_res:
                    missing_result_files.append(
                        {'municipality_name': mncp.get('municipalityName'), 'year': elct_yr_can})
                elif elct_yr_can < elct_yr_res:
                    missing_cndt_files.append({'municipality_name': mncp.get('municipalityName'), 'year': elct_yr_res})

            elif not elct_yr_res and elct_yr_can:
                missing_result_files.append({'municipality_name': mncp.get('municipalityName'), 'year': elct_yr_can})
            elif not elct_yr_can and elct_yr_res:
                missing_cndt_files.append({'municipality_name': mncp.get('municipalityName'), 'year': elct_yr_res})
            else:
                missing_both_files.append({'municipality_name': mncp.get('municipalityName'), 'year': elct_yr_res})

        for filepath in CONFIG.FILE_PATHS_EXCLUDED:
            for file in glob.glob(filepath):
                with open(file, 'rb') as f:
                    year = re.findall('\d+(?=/)', f.name)[0] if f.name else None
                    mncp_name = re.findall('([a-zA-Z]+)(?=\.txt)', f.name)[0]
                    f_string = f.read().decode("cp437")
                    if "Resultaat_" in f_string and "Kandidatenlijsten_" in f_string:
                        add = True
                        for mbf in missing_both_files:
                            if mbf.get('municipality_name') == mncp_name and mbf.get('year') >= year:
                                add = False
                        if add:
                            missing_both_files.append({'municipality_name': mncp_name, 'year': year})
                    elif "Resultaat_" in f_string and "Kandidatenlijsten_" not in f_string:
                        add = True
                        for mrf in missing_result_files:
                            if mrf.get('municipality_name') == mncp_name and mrf.get('year') >= year:
                                add = False
                        if add:
                            missing_result_files.append({'municipality_name': mncp_name, 'year': year})
                    elif "Resultaat_" not in f_string and "Kandidatenlijsten_" in f_string:
                        add = True
                        for mcf in missing_cndt_files:
                            if mcf.get('municipality_name') == mncp_name and mcf.get('year') >= year:
                                add = False
                        if add:
                            missing_cndt_files.append({'municipality_name': mncp_name, 'year': year})
        return {
            'results': missing_result_files,
            'candidates': missing_cndt_files,
            'both': missing_both_files
        }
        # missing_files = missing_cndt_files + missing_result_files + missing_both_files
