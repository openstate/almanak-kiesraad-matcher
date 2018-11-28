from lxml import etree
from CONFIG import CONFIG
from import_data import ImportCandidates
from matching import ErrorChecking
import json
import glob
import pprint as pp
import unidecode
import os
import urllib.request

class ImportProvinceAlmanak:
    ictu_codes_incorrect = []
    almanak_municipality_data = []
    parser = etree.XMLParser(ns_clean=True)

    def parse_almanak(self):
        EC = ErrorChecking.ErrorChecking({})
        # Parse data from Allmanak xml file to etree elementTree
        almanak_path = CONFIG.FILEPATH_ALMANAK_PROVINCE
        if '://' in almanak_path:
            almanak_path = urllib.request.urlopen(CONFIG.FILEPATH_ALMANAK_PROVINCE)
        xml_almanak = etree.parse(almanak_path, self.parser)
        # The xpath gives us all valid Dutch municipalities (e.g. 380 in total in September 2018)
        mogelijkenamen = []
        final_mapping = []
        stats = []
        for province in xml_almanak.xpath(
                '//p:organisatie[p:type="Provincie"]',
                namespaces=CONFIG.NS_ALMANAK_PROVINCE):

            # mogelijkenamen.append(municipality.xpath('./p:organisaties/p:organisatie[./p:naam="Gedeputeerde Staten"]/p:functies/p:functie/p:naam/text()', namespaces=CONFIG.NS_ALMANAK_PROVINCE))
            mogelijkenamen.append(province.xpath(
                './p:organisaties/p:organisatie/p:naam/text()',
                namespaces=CONFIG.NS_ALMANAK_PROVINCE))

            province_name = province.xpath('./p:naam/text()', namespaces=CONFIG.NS_ALMANAK_PROVINCE)[0]
            number_registered_PS = len(province.xpath('./p:organisaties/p:organisatie[./p:naam="Provinciale Staten"]/p:functies/p:functie/p:medewerkers/p:medewerker', namespaces=CONFIG.NS_ALMANAK_PROVINCE))
            municipality_code = province.xpath('./p:ictuCode/p:ictuCode/text()', namespaces=CONFIG.NS_ALMANAK_PROVINCE)

            municipality_data = {}
            if "Provincie " in province_name:
                province_name = province_name.replace("Provincie ", "")
            municipality_data['municipalityName'] = province_name

            print(province_name)
            has_parameters = {
                'contact_email': province.xpath('./p:contactEmail', namespaces=CONFIG.NS_ALMANAK_PROVINCE) != [],
                'commissaris_koning': province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Commissaris van de Koning" or ./p:naam="Voorzitter / Commissaris van de Koning"]/p:functies/p:functie/p:medewerkers/p:medewerker',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE) != [],
                'leden_PS': len(province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Provinciale Staten"]/p:functies/p:functie[./p:naam="Provinciale Staten" or ./p:naam="Statenleden" or ./p:naam="Lid"]/p:medewerkers/p:medewerker',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE)) > 0,
                'voorzitter_PS': province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Provinciale Staten"]/p:functies/p:functie[./p:naam="Voorzitter" or ./p:naam="Voorzitter / Commissaris van de Koning"]/p:medewerkers/p:medewerker',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE) != [],
                'griffier_PS': province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Provinciale Staten"]/p:functies/p:functie[./p:naam="Griffier" or ./p:naam="Statengriffier"]/p:medewerkers/p:medewerker',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE) != [] or \
                               province.xpath(
                                   './p:organisaties/p:organisatie[./p:naam="Statengriffie"]',
                                   namespaces=CONFIG.NS_ALMANAK_PROVINCE) != [],
                'leden_GS': len(province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Gedeputeerde Staten"]/p:functies/p:functie[./p:naam="Gedeputeerde" or ./p:naam="Lid"]/p:medewerkers/p:medewerker',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE)) > 0,
                'voorzitter_GS': len(province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Gedeputeerde Staten"]/p:functies/p:functie[./p:naam="Voorzitter" or ./p:naam="Voorzitter, Commissaris van de Koning"]/p:medewerkers/p:medewerker',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE)) > 0,
                'secretaris_GS': len(province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Gedeputeerde Staten"]/p:functies/p:functie[./p:naam="Secretaris" or ./p:naam="Provinciesecretaris"]/p:medewerkers/p:medewerker',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE)) > 0,
                'provinciale_organisatie': province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Provinciale Organisatie" or ./p:naam="Provinciale organisatie"]',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE) != [],
                'statencommissies': province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Statencommissies"]',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE) != [],
                'number_GS': len(province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Gedeputeerde Staten"]/p:functies/p:functie[./p:naam="Gedeputeerde" or ./p:naam="Lid"]/p:medewerkers/p:medewerker',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE)),
                'number_PS': len(province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Provinciale Staten"]/p:functies/p:functie[./p:naam="Provinciale Staten" or ./p:naam="Statenleden" or ./p:naam="Lid"]/p:medewerkers/p:medewerker',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE)),
                'number_seats_PS': self.get_number_seats(province_name)
            }
            stats.append({'province_name': province_name, 'has_parameters': has_parameters})
            # print(has_parameters)

            municipality_data['numberSeats'] = number_registered_PS

            if len(municipality_code) > 0:
                municipality_data['municipalityCode'] = municipality_code[0][1:]
            else:
                self.ictu_codes_incorrect.append(province_name)

            party_data = []
            for party in province.xpath('.//p:zetel', namespaces=CONFIG.NS_ALMANAK_PROVINCE):
                party_data.append({'partyName': party.xpath('./p:partij/text()', namespaces=CONFIG.NS_ALMANAK_PROVINCE)[0],
                                   'numberSeats': party.xpath('./p:aantal/text()', namespaces=CONFIG.NS_ALMANAK_PROVINCE)[0]})

            municipality_data['partyData'] = party_data
            municipality_data['raadsleden'] = province.xpath(
                    './p:organisaties/p:organisatie[./p:naam="Provinciale Staten"]/p:functies/p:functie[./p:naam="Provinciale Staten" or ./p:naam="Statenleden" or ./p:naam="Lid"]/p:medewerkers/p:medewerker',
                    namespaces=CONFIG.NS_ALMANAK_PROVINCE)
            # print(municipality_data['raadsleden'])
            self.almanak_municipality_data.append(municipality_data)

            if len(municipality_data['raadsleden']) > 0:
                candidates_list = self.import_election_data(province_name)
                full_party_map = self.import_file('./data/big_nine_mapping.json')
                municipality_rlid_mapping, municipality_rlid_unmappable = [], []
                EC.match_mncp_members(municipality_data, full_party_map, candidates_list, municipality_rlid_mapping,
                                      municipality_rlid_unmappable, True)
                final_mapping.append({'province_name': province_name,
                                      'mapping': municipality_rlid_mapping, 'unmappable': municipality_rlid_unmappable})

        self.write_to_file(stats, './exports/error_stats_province.json')

        # pp.pprint(final_mapping)
        return final_mapping
        # print(mogelijkenamen)

    def import_election_data(self, mncp_name):
        mncp_name = unidecode.unidecode(mncp_name).replace('-', '')
        cndt_list = []
        for file in glob.glob(CONFIG.FILE_PATH_CANDIDATES_PROVINCE):
            if mncp_name in file:
                IC = ImportCandidates.ImportCandidates()
                cndt_list += IC.get_candidates(file)

        distinct_list = []
        for i in range(len(cndt_list)):
            if cndt_list[i] not in cndt_list[i + 1:]:
                distinct_list.append(cndt_list[i])

        return distinct_list

    def get_number_seats(self, province_name):
        globpaths = glob.glob('./data/*/PS2015/*'+province_name+'/Resultaat*.eml.xml')
        if len(globpaths) > 0:
            txt = globpaths[0]
            with open(txt, 'rb') as f:
                eml_read = etree.parse(f, self.parser)
                # --------- Basic check on total number seats ---------
                number_elected = eml_read.xpath('count(//def:Candidate)', namespaces=CONFIG.NS_RESULTS)
                return int(number_elected)
        else:
            return None

    @staticmethod
    def write_to_file(mapping, file_name):
        f = open(file_name, 'w')
        f.write('{ "mapping": [')
        for index, item in enumerate(mapping):
            f.write(json.dumps(item))
            if index != len(mapping)-1:
                f.write(",\n")
        f.write("]}")
        f.close()
        print("Done writing file " + file_name)

    def import_file(self, file_name):
        with open(file_name) as f:
            data = json.load(f)
        return data.get('mapping')
