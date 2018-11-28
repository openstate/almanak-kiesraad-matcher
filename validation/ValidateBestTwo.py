from matching import AssignScore

class ValidateBestTwo:
    import json
    import copy

    def __init__(self):
        print("init")

    def import_file(self, file_name):
        with open(file_name) as f:
            data = self.json.load(f)
        return data.get("mapping")

    def flatten_mapping(self, mapping):
        newMap = []
        for mncp in mapping:
            newMap += mncp['mapping']
        return newMap

    def read_file(self, mapping, SW):
        score1 = []
        score2 = []
        for mncp in mapping:
            for member in mncp['mapping']:
                if len(member['maps_with']) > 1:
                    member1 = member['maps_with'][0]['score']
                    member2 = member['maps_with'][1]['score']
                    if member1 != 0 and member2 != 0 and member2 < member1:
                        score1.append(member1)
                        score2.append(member2)

        return self.distance_scatter(score1, score2)

    # loop members etc
    def loop_data(self, SW, mapping_data):
        AS = AssignScore.AssignScore()
        AS.assign_score_all(mapping_data, SW)

    distances = []

    def distance_scatter(self, score1, score2):
        total_distance = 0
        for index in range(len(score1)):
            distance = score1[index] - score2[index]
            total_distance += distance
        avg_distance = total_distance / len(score1)
        return avg_distance

    # create different setups and loop
    def loop_setups(self, mapping_data):
        SW = {
            'gender': 40,
            'last_name': 50,
            'discount_combined_name': 25,
            "initial": 20,
            'first_letter': 20,
            'party': 40,
            'lv_ln_multiplier': 3,
            'lv_in_multiplier': 6,
        }
        self.loop_data(SW, mapping_data)

        f = open('./exports/max_distance_configurations_final.json', 'a')
        best_distance = {'config': SW, 'distance': 0}
        print(self.json.dumps(best_distance))
        f.write(self.json.dumps(best_distance) + "\n")
        f.flush()
        previous_best_weights = {}
        while best_distance['config'] != previous_best_weights:
            previous_best_weights = best_distance['config']
            prev = self.copy.deepcopy(previous_best_weights)

            last_name = prev['last_name'] * 0.8
            while last_name <= prev['last_name'] * 1.2:
                SW["last_name"] = last_name
                last_name += prev['last_name'] * 0.2
                print('last_name ' + str(last_name))

                gender = prev['gender'] * 0.8
                while gender <= prev['gender'] * 1.2:
                    SW["gender"] = gender
                    gender += prev['gender'] * 0.2
                    print('gender ' + str(gender))

                    discount_combined_name = prev['discount_combined_name'] * 0.8
                    while discount_combined_name <= prev['discount_combined_name'] * 1.2:
                        SW["discount_combined_name"] = discount_combined_name
                        discount_combined_name += prev['discount_combined_name'] * 0.2
                        print('discount_combined_name ' + str(discount_combined_name))

                        initial = prev['initial'] * 0.8
                        while initial <= prev['initial'] * 1.2:
                            SW["initial"] = initial
                            initial += prev['initial'] * 0.2

                            first_letter = prev['first_letter'] * 0.8
                            while first_letter <= prev['first_letter'] * 1.2:
                                SW["first_letter"] = first_letter
                                first_letter += prev['first_letter'] * 0.2

                                party = prev['party'] * 0.8
                                while party <= prev['party'] * 1.2:
                                    SW["party"] = party
                                    party += prev['party'] * 0.2

                                    lv_ln_multiplier = prev['lv_ln_multiplier'] * 0.8
                                    while lv_ln_multiplier <= prev['lv_ln_multiplier'] * 1.2:
                                        SW["lv_ln_multiplier"] = lv_ln_multiplier
                                        lv_ln_multiplier += prev['lv_ln_multiplier'] * 0.2

                                        lv_in_multiplier = prev['lv_in_multiplier'] * 0.8
                                        while lv_in_multiplier <= prev['lv_in_multiplier'] * 1.2:
                                            SW["lv_in_multiplier"] = lv_in_multiplier
                                            lv_in_multiplier += prev['lv_in_multiplier'] * 0.2

                                            self.loop_data(SW, mapping_data)
                                            this_distance = self.read_file(mapping_data, SW)

                                            if this_distance > best_distance['distance']:
                                                best_distance = {'config': self.copy.deepcopy(SW),
                                                                 'distance': this_distance}
            print(previous_best_weights)
            print(best_distance['config'])
            print(best_distance)
            f.write(self.json.dumps(best_distance) + "\n")
            f.flush()
        print('done')


if __name__ == "__main__":
    ValidateBestTwo()
