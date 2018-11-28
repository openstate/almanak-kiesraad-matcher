from lxml import etree
import glob
from CONFIG import CONFIG

class CheckSeats:
    parser = etree.XMLParser(ns_clean=True)

    def __init__(self, missing_files):
        self.missing_result_files = missing_files.get('results')
        self.missing_both_files = missing_files.get('both')

    # ---- Basic check if seats in municipality are equal to seats elected ---- #
    def check_all_seats(self, municipalities):
        mncp_seat_stats = []
        for mncp in municipalities:
            seat_numbers = self.check_seats(mncp)
            if seat_numbers:
                mncp_seat_stats.append(seat_numbers)
        return mncp_seat_stats

    def check_seats(self, municipality):
        result_file_path = municipality.get('resultFileName')
        if result_file_path and municipality.get('municipalityName') not in [item['municipality_name'] for item in
                                                                             self.missing_result_files + self.missing_both_files]:
            txt = glob.glob(result_file_path)[0]
            with open(txt, 'rb') as f:
                eml_read = etree.parse(f, self.parser)
                # --------- Basic check on total number seats ---------
                number_elected = eml_read.xpath('count(//def:Candidate)', namespaces=CONFIG.NS_RESULTS)
                seat_numbers = {'municipality_name': municipality.get('municipalityName'),
                                'stats': {
                                    'number_elected': int(number_elected),
                                    'number_seats': int(municipality.get('numberSeats')),
                                    'equal_seats': int(number_elected) == int(municipality.get('numberSeats'))}
                                }
                return seat_numbers
        else:
            return {'municipality_name': municipality.get('municipalityName'),
                    'stats': {
                        'number_elected': None,
                        'number_seats': int(municipality.get('numberSeats')),
                        'equal_seats': None}
                    }

    def get_seats_for_mncp(self, municipality):
        result_file_path = municipality.get('resultFileName')
        if result_file_path:
            txt = glob.glob(result_file_path)[0]
            with open(txt, 'rb') as f:
                eml_read = etree.parse(f, self.parser)
                # --------- Basic check on total number seats ---------
                number_elected = eml_read.xpath('count(//def:Candidate)', namespaces=CONFIG.NS_RESULTS)
                return number_elected

    def check_seats_from_mapping(self, mapping, almanak_mncp_data):
        improved = []
        for mncp in mapping:
            for almcp in almanak_mncp_data:
                if almcp.get('municipalityName') == mncp.get('municipality_name') and len(mncp.get('mapping')) == self.get_seats_for_mncp(almcp):
                    improved.append(mncp.get('municipality_name'))
        return improved
