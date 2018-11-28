import json
import pprint as pp

class ScoreWorks:
    def import_file(self, file_name):
        with open(file_name) as f:
            data = json.load(f)
        return data.get('mapping')

    def check(self, mapping):
        wrong = []
        count = 0
        for mncp in mapping:
            for member in mncp['mapping']:
                if len(member['maps_with']) > 1 and member['maps_with'][0]['score'] < member['maps_with'][1]['score']:
                    wrong.append(member)
                if len(member['maps_with']) > 1 and member['maps_with'][0]['name']:
                    count += 1

        pp.pprint(wrong)
        print(len(wrong))
        print(count)

    def find_person(self, mapping, name):
        result = []
        for mncp in mapping:
            for rlid in mncp.get('mapping'):
                if rlid.get('name_allmanak') == name:
                    result.append(rlid)
        return result


if __name__ == "__main__":
    ScoreWorks()
