import numpy as np
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

class Matches:

    def __init__(self):
        self.matches_list = []

    def add_matches(self, skill_query, skill_response):
        self.matches_list.append({'query':skill_query, 'candidates':skill_response})

    def calculate_scores(self):
        final_scores = {}

        for match_set in self.matches_list:

            expected_years = int(match_set['query']['years'])
            query_skill = match_set['query']['skill']
            available_points = 1

            for candidate in match_set['candidates']:

                cv_name = candidate[0]
                skill_json = json.loads(candidate[2])
                skill = skill_json['skill']
                years = int(skill_json['years']) if skill_json['years'] is not None else 0
                points = available_points if years >= expected_years else 0
                available_points -= 0.1

                if cv_name not in final_scores:
                    final_scores[cv_name] = {'cv_name': cv_name, 'score': max(0, points), 'skills': [skill]}
                else:
                    final_scores[cv_name]['score'] += max(0, points)
                    final_scores[cv_name]['skills'].append(skill)

        #Normalize the scores using softmax        
        scores = np.array([final_scores[cv]['score'] for cv in final_scores])
        softmax_scores = np.exp(scores) / np.sum(np.exp(scores))

        for i, cv_name in enumerate(final_scores):
            final_scores[cv_name]['score'] = (softmax_scores[i] * 100).round(2)

        # Sort the scores
        final_scores = dict(sorted(final_scores.items(), key=lambda x: x[1]['score'], reverse=True))

        print(f'Final scores: {final_scores}')

        return final_scores