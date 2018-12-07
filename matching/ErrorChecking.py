from lxml import etree
import glob
import Levenshtein as lv
import re
import json
import unidecode
from CONFIG import CONFIG
from import_data import ImportCandidates

class ErrorChecking:
    parser = etree.XMLParser(ns_clean=True)

    def __init__(self, missing_files):
        self.missing_result_files = missing_files.get('results')
        self.missing_both_files = missing_files.get('both')

    def match_all_members(self, almanak_mncp_data):
        IC = ImportCandidates.ImportCandidates()
        full_party_map = self.import_file('./data/almanak_kiesraad_party_mapping.json')
        final_mapping = []

        for municipality in almanak_mncp_data:
            # -------- Check if candidates in the Allmanak are present on the latest candidate list of the election ---------- #
            candidate_file_path = municipality.get('candidateFileName')
            if candidate_file_path and municipality.get('municipalityName') not in [item['municipality_name'] for item
                                                                                    in self.missing_both_files + self.missing_result_files]:
                party_map_mncp = []
                for prty_mncp in full_party_map:
                    if prty_mncp.get('municipality_name') == municipality.get('municipalityName'):
                        party_map_mncp = prty_mncp.get('party_mapping')

                candidates_list = IC.get_candidates(candidate_file_path)

                municipality_rlid_mapping, municipality_rlid_unmappable = [], []
                self.match_mncp_members(municipality, party_map_mncp, candidates_list, municipality_rlid_mapping, municipality_rlid_unmappable)
                final_mapping.append({'municipality_name': municipality.get('municipalityName'), 'municipality_code': municipality.get('municipalityCode'),
                                      'mapping': municipality_rlid_mapping, 'unmappable': municipality_rlid_unmappable})
        return final_mapping

    def match_mncp_members(self, municipality, party_map_mncp, candidates, rlid_mapping, rlid_unmappable, is_province_check=False):
        big_nine_mapping = self.import_file('./data/big_nine_mapping.json')
        could_not_find_party, party_not_elected = [], []
        namespace = CONFIG.NS_ALMANAK if not is_province_check else CONFIG.NS_ALMANAK_PROVINCE

        for raadslid in municipality.get('raadsleden'):
            rlidNameOriginal = raadslid.xpath('./p:naam/text()', namespaces=namespace)[0]
            # Remove all name prefixes
            rgx = re.compile("Dhr\. |Dhr\.|Mw\. |Mw\.|mr\. |mr\.|dr\. |dr\.|drs\. |drs\.|ir\. |ir\.|ing\. |ing\.|jhr. |jhr.", flags=re.IGNORECASE)
            raadslidName = re.sub(rgx, "", rlidNameOriginal).replace(".", "")

            # Convert special characters to normal characters using unidecode module and lower case
            raadslidName = unidecode.unidecode(raadslidName).lower()

            gender = "undefined"
            if 'Dhr.' in rlidNameOriginal or 'dhr.' in rlidNameOriginal:
                gender = 'male'
            elif 'Mw.' in rlidNameOriginal or 'mw.' in rlidNameOriginal:
                gender = 'female'

            raadslidParty = raadslid.xpath('./p:partij/text()', namespaces=namespace)
            systemId = raadslid.xpath('./p:systemId/p:systemId/text()', namespaces=namespace)[0]
            raadslidParty = raadslidParty[0] if len(raadslidParty) > 0 else ""

            raadslid_data = {
                'name_allmanak': raadslidName,
                'systemId_allmanak': systemId,
                'name_original': rlidNameOriginal,
                'gender_allmanak': gender,
                'party_allmanak': raadslidParty,
                'maps_with': []
            }

            elected_parties = self.get_parties_elected(municipality)
            found_party = False
            for mapping in party_map_mncp:
                if raadslidParty == mapping.get('al'):
                    if re.sub('[^A-Za-z0-9]+', '', mapping.get('kr')).lower() not in elected_parties:
                        raadslid_data['flag'] = "Party not elected"
                        party_not_elected.append(
                            {'municipality_name': municipality['municipalityName'], 'party_name': mapping['kr']})
                    found_party = True
            if not found_party and raadslidParty not in [d['al'] for d in
                                                         big_nine_mapping] and "Fractie" not in raadslidParty and "Lijst" not in raadslidParty:
                could_not_find_party.append({
                    'mncp_name': municipality.get('municipalityName'),
                    'ar': raadslidParty
                })

            # ~~ Name matching ~~ #
            found = self.matches_partial_name(candidates, raadslid_data, rlid_mapping)

            if not found:
                rlid_unmappable.append({'name': rlidNameOriginal, 'party': raadslidParty, 'reason': 'no_match_found'})

    def get_parties_elected(self, municipality):
        result_file_path = municipality.get('resultFileName')
        parties_elected = []
        if result_file_path and municipality.get('municipalityName') not in [item['municipality_name'] for item in
                                                                             self.missing_result_files + self.missing_both_files]:
            txt = glob.glob(result_file_path)[0]
            with open(txt, 'rb') as f:
                eml_read = etree.parse(f, self.parser)
                parties_elected = []
                for affiliation in eml_read.xpath('//def:Selection[./def:AffiliationIdentifier]',
                                                  namespaces=CONFIG.NS_RESULTS):
                    elected_party_name = affiliation.xpath('./def:AffiliationIdentifier/def:RegisteredName/text()',
                                                           namespaces=CONFIG.NS_RESULTS)
                    elected_party_name = elected_party_name[0] if len(elected_party_name) > 0 else ""
                    parties_elected.append(elected_party_name)
                parties_elected = [re.sub('[^A-Za-z0-9]+', '', d).lower() for d in parties_elected]
        return parties_elected

    def matches_partial_name(self, candidates, raadslid_data, rlid_mapping):
        match_found = False
        raadslid_name = raadslid_data.get('name_allmanak')
        for entry in rlid_mapping:
            if entry.get("name_allmanak") == raadslid_name:
                raadslid_data = entry

        for candidate in candidates:
            candidate_data = {
                "name": {
                    "initials": candidate.get("initials"),
                    "first_name": candidate.get("firstName"),
                    "prefix": candidate.get("prefix"),
                    "last_name": candidate.get("lastName"),
                    "original_name": candidate.get("original_name")
                },
                "party": candidate.get("party"),
                "gender": candidate.get("gender")
            }
            candidate_name = candidate.get('initials') + " " + candidate.get('prefix') + candidate.get('lastName')

            # =========================== EXACT ===================== #
            if raadslid_name == candidate_name:
                candidate_data['ln_levenshtein_distance'] = 0
                candidate_data['in_levenshtein_distance'] = 0
                candidate_data['combined_name_match'] = False
                candidate_data['initials_match'] = True
                candidate_data['firstnameletter_matches_init'] = True
                raadslid_data.get("maps_with").append(candidate_data)
                match_found = True
            else:
                # ===================== PARTIALLY MATCHING ============== #
                # Split combined last names (e.g. Nieuwenhoven-Kessels)
                split_candidate_name = re.split(" - |- | -|-", candidate.get('lastName'))
                if len(split_candidate_name) <= 1:
                    split_candidate_name = None

                split_raadslid_name = re.split(" - |- | -|-", raadslid_name)
                if len(split_raadslid_name) <= 1:
                    split_raadslid_name = None

                split_name = raadslid_name.split(" ")
                if len(split_name) > 1:
                    raadslid_initials = split_name[0]
                    raadslid_last_name = " ".join(split_name[1:])
                else:
                    raadslid_initials = "undefined"
                    raadslid_last_name = split_name[0]

                # ~~ Check if part of last name is included in name other data set, with correct initials ~~ #
                cdd_lname_in_rlidname = candidate.get('lastName') in raadslid_name
                cdd_split_lname_in_rlidname = split_candidate_name and len(split_candidate_name[0]) > 2 and \
                                              (split_candidate_name[0] in raadslid_name or split_candidate_name[
                                                  1] in raadslid_name)
                cdd_lname_in_split_rlidname = split_raadslid_name and len(split_raadslid_name[0]) > 2 and \
                                              (candidate.get('lastName') in split_raadslid_name[0] or
                                               candidate.get('lastName') in split_raadslid_name[1])
                cdd_init_is_rdlid_init = candidate.get('initials') == raadslid_initials
                cdd_init_in_rdlid_init = candidate.get('initials') in raadslid_initials
                rlid_init_in_cdd_init = raadslid_initials in candidate.get('initials')

                fst_letter_cdd_is_init = candidate.get('firstName') and candidate.get('firstName')[0].lower() == raadslid_initials

                candidateFullLastName = candidate.get('prefix') + candidate.get('lastName')
                ln_distance = lv.distance(raadslid_last_name, candidateFullLastName)
                in_distance = lv.distance(raadslid_initials, candidate.get('initials'))

                candidate_data['ln_levenshtein_distance'] = ln_distance
                candidate_data['in_levenshtein_distance'] = in_distance
                candidate_data['initials_match'] = cdd_init_is_rdlid_init
                candidate_data['firstnameletter_matches_init'] = fst_letter_cdd_is_init
                candidate_data['combined_name_match'] = False

                if ln_distance < 3 and (
                        cdd_init_in_rdlid_init or rlid_init_in_cdd_init or fst_letter_cdd_is_init or in_distance < 8):
                    raadslid_data.get("maps_with").append(candidate_data)
                    match_found = True

                elif (cdd_lname_in_rlidname or cdd_split_lname_in_rlidname or cdd_lname_in_split_rlidname) and \
                        (cdd_init_in_rdlid_init or rlid_init_in_cdd_init or in_distance < 8):
                    candidate_data['combined_name_match'] = True
                    raadslid_data.get("maps_with").append(candidate_data)
                    match_found = True

        rlid_mapping.append(raadslid_data)
        return match_found

    def import_file(self, file_name):
        with open(file_name) as f:
            data = json.load(f)
        return data.get('mapping')
