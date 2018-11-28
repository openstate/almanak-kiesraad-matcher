from lxml import etree
import unidecode
from CONFIG import CONFIG

class ImportCandidates:
    parser = etree.XMLParser(ns_clean=True)

    def get_candidates(self, file_path):
        cndt_array = []
        with open(file_path, 'rb') as f:
            eml_read = etree.parse(f, self.parser)
            parties_eml = eml_read.xpath('//def:Affiliation', namespaces=CONFIG.NS_CANDIDATES_LIST)

            for party in parties_eml:
                cndt_party = party.xpath('./def:AffiliationIdentifier/def:RegisteredName/text()',
                                             namespaces=CONFIG.NS_CANDIDATES_LIST)
                cndt_party = cndt_party[0] if len(cndt_party) > 0 else ""
                cndt_elems = party.xpath('./def:Candidate', namespaces=CONFIG.NS_CANDIDATES_LIST)
                for cndt_elem in cndt_elems:
                    cndt_name = \
                        cndt_elem.xpath('./def:CandidateFullName/ns3:PersonName', namespaces=CONFIG.NS_CANDIDATES_LIST)[0]
                    cndt_initials = cndt_name.xpath('./ns3:NameLine/text()', namespaces=CONFIG.NS_CANDIDATES_LIST)[0].replace(" ", "")

                    cndt_first_name = cndt_name.xpath('./ns3:FirstName/text()', namespaces=CONFIG.NS_CANDIDATES_LIST)
                    cndt_first_name = cndt_first_name[0] if len(cndt_first_name) > 0 else ""

                    cndt_name_prefix = cndt_name.xpath('./ns3:NamePrefix/text()', namespaces=CONFIG.NS_CANDIDATES_LIST)
                    if len(cndt_name_prefix) > 0:
                        cndt_name_prefix = cndt_name_prefix[0] + " "
                    else:
                        cndt_name_prefix = ""

                    cndt_last_name = cndt_name.xpath('./ns3:LastName/text()', namespaces=CONFIG.NS_CANDIDATES_LIST)[0]

                    cndt_gender = cndt_elem.xpath('./def:Gender/text()', namespaces=CONFIG.NS_CANDIDATES_LIST)
                    cndt_gender = cndt_gender[0] if len(cndt_gender) > 0 else "undefined"

                    # Convert special characters to normal characters using unidecode module and lower case
                    cndt_array.append({
                        'initials': unidecode.unidecode(cndt_initials.replace(".", "")).lower(),
                        'firstName': unidecode.unidecode(cndt_first_name).lower(),
                        'prefix': unidecode.unidecode(cndt_name_prefix).lower(),
                        'lastName': unidecode.unidecode(cndt_last_name).lower(),
                        'gender': cndt_gender,
                        'party': cndt_party,
                        'original_name': {
                            'initials': cndt_initials,
                            'firstName': cndt_first_name,
                            'prefix': cndt_name_prefix,
                            'lastName': cndt_last_name
                        }
                    })
        return cndt_array