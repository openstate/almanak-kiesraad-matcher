from import_data import ImportAlmanak, ImportCandidates, ImportProvinceAlmanak, ImportStatenGeneraalAlmanak
from matching import ErrorChecking, CheckSeats, AssignScore
from results import ExportDataset, CreateErrorStats, CreateGraphs
from validation import ValidateBestTwo, ScoreWorks, MappingValidation, CreateFinalDataSets

import pprint as pp
import json
import os
import subprocess

class Main:
    def __init__(self):
        seat_stats = self.seats()
        if not os.path.exists('exports'):
            os.makedirs('exports')
        self.write_to_file(seat_stats, './exports/seats_errors.json')
        self.municipality_check()

        error_stats = self.stats(self.import_file('./exports/corrected_almanak.json'))
        self.write_to_file(self.merge_seat_error_stats(seat_stats, error_stats), './exports/error_stats_total.json')
        self.province_check()

        self.stagen_check(kamer_name="Eerste Kamer der Staten-Generaal")
        pp.pprint(self.stats(self.import_file('./exports/staten_generaal_best.json'), return_totals=True))
        self.write_to_file(self.stats(self.import_file('./exports/staten_generaal_best.json'), return_totals=False), './exports/error_stats_EK_total.json')

        self.stagen_check(kamer_name="Tweede Kamer der Staten-Generaal")
        pp.pprint(self.stats(self.import_file('./exports/staten_generaal_best.json'), return_totals=True))
        self.write_to_file(self.stats(self.import_file('./exports/staten_generaal_best.json'), return_totals=False), './exports/error_stats_TK_total.json')

        subprocess.call(['./visualization/create_geo_json.sh'])

        # pp.pprint(self.stats(self.import_file('./exports/potentials.json'), return_totals=True))
        # pp.pprint(self.stats_examples(self.import_file('./exports/potentials.json'), 2))

        # pp.pprint(self.stats_examples(self.import_file('./exports/province_best.json'), 2))
        # pp.pprint(self.stats(self.import_file('./exports/province_best.json'), return_totals=False))

    def import_almanak(self):
        IA = ImportAlmanak.ImportAlmanak()
        return IA.import_all()

    def missing_files(self, almanak_mncp_data):
        IA = ImportAlmanak.ImportAlmanak()
        return IA.find_missing_election_files(almanak_mncp_data)

    def seats(self):
        almanak_mncp_data = self.import_almanak()
        missing_files = self.missing_files(almanak_mncp_data)

        CS = CheckSeats.CheckSeats(missing_files)
        seat_data = CS.check_all_seats(almanak_mncp_data)
        return seat_data

    def match(self):
        almanak_mncp_data = self.import_almanak()
        missing_files = self.missing_files(almanak_mncp_data)

        EC = ErrorChecking.ErrorChecking(missing_files)
        return EC.match_all_members(almanak_mncp_data)

    def score(self, mapping):
        AS = AssignScore.AssignScore()
        return AS.assign_score_all(mapping)

    def best(self, mapping):
        ED = ExportDataset.ExportDataset()
        return ED.get_best_mapping(mapping)

    def potentials(self, mapping):
        ED = ExportDataset.ExportDataset()
        return ED.get_potentials(mapping)

    def stats(self, mapping, return_totals=False):
        CES = CreateErrorStats.CreateErrorStats()
        return CES.create_stats(mapping, return_totals)

    def stats_examples(self, mapping, amount):
        CES = CreateErrorStats.CreateErrorStats()
        return CES.create_stats_examples(mapping, amount)

    @staticmethod
    def merge_seat_error_stats(seat_stats, error_stats):
        for mncp_seat in seat_stats:
            found = False
            for mncp in error_stats:
                if mncp.get('municipality_name') == mncp_seat.get('municipality_name'):
                    for key in mncp_seat.get('stats').keys():
                        mncp[key] = mncp_seat.get('stats').get(key)
                    found = True
            if not found:
                error_stats.append(mncp_seat)
        return error_stats

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

    @staticmethod
    def import_file(file_name):
        with open(file_name) as f:
            data = json.load(f)
        f.close()
        return data.get('mapping')

    # --- Validation ---

    def optimize_weights(self, mapping):
        VBT = ValidateBestTwo.ValidateBestTwo()
        VBT.loop_setups(mapping)

    def works(self, mapping):
        SW = ScoreWorks.ScoreWorks()
        SW.check(mapping)
        # pp.pprint(SW.find_person(mapping, 'rhmg hermans'))

    def show_scores(self, mapping):
        CG = CreateGraphs.CreateGraphs()
        CG.plot_scores(mapping)

    def validate_weights_of_sample(self, best_mapping):
        MV = MappingValidation.MappingValidation()
        # return MV.validate_best(best_mapping[:2])
        return MV.validate_sample(MV.get_sample(best_mapping))

    def validate_weights_worst(self, best_mapping):
        MV = MappingValidation.MappingValidation()
        return MV.validate_sample2(MV.get_worst_scores(best_mapping))

    def plot_correct(self, flat_map):
        CG = CreateGraphs.CreateGraphs()
        CG.plot_incorrect_distance(flat_map)

    def final_dataset(self, best_mapping, validated_mapping_sample):
        CFD = CreateFinalDataSets.CreateFinalDataSets()
        return CFD.remove_incorrect(best_mapping, validated_mapping_sample)

    def check_seats_improved(self, mapping):
        almanak_mncp_data = self.import_almanak()
        missing_files = self.missing_files(almanak_mncp_data)

        CS = CheckSeats.CheckSeats(missing_files)
        l1 = CS.check_all_seats(almanak_mncp_data)
        pp.pprint(CS.check_seats_from_mapping(mapping, l1.get('incorrect')))

    def import_province_almanak(self):
        IPA = ImportProvinceAlmanak.ImportProvinceAlmanak()
        return IPA.parse_almanak()

    def import_stagen_almanak(self, kamer_name):
        ISGA = ImportStatenGeneraalAlmanak.ImportStatenGeneraalAlmanak()
        return ISGA.parse_almanak(kamer_name)

    def municipality_check(self):
        self.write_to_file(self.match(), './exports/match.json')
        self.write_to_file(self.score(self.import_file('./exports/match.json')), './exports/score.json')
        self.write_to_file(self.best(self.import_file('./exports/score.json')), './exports/best.json')
        self.write_to_file(self.potentials(self.import_file('./exports/score.json')), './exports/potentials.json')

        self.write_to_file(self.final_dataset(self.import_file('./exports/potentials.json'), self.import_file('./data/validated_sample_worst_5percent.json')), './exports/excluded_validation.json')
        self.write_to_file(self.final_dataset(self.import_file('./exports/excluded_validation.json'), self.import_file('./data/validated_sample_any_score.json')), './exports/corrected_almanak.json')
        # self.check_seats_improved(self.import_file('./exports/excluded_validation.json'))

    def municipality_validation(self):
        print()
        # self.optimize_weights(self.import_file('./exports/not_perfect.json')[:181])
        # self.works(self.import_file('./exports/score.json'))
        # self.show_scores(self.import_file('./exports/best.json'))
        # self.write_to_file(self.validate_weights(self.import_file('./exports/best.json')), './validated_sample_any_score.json')
        # self.write_to_file(self.validate_weights_worst(self.import_file('./exports/best.json')), './validated_sample_worst_5percent.json')
        self.plot_correct(self.import_file('./exports/validated_sample_worst_5percent.json'))

    def province_check(self):
        self.write_to_file(self.import_province_almanak(), './exports/province_match.json')
        self.write_to_file(self.score(self.import_file('./exports/province_match.json')),
                           './exports/province_score.json')
        self.write_to_file(self.best(self.import_file('./exports/province_score.json')), './exports/province_best.json')

    def stagen_check(self, kamer_name="Eerste Kamer der Staten-Generaal"):
        self.write_to_file(self.import_stagen_almanak(kamer_name), './exports/staten_generaal_match.json')
        self.write_to_file(self.score(self.import_file('./exports/staten_generaal_match.json')),
                           './exports/staten_generaal_score.json')
        self.write_to_file(self.potentials(self.import_file('./exports/staten_generaal_score.json')),
                           './exports/staten_generaal_potentials.json')

        if kamer_name == "Eerste Kamer der Staten-Generaal":
            self.write_to_file(self.best(self.import_file('./exports/staten_generaal_potentials.json')), './exports/eerste_kamer_best.json')
        elif kamer_name == "Tweede Kamer der Staten-Generaal":
            self.write_to_file(self.best(self.import_file('./exports/staten_generaal_potentials.json')), './exports/tweede_kamer_best.json')

if __name__ == '__main__':
    Main()
