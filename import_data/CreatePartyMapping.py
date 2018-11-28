class CreatePartyMapping:
    import Levenshtein as lv
    import json
    from difflib import SequenceMatcher

    def __init__(self):
        data = self.import_file('final_mapping.json')
        self.create_party_mapping(data)
        # self.merge_mapping_files('final_party_mapping.json', 'manual_mapped_parties.json', 'merges_parties.json')
        print('DONE')

    def import_file(self, file_name):
        with open(file_name) as f:
            data = self.json.load(f)
        return data.get('mapping')

    def create_file(self, file_name, mapping):
        f = open(file_name, 'w')
        f.write('{ "mapping": [')
        for item in mapping:
            f.write(self.json.dumps(item) + ",\n")
        f.write("]}")
        print('done')

    def get_abbreviation(self, name):
        abbrv = "".join(e[0] for e in str.split(name))
        if len(abbrv) < 3:
            abbrv = "ABBREVIATION TOO SHORT - THIS STRING WONT MATCH"
        return abbrv

    def create_party_mapping(self, final_data):
        big_nine_names = ['vvd', 'd66', 'pvda', 'cda', 'christenunie', 'pvv', 'sgp', 'sp', 'groenlinks', 'cusgp']
        final_party_mapping = []
        unmappable_parties = []
        all_party_mapping = []
        unmappable_count = 0

        for gmnt in final_data:
            party_mapping = []
            party_unmap = []
            for ar in gmnt.get('mapping'):
                maps_with = ar.get('maps_with')
                for cndt in maps_with:
                    cndt_name_data = cndt.get('name')
                    cndt_name = cndt_name_data.get('initials') + " " + cndt_name_data.get('prefix') + cndt_name_data.get('last_name')
                    if ar.get('name_allmanak') == cndt_name:
                        abbrv_pa = self.get_abbreviation(ar.get('party_allmanak').lower())
                        abbrv_pc = self.get_abbreviation(cndt.get('party').lower())

                        tknz_pa = "".join(e for e in ar.get('party_allmanak').lower() if e.isalnum())
                        tknz_pc = "".join(e for e in cndt.get('party').lower() if e.isalnum())

                        # longest common substring problem
                        sqm = self.SequenceMatcher(None, tknz_pa, tknz_pc)
                        matching_blocks = sqm.get_matching_blocks()
                        total_matching_size = 0
                        for mb in matching_blocks:
                            total_matching_size += mb.size

                        if tknz_pa in tknz_pc or tknz_pc in tknz_pa or abbrv_pa in tknz_pc or abbrv_pc in tknz_pa:
                            party_mapping.append({'al': ar.get('party_allmanak'), 'kr': cndt.get('party')})
                        elif total_matching_size > 8:
                            party_mapping.append({'al': ar.get('party_allmanak'), 'kr': cndt.get('party'), 'mb_size': total_matching_size})
                        elif tknz_pa not in big_nine_names:
                            party_unmap.append({'al': ar.get('party_allmanak'), 'kr': cndt.get('party')})

            party_mapping = [dict(t) for t in {tuple(d.items()) for d in party_mapping}]
            party_unmap = [dict(t) for t in {tuple(d.items()) for d in party_unmap}]
            unmappable_count += len(party_unmap)
            if all_party_mapping:
                # all_party_mapping.extend(party_mapping)
                counter = 0
            else:
                all_party_mapping = party_mapping

            final_party_mapping.append({'municipality_name': gmnt.get('municipality_name'), 'party_mapping': party_mapping})
            if len(party_unmap) > 0:
                unmappable_parties.append({'municipality_name': gmnt.get('municipality_name'), 'party_mapping': party_unmap})

        print("unmap count " + str(unmappable_count))
        self.create_file('final_party_mapping.json', final_party_mapping)
        self.create_file('all_party_mapping.json', [dict(t) for t in {tuple(d.items()) for d in all_party_mapping}])
        self.create_file('unmappable_parties.json', unmappable_parties)

        return [dict(t) for t in {tuple(d.items()) for d in all_party_mapping}]

    def merge_mapping_files(self, fn1, fn2, output_name):
        mapping1 = self.import_file(fn1)
        mapping2 = self.import_file(fn2)
        for munip2 in mapping2:
            for munip1 in mapping1:
                if munip1.get('municipality_name') == munip2.get('municipality_name'):
                    pm1 = munip1.get('party_mapping')
                    pm2 = munip2.get('party_mapping')
                    pm1.extend(pm2)

        self.create_file(output_name, mapping1)

if __name__ == "__main__":
    CreatePartyMapping()
