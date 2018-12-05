import copy

class ExportDataset:
    @staticmethod
    def get_best_mapping(final_mapping):
        cpy_fnl = copy.deepcopy(final_mapping)
        for mncp in cpy_fnl:
            for lid in mncp.get('mapping'):
                maps_with = lid.get('maps_with')
                best_map = lid.get('maps_with')[0] if len(lid.get('maps_with')) > 0 else ""
                for map in maps_with:
                    if map.get('score') > best_map.get('score'):
                        best_map = map
                lid['maps_with'] = [best_map]
        return cpy_fnl

    @staticmethod
    def get_best_mapping_under(final_mapping, score):
        cpy_fnl = copy.deepcopy(final_mapping)
        new_mapping = []
        for mncp in cpy_fnl:
            mncp_mapping_wscore = {'municipality_name': mncp.get('municipality_name'), 'mapping': []}
            new_mapping.append(mncp_mapping_wscore)
            for lid in mncp.get('mapping'):
                best_map = lid.get('maps_with')[0] if len(lid.get('maps_with')) > 0 else []
                best_map2 = lid.get('maps_with')[1] if len(lid.get('maps_with')) > 1 else []
                lid['maps_with'] = [best_map, best_map2]
                if best_map != [] and best_map.get('score') < score:
                    mncp_mapping_wscore['mapping'].append(lid)
        return new_mapping

    @staticmethod
    def get_best2_mapping_under(final_mapping, score2):
        cpy_fnl = copy.deepcopy(final_mapping)
        new_mapping = []
        for mncp in cpy_fnl:
            mncp_mapping_wscore = {'municipality_name': mncp.get('municipality_name'), 'mapping': []}
            new_mapping.append(mncp_mapping_wscore)
            for lid in mncp.get('mapping'):
                best_map = lid.get('maps_with')[0] if len(lid.get('maps_with')) > 1 else []
                best_map2 = lid.get('maps_with')[1] if len(lid.get('maps_with')) > 1 else []
                lid['maps_with'] = [best_map, best_map2]
                if best_map != [] and int(best_map.get('score_new')) < score2:
                    mncp_mapping_wscore['mapping'].append(lid)
        return new_mapping

    @staticmethod
    def get_best_mapping_above(final_mapping, score):
        cpy_fnl = copy.deepcopy(final_mapping)
        new_mapping = []
        for mncp in cpy_fnl:
            mncp_mapping_wscore = {'municipality_name': mncp.get('municipality_name'), 'mapping': []}
            new_mapping.append(mncp_mapping_wscore)
            for lid in mncp.get('mapping'):
                best_map = lid.get('maps_with')[0] if len(lid.get('maps_with')) > 1 else []
                best_map2 = lid.get('maps_with')[1] if len(lid.get('maps_with')) > 1 else []
                lid['maps_with'] = [best_map, best_map2]
                if best_map != [] and int(best_map.get('score')) > score:
                    mncp_mapping_wscore['mapping'].append(lid)
        return new_mapping

    @staticmethod
    def get_not_perfect(final_mapping):
        count = 0
        cpy_fnl = copy.deepcopy(final_mapping)
        new_mapping = []
        for mncp in cpy_fnl:
            mncp_mapping_wscore = {'municipality_name': mncp.get('municipality_name'), 'mapping': []}
            new_mapping.append(mncp_mapping_wscore)
            for lid in mncp.get('mapping'):
                # if lid['maps_with'] != [] and lid['maps_with'][0]['ln_levenshtein_distance'] != 0 and lid['maps_with'][0]['in_levenshtein_distance'] != 0:
                #     mncp_mapping_wscore['mapping'].append(lid)
                #     count += 1
                if len(lid['maps_with']) > 1:
                    mncp_mapping_wscore['mapping'].append(lid)
                    count += 1
        print(count)
        return new_mapping

    @staticmethod
    def get_sample(mapping, size):
        count = 0
        sample = []
        for item in mapping:
            for member in item['mapping']:
                if len(member['maps_with']) > 1:
                    sample.append(member)
                    count += 1
                if count == size:
                    break
            if count == size:
                break
        return sample


    @staticmethod
    def get_potentials(mapping):
        SCORE_LIMIT = 0.0034
        for mncp in mapping:
            to_be_removed = []
            unsure_matches = []
            for rlid in mncp.get('mapping'):
                if len(rlid.get('maps_with')) > 1 and rlid.get('maps_with')[0].get('score') > SCORE_LIMIT:
                    new_maps_with = [rlid.get('maps_with')[0]]
                    i = 1
                    while i < len(rlid.get('maps_with')) and rlid.get('maps_with')[0].get('score') != 1.0 and \
                            rlid.get('maps_with')[i].get('score') / rlid.get('maps_with')[0].get('score') > 0.9:
                        new_maps_with.append(rlid.get('maps_with')[i])
                        i += 1
                    rlid['maps_with'] = new_maps_with
                elif len(rlid.get('maps_with')) > 0 and rlid.get('maps_with')[0].get('score') <= SCORE_LIMIT:
                    unsure_matches.append(rlid)
                    to_be_removed.append(rlid)
                elif len(rlid.get('maps_with')) == 0:
                    to_be_removed.append(rlid)
            mncp['mapping'] = [value for value in mncp.get('mapping') if value not in to_be_removed]
            mncp['unsure_matches'] = unsure_matches
        return mapping
