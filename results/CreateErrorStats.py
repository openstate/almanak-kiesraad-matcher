import numpy
import random
import pprint as pp
import itertools

class CreateErrorStats:

    @staticmethod
    def create_stats(mapping, return_totals=False):
        stats = []
        total_members = 0

        for mncp in mapping:
            mns = {
                'municipality_name': mncp.get('municipality_name'),
                'name_not_map': 0,
                'gender_not_map': 0,
                'gender_undefined_al': 0,
                'gender_undefined_kr': 0,
                'party_not_map': 0,
                'could_not_map': 0,
                'prefix_missing': 0,
                'first_letter_initial': 0,
                'spelling_mistake_initial': 0,
                'spelling_mistake_lname': 0,
                'combined_name_mistake': 0,
                'unsure_matches': len(mncp.get('unsure_matches'))
            }

            for member in mncp.get('mapping'):
                best_map = member['maps_with'][0] if len(member['maps_with']) > 0 else None
                mgender = member['gender_allmanak']
                mname = member['name_allmanak']
                mparty = member['party_allmanak']
                
                if best_map:
                    bname = best_map['name']['initials'] + " " + best_map['name']['prefix'] + best_map['name']['last_name']
                    bgender = best_map['gender']
                    bparty = best_map['party']
                    lv_ln = best_map['ln_levenshtein_distance']
                    lv_in = best_map['in_levenshtein_distance']
                    cbn = best_map['combined_name_match']
                    im = best_map['initials_match']
                    fstl = best_map['firstnameletter_matches_init']
                    if mname != bname:
                        mns['name_not_map'] += 1
                    if mgender == 'undefined':
                        mns['gender_undefined_al'] += 1
                    if bgender == 'undefined':
                        mns['gender_undefined_kr'] += 1
                    if mgender != bgender and (mgender != "undefined" and bgender != "undefined"):
                        mns['gender_not_map'] += 1

                    if bparty != mparty:
                        mns['party_not_map'] += 1
                    if best_map['name']['prefix'] not in mname:
                        mns['prefix_missing'] += 1

                    if lv_in != 0:
                        mns['spelling_mistake_initial'] += 1
                    if lv_ln != 0:
                        mns['spelling_mistake_lname'] += 1
                    if cbn:
                        mns['combined_name_mistake'] += 1
                    if not im and fstl:
                        mns['first_letter_initial'] += 1
                total_members += 1
            mns['could_not_map'] = len(mncp.get('unmappable'))
            total_members += len(mncp.get('unmappable'))

            stats.append(mns)

        totals = {
            'total_members': total_members,
            'name_not_map': sum(item['name_not_map'] for item in stats),
            'gender_not_map': sum(item['gender_not_map'] for item in stats),
            'gender_undefined_al': sum(item['gender_undefined_al'] for item in stats),
            'gender_undefined_kr': sum(item['gender_undefined_kr'] for item in stats),
            'party_not_map': sum(item['party_not_map'] for item in stats),
            'could_not_map': sum(item['could_not_map'] for item in stats),
            'prefix_missing': sum(item['prefix_missing'] for item in stats),
            'first_letter_initial': sum(item['first_letter_initial'] for item in stats),
            'spelling_mistake_initial': sum(item['spelling_mistake_initial'] for item in stats),
            'spelling_mistake_lname': sum(item['spelling_mistake_lname'] for item in stats),
            'combined_name_mistake': sum(item['combined_name_mistake'] for item in stats)
        }
        return totals if return_totals else stats

    @staticmethod
    def create_stats_examples(mapping, number_examples):
        stats = []
        total_members = 0
        for mncp in mapping:
            name = mncp.get('municipality_name')
            mns = {
                'name_not_map': [],
                'gender_not_map': [],
                'gender_undefined_al': [],
                'gender_undefined_kr': [],
                'party_not_map': [],
                'could_not_map': [],
                'prefix_missing': [],
                'first_letter_initial': [],
                'spelling_mistake_initial': [],
                'spelling_mistake_lname': [],
                'combined_name_mistake': []
            }

            for member in mncp.get('mapping'):
                best_map = member['maps_with'][0] if len(member['maps_with']) > 0 else None
                mgender = member['gender_allmanak']
                mname = member['name_allmanak']
                mparty = member['party_allmanak']

                if best_map:
                    bname = best_map['name']['initials'] + " " + best_map['name']['prefix'] + best_map['name'][
                        'last_name']
                    bgender = best_map['gender']
                    bparty = best_map['party']
                    lv_ln = best_map['ln_levenshtein_distance']
                    lv_in = best_map['in_levenshtein_distance']
                    cbn = best_map['combined_name_match']
                    im = best_map['initials_match']
                    fstl = best_map['firstnameletter_matches_init']
                    if mname != bname:
                        mns['name_not_map'].append(member)
                    if mgender == 'undefined':
                        mns['gender_undefined_al'].append(member)
                    if bgender == 'undefined':
                        mns['gender_undefined_kr'].append(member)
                    if mgender != bgender and (mgender != "undefined" and bgender != "undefined"):
                        mns['gender_not_map'].append(member)

                    if bparty != mparty:
                        mns['party_not_map'].append(member)
                    if best_map['name']['prefix'] not in mname:
                        mns['prefix_missing'].append(member)

                    if lv_in != 0:
                        mns['spelling_mistake_initial'].append(member)
                    if lv_ln != 0:
                        mns['spelling_mistake_lname'].append(member)
                    if cbn:
                        mns['combined_name_mistake'].append(member)
                    if not im and fstl:
                        mns['first_letter_initial'].append(member)
                total_members += 1
            mns['could_not_map'] = mncp.get('unmappable')
            total_members += len(mncp.get('unmappable'))

            stats.append({'municipality_name': name, 'stats': mns})

        stats = [stat.get('stats') for stat in stats]
        random.seed("almanak")
        examples = {}
        for key in mns.keys():
            ne = number_examples
            if len([x for y in [item.get(key) for item in stats] for x in y]) <= number_examples:
                ne = len([x for y in [item.get(key) for item in stats] for x in y])
            examples[key] = random.sample([x for y in [item.get(key) for item in stats] for x in y], ne)

        return examples

if __name__ == "__main__":
    CreateErrorStats()
