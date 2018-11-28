import json
import pprint as pp


class CreateGraphs:
    def __init__(self):
        print()
        # self.weights_distance(self.import_distance_file('../exports/max_distance_configurations_final.json'))

    def import_distance_file(self, file_name):
        mns = {"gender": [],
               "last_name": [],
               "discount_combined_name": [],
               "initial": [],
               "first_letter": [],
               "party": [],
               "lv_ln_multiplier": [],
               "lv_in_multiplier": [],
               "distance": []}

        with open(file_name) as f:
            for line in f.readlines():
                data = json.loads(line)
                for key in mns.keys():
                    if key != 'distance':
                        mns[key].append(data.get('config').get(key))
                    else:
                        mns['distance'].append(data.get('distance'))
        return mns

    def weights_distance(self, data):
        from matplotlib import pyplot as plt

        fig = plt.figure(figsize=(8, 5))
        ax = fig.add_subplot(111)
        ax.set_title("Score Weight versus Distance")
        ax.set_xlabel("Distance")
        ax.set_ylabel("Weight")
        for k, v in data.items():
            if k != 'distance':
                ax.plot(data.get('distance'), v, label=k)

        fig.legend()
        fig.savefig('weights_distance.png', dpi=300)
        fig.show()

    def plot_scores(self, mapping):
        from matplotlib import pyplot as plt
        data = []
        for mncp in mapping:
            for rlid in mncp.get('mapping'):
                for cndt in rlid.get('maps_with'):
                    if not isinstance(cndt, str):
                        if cndt.get('score') < 0.001:
                            data.append(cndt.get('score'))
                            pp.pprint(rlid)
        plt.hist(data, bins=1000)
        plt.show()

    def plot_incorrect_distance(self, flat_map):
        from matplotlib import pyplot as plt
        from matplotlib import interactive
        interactive(True)
        score_correct = []
        score_incorrect = []
        for member in flat_map:
            score = member.get('maps_with')[0].get('score')
            if score < 0.2:
                if member.get('correct') == 'y':
                    score_correct.append(score)
                else:
                    score_incorrect.append(score)
        plt.hist([score_correct, score_incorrect], 10, histtype='bar', color=['green', 'red'], label=['correct', 'incorrect'])
        plt.title('Number of (in)correct matches for scores (part 1)')
        plt.xlabel('Matching score')
        plt.ylabel('Number of matches')
        plt.legend()
        plt.show()
        print("Percentage below score 0.2 incorrect: " + str(len(score_incorrect) / (len(score_incorrect) + len(score_correct)) * 100))

        score_correct = []
        score_incorrect = []
        for member in flat_map:
            score = member.get('maps_with')[0].get('score')
            if score >= 0.2:
                if member.get('correct') == 'y':
                    score_correct.append(score)
                else:
                    score_incorrect.append(score)
        plt.hist([score_correct, score_incorrect], 10, histtype='bar', color=['green', 'red'], label=['correct', 'incorrect'])
        plt.title('Number of (in)correct matches for scores (part 2)')
        plt.xlabel('Matching score')
        plt.ylabel('Number of matches')
        plt.legend()
        plt.show()
        print("Percentage above score 0.2 incorrect: " + str(len(score_incorrect) / (len(score_incorrect) + len(score_correct)) * 100))

        score_correct = []
        score_incorrect = []
        for member in flat_map:
            score = member.get('maps_with')[0].get('score')
            if member.get('correct') == 'y':
                score_correct.append(score)
            else:
                score_incorrect.append(score)
        print("Total percentage incorrect: " + str(len(score_incorrect) / (len(score_incorrect) + len(score_correct)) * 100))

if __name__ == "__main__":
    CreateGraphs()
