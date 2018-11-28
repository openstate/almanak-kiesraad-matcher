class MappingValidation:
    import json
    import random

    mncp_sample_size = 80
    member_sample_size = 5

    def import_file(self, file_name):
        with open(file_name) as f:
            data = self.json.load(f)
        return data.get('mapping')

    def __init__(self):
        print()
        # mapping = self.import_file('final_mapping.json')
        # self.random.seed('allmanak')
        # sample = self.get_sample(mapping)
        # # sample = self.validate_whole_set(mapping)
        # validated_sample = self.validate_sample(sample)
        # self.write_sample_results(validated_sample)

    def get_sample(self, mapping):
        import matplotlib.pyplot as plt
        sample_list_mncp = []

        total_sample = []
        self.random.seed('almanak')
        sample_indexes_mncp = self.random.sample(range(len(mapping)), self.mncp_sample_size)
        for index in sample_indexes_mncp:
            sample_list_mncp.append(mapping[index])

        for mncp in sample_list_mncp:
            sample_list_member = []
            sample_indexes_member = self.random.sample(range(len(mncp.get('mapping'))), self.member_sample_size)
            member_mapping = mncp.get('mapping')
            for index in sample_indexes_member:
                sample_list_member.append(member_mapping[index])
            total_sample.append({'muncipality_name': mncp.get('municipality_name'), 'members': sample_list_member})

        mncp_names = [m['municipality_name'] for m in sample_list_mncp]
        mncp_no_rdsl = [len(m['mapping']) for m in sample_list_mncp]

        print(total_sample)
        plt.hist(x=mncp_no_rdsl, bins=range(45))
        plt.xlabel('Number of seats in municipality')
        plt.ylabel('Number of municipalities')
        plt.title('Distribution of municipality sizes in sample')
        plt.show()
        print(self.random.randrange(len(mapping))) #len = 373
        return total_sample

    def validate_whole_set(self, mapping):
        total_sample = []
        for mncp in mapping:
            list_member = mncp.get('mapping')
            if len(list_member) > 0:
                total_sample.append({'muncipality_name': mncp.get('municipality_name'), 'members': list_member})
        return total_sample

    def get_worst_scores(self, mapping):
        rlid_count = 0
        for mncp in mapping:
            for rlid in mncp.get('mapping'):
                rlid_count += 1
        map = self.flatten_mapping(mapping)
        sorted_map = sorted(map, key=lambda x: x.get("maps_with")[0].get("score"), reverse=False)
        return sorted_map[:int(len(sorted_map)/20)]

    def flatten_mapping(self, mapping):
        newMap = []
        for mncp in mapping:
            for rlid in mncp.get('mapping'):
                if len(rlid.get('maps_with')) > 0 and rlid.get('maps_with')[0] != "":
                    rlid['municipality'] = mncp.get('municipality_name')
                    newMap.append(rlid)
        return newMap

    def validate_sample(self, sample):
        import json
        count = 1
        total_count = 0
        for mncp in sample:
            total_count += len(mncp['members'])
        for mncp in sample:
            for member in mncp['members']:
                print(json.dumps(member, indent=4))
                correct_input = False
                answer = ""
                while not correct_input:
                    print("Answered " + str(count) + " out of " + str(total_count))
                    answer = input('Is the mapping with the best score correct? (y/n)')
                    correct_input = True if answer == 'y' or answer == 'n' else False
                member['correct'] = answer
                count += 1
        return sample

    def validate_sample2(self, sample):
        import json
        count = 1
        total_count = len(sample)
        for member in sample:
            print(json.dumps(member, indent=4))
            correct_input = False
            answer = ""
            while not correct_input:
                print("Answered " + str(count) + " out of " + str(total_count))
                answer = input('Is the mapping with the best score correct? (y/n)')
                correct_input = True if answer == 'y' or answer == 'n' else False
            member['correct'] = answer
            count += 1
        return sample

    def validate_best(self, best_mapping):
        import json
        count = 1
        total_count = 0
        for mncp in best_mapping:
            total_count += len(mncp['mapping'])
        for mncp in best_mapping:
            for rlid in mncp.get('mapping'):
                print(json.dumps(rlid, indent=4))
                correct_input = False
                answer = ""
                while not correct_input:
                    print("Answered " + str(count) + " out of " + str(total_count))
                    answer = input('Is the mapping with the best score correct? (y/n)')
                    correct_input = True if answer == 'y' or answer == 'n' else False
                rlid['correct'] = answer
                count += 1
        return best_mapping

    def write_sample_results(self, validation_results):
        import json
        f = open('./exports/validation_results_under_111.json', 'w')
        f.write('{ "mncp_sample_size":'+str(self.mncp_sample_size)+', "member_sample_size":'+str(self.member_sample_size)+',"mapping": [')
        for item in validation_results:
            f.write(json.dumps(item) + ",\n")
        f.write("]}")
        print('done')


if __name__ == "__main__":
    MappingValidation()
