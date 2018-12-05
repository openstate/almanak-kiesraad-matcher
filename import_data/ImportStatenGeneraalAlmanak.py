from lxml import etree
from CONFIG import CONFIG
from import_data import ImportCandidates
from matching import ErrorChecking
import json
import urllib.request

class ImportStatenGeneraalAlmanak:
    ictu_codes_incorrect = []
    almanak_kamer_data = []
    parser = etree.XMLParser(ns_clean=True)

    def parse_almanak(self, for_kamer=None):
        final_mapping = []
        EC = ErrorChecking.ErrorChecking({})
        almanak_path = CONFIG.FILEPATH_ALMANAK_SG
        if '://' in almanak_path:
            almanak_path = urllib.request.urlopen(CONFIG.FILEPATH_ALMANAK_SG)
        # Parse data from Allmanak xml file to etree elementTree
        xml_almanak = etree.parse(almanak_path, self.parser)
        for kamer in xml_almanak.xpath(
                '//p:overheidsorganisaties/p:organisaties/p:organisatie[p:type="Staten-Generaal"]',
                namespaces=CONFIG.NS_ALMANAK_STAGEN):
            kamer_name = kamer.xpath('./p:naam/text()', namespaces=CONFIG.NS_ALMANAK_STAGEN)[0]
            if for_kamer is None or for_kamer == kamer_name:
                print("------------------- Kmaer ")
                print(for_kamer)
                print(kamer_name)
                kamer_data = {}
                party_data = []
                if kamer_name == "Eerste Kamer der Staten-Generaal":
                    for party in kamer.xpath('./p:organisaties/p:organisatie[p:naam="Samenstelling"]/p:organisaties/p:organisatie', namespaces=CONFIG.NS_ALMANAK_STAGEN):
                        party_data.append({'partyName': party.xpath('./p:afkorting/text()', namespaces=CONFIG.NS_ALMANAK_STAGEN)[0],
                                           'numberSeats': len(party.xpath('.//p:functie[contains(./p:naam, "Kamerlid")]/p:medewerkers/p:medewerker[not(./p:eindDatum)]', namespaces=CONFIG.NS_ALMANAK_STAGEN))})
                elif kamer_name == "Tweede Kamer der Staten-Generaal":
                    for party in kamer.xpath('./p:organisaties/p:organisatie[p:naam="Kamer"]/p:organisaties/p:organisatie', namespaces=CONFIG.NS_ALMANAK_STAGEN):
                        party_data.append({'partyName': party.xpath('./p:naam/text()', namespaces=CONFIG.NS_ALMANAK_STAGEN)[0],
                                           'numberSeats': len(party.xpath('.//p:functie[contains(./p:naam, "Kamerlid")]/p:medewerkers/p:medewerker[not(./p:eindDatum)]', namespaces=CONFIG.NS_ALMANAK_STAGEN))})

                kamer_data['partyData'] = party_data
                kamer_data['municipalityName'] = kamer_name
                kamer_data['raadsleden'] = kamer.xpath('.//p:functie[contains(./p:naam, "Kamerlid")]/p:medewerkers/p:medewerker[not(./p:eindDatum)]', namespaces=CONFIG.NS_ALMANAK_STAGEN)
                self.almanak_kamer_data.append(kamer_data)
                print("leden in almanak -----")
                print(len(kamer_data.get('raadsleden')))

                if len(kamer_data.get('raadsleden')) > 0:
                    candidates_list = self.import_election_data(kamer_name)
                    full_party_map = self.import_file('./data/big_nine_mapping.json')
                    kamer_rlid_mapping, kamer_rlid_unmappable = [], []
                    EC.match_mncp_members(kamer_data, full_party_map, candidates_list, kamer_rlid_mapping,
                                          kamer_rlid_unmappable, True)
                    final_mapping.append({'kamer_name': kamer_name,
                                          'mapping': kamer_rlid_mapping, 'unmappable': kamer_rlid_unmappable})
        return final_mapping

    def import_election_data(self, kamer_name):
        cndt_list = []
        file_name = CONFIG.FILE_PATH_CANDIDATES_EK
        if kamer_name == "Tweede Kamer der Staten-Generaal":
            file_name = CONFIG.FILE_PATH_CANDIDATES_TK

        IC = ImportCandidates.ImportCandidates()
        cndt_list += IC.get_candidates(file_name)

        distinct_list = []
        for i in range(len(cndt_list)):
            if cndt_list[i] not in cndt_list[i + 1:]:
                distinct_list.append(cndt_list[i])

        return distinct_list

    def import_file(self, file_name):
        with open(file_name) as f:
            data = json.load(f)
        return data.get('mapping')

    @staticmethod
    def write_to_file(mapping, file_name):
        f = open(file_name, 'w')
        f.write('{ "mapping": [')
        for index, item in enumerate(mapping):
            f.write(json.dumps(item))
            if index != len(mapping) - 1:
                f.write(",\n")
        f.write("]}")
        f.close()
        print("Done writing file " + file_name)

if __name__ == '__main__':
    ImportStatenGeneraalAlmanak()
