class CreateFinalDataSets:

    def __init__(self):
        print()

    def remove_incorrect(self, mapping, validated_mapping):
        incorrect = [rlid for rlid in validated_mapping if rlid.get('correct') == 'n']
        for mncp in mapping:
            for rlid in incorrect:
                if rlid.get('municipality') == mncp.get('municipality_name'):
                    mncp['unmappable'].append({'name': rlid.get('name_original'), 'party': rlid.get('party_allmanak'), 'reason': 'score_too_low'})
                    for member in mncp.get('mapping'):
                        if member.get('name_allmanak') == rlid.get('name_allmanak') and member.get('party_allmanak') == rlid.get('party_allmanak'):
                            mncp['mapping'].remove(member)
        return mapping
