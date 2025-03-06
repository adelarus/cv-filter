import json
'''
[
    [
        "CV_Rus_Adela.pdf",
        0.5742932806670502,
        "{\"skill\": \"Java\", \"years\": 12}"
    ],
    [
        "CV_Rus_Adela.pdf",
        0.758156409421658,
        "{\"skill\": \"JPA\", \"years\": 12}"
    ]
    ]
'''

def calculate_score(matches_list):
    final_scores = {}

    for match in matches_list:
        cv_name = match[0]
        skill_json = json.loads(match[2])
        skill = skill_json['skill']
        years = skill_json['years']
        similarity = match[1]

        if cv_name not in final_scores:
            final_scores[cv_name] = {'cv_name': cv_name, 'score': 0, 'skills': []}
        
        final_scores[cv_name]['score'] += similarity
        final_scores[cv_name]['skills'].append({'skill': skill, 'years': years})

    return final_scores