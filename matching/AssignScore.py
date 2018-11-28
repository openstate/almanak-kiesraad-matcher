from CONFIG import CONFIG
import json

class AssignScore:
    def assign_score_all(self, mapping, scoring_weights=CONFIG.SCORING_WEIGHTS):
        print(scoring_weights)
        for mncp in mapping:
            party_map_mncp = []
            full_party_map = self.import_file('./data/almanak_kiesraad_party_mapping.json')
            for prty_mncp in full_party_map:
                if prty_mncp.get("municipality_name") == mncp.get("municipality_name"):
                    party_map_mncp = prty_mncp.get("party_mapping")
            for almk_rlid in mncp.get('mapping'):
                self.assign_scores(almk_rlid, party_map_mncp, scoring_weights)
        return mapping

    def assign_scores(self, almk_rlid, party_map_mncp, SW):
        maps_with = almk_rlid.get("maps_with")
        if maps_with:
            max_score = SW.get("gender") + SW.get('last_name') + SW.get('party') + max(SW.get("first_letter"), SW.get("initial"))
            for cndt in maps_with:
                score = self.calculate_match_chance(cndt, almk_rlid, party_map_mncp, SW)
                cndt['score'] = score / max_score
            almk_rlid['maps_with'] = sorted(almk_rlid.get('maps_with'), key=lambda x: x['score'], reverse=True)

    # assign score to mapping
    def calculate_match_chance(self, cndt, almk_rlid, prty_map, SW):
        ar_party = almk_rlid.get("party_allmanak")
        cndt_party = cndt.get("party")

        score = 0
        gender_match = almk_rlid.get("gender_allmanak") == cndt.get("gender")
        if gender_match:
            score += SW["gender"]
        elif (cndt.get("gender") == "undefined" and not almk_rlid.get("gender_allmanak") == "undefined") \
                or (almk_rlid.get("gender_allmanak") == "undefined" and not cndt.get("gender") == "undefined"):
            score += SW["gender"]

        if cndt.get("combined_name_match"):
            cmatch = (SW["last_name"] - SW["discount_combined_name"])
            if cmatch > 0:
                score += cmatch
        else:
            score_disc_ln = (SW["last_name"] - (int(cndt.get("ln_levenshtein_distance")) * SW["lv_ln_multiplier"]))
            if score_disc_ln > 0:
                score += score_disc_ln

        if not cndt.get("initials_match") and cndt.get("firstnameletter_matches_init"):
            score += SW["first_letter"]
        else:
            score_disc_in = (SW["initial"] - (
                    int(cndt.get("in_levenshtein_distance")) * SW["lv_in_multiplier"]))
            if score_disc_in > 0:
                score += score_disc_in

        count_party_high = 0
        for mapping in prty_map:
            if ar_party == mapping.get("al") and cndt_party == mapping.get("kr"):
                score += SW["party"]
                count_party_high += 1

        if count_party_high > 1:
            print("ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERRORERROR ERROR ERROR ERROR ERROR ERRORERROR")
        return score

    def import_file(self, file_name):
        with open(file_name) as f:
            data = json.load(f)
        return data.get('mapping')
