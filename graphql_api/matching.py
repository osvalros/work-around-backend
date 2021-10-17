from collections import defaultdict
from typing import List
import itertools

import networkx as nx

from graphql_api.models import Application

"""
SHELL TESTING:
from graphql_api.matching import MatchingAlgorithm
a = MatchingAlgorithm()
a.find_matching_application_sets()
"""

class MatchingAlgorithm:
    """AI-powered algorithm to compute matchings among applicants"""

    def __init__(self):
        pass

    def find_matching_application_sets(self) -> List[List[str]]:
        all_applications = Application.objects.prefetch_related(
            "property__city", "preferred_cities").filter(accepted=False)

        application_groups = defaultdict(list)

        for app in all_applications:
            group_by = self.get_group_by_attributes(app)
            application_groups[group_by].append(app)

        all_cycles = []

        for application_group in application_groups.values():
            cycles = self.find_cycles_in_group(application_group)
            all_cycles += cycles

        return all_cycles

    def find_cycles_in_group(self, application_group: List[Application]):
        G = nx.DiGraph()
        G.add_nodes_from([a.id for a in application_group])

        # maps cities to all applications offering a property in that city
        property_city_to_applications_map = defaultdict(list)
        for application in application_group:
            property_city_to_applications_map[application.property.city_id]\
                .append(application.id)

        for application in application_group:
            for city in application.preferred_cities.all():
                matching_application_ids = [
                    # just in case
                    a_id for a_id in property_city_to_applications_map[city.id]
                    if a_id != application.id
                ]
                edges = [(application.id, matching_id) for matching_id in matching_application_ids]
                G.add_edges_from(edges)

        simple_cycles = nx.simple_cycles(G)
        return list(simple_cycles)

    def get_group_by_attributes(self, application: Application):
        return application.length_of_stay,

