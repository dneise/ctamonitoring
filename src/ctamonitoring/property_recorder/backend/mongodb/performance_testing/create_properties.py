#!/usr/bin/env python
'''
monitest.create_properties -- shortdesc

monitest.create_properties is a description

It defines classes_and_methods

@author: tschmidt
@organization: DESY Zeuthen
@copyright: 2014, cta-observatory.org. All rights reserved.
@version: $Id$
@change: $LastChangedDate$
@change: $LastChangedBy$
@requires: random
@requires: pymongo
'''

from random import seed as randseed
from random import choice as randchoice
from random import randint
from random import uniform
import pymongo
from pymongo import MongoClient


__all__ = []
__version__ = '$Revision$'.split()[1]
__date__ = '2014-01-06'
__updated__ = '$LastChangedDate$'.split()[1]

host = "zoja"
seed = None
#systems = (("SST", 40, 1000), ("MST", 50, 1500), ("LST", 10, 2000),
#           ("SYSTEM_A", 100, 50), ("SYSTEM_B", 10, 250), ("SYSTEM_C", 5, 500),
#           (None, 1, 5000))
systems = (("SST", 4, 300), ("MST", 5, 500), ("LST", 1, 600),
           ("SYSTEM_A", 3, 50), ("SYSTEM_B", 1, 80), ("SYSTEM_C", 1, 160),
           (None, 1, 160))


def create_systems(systems_collection,
                   properties_collection,
                   system_type = "SYSTEM",
                   n_systems = 1, n_properties_per_system = 1000):
    comp_type_descriptions = []
    props_total = 0
    while props_total < n_properties_per_system:
        tmp_n_comps = randchoice((1, 1, 1, 2, 2, 2, 3, 3, 4, 5))
        n_props = randint(5, 30)
        periods = [randchoice((1, 1, 1, 1, 5, 5, 5, 5, 10, 20))
                   for p in range(n_props)]
        for n_comps in range(1, tmp_n_comps + 1):
            if props_total + n_comps * n_props > n_properties_per_system:
                break
        comp_type_descriptions.append((n_comps, periods))
        props_total += n_comps * n_props
        print len(comp_type_descriptions), n_comps, n_props, periods[:10]
    print props_total
    
    if not system_type: n_systems = 1
    for sys_id in range (1, n_systems + 1):
        if system_type:
            system_desc = {
                           "system name" : "%s%d" % (system_type, sys_id),
                           "system type" : system_type,
                           "lock" : None
                          }
        else:
            system_desc = {
                           "lock" : None
                          }
        systems_collection.insert(system_desc)
        for comp_type_id, comp_type_desc in enumerate(comp_type_descriptions, 1):
            for comp_id in range(1, comp_type_desc[0] + 1):
                for prop_id, period in enumerate(comp_type_desc[1], 1):
                    while(True):
                        graph_min = uniform(-1000, 1000)
                        graph_max = uniform(-1000, 1000)
                        if graph_min < graph_max - 1:
                            break
                        if graph_max < graph_min - 1:
                            graph_min, graph_max = graph_max, graph_min
                            break
                    meta = {"graph_min" : graph_min,
                            "graph_max" : graph_max,
                            "period" : period
                           }
                    if system_type:
                        property_desc = {
                                         "system name" : "%s%d" % (system_type, sys_id),
                                         "system type" : system_type,
                                         "component name" : "%s%d.%d.%d" % (system_type, sys_id, comp_type_id, comp_id),
                                         "component type" : "%s%d" % (system_type, comp_type_id),
                                         "property name" : "prop%d" % prop_id,
                                         "property type" : "DOUBLE",
                                         "property_type_desc" : None,
                                         "meta" : meta,
                                         "lock" : None
                                        }
                    else:
                        property_desc = {
                                         "component name" : "Comp%d.%d" % (comp_type_id, comp_id),
                                         "component type" : "CompTyp%d" % comp_type_id,
                                         "property name" : "prop%d" % prop_id,
                                         "property type" : "DOUBLE",
                                         "property_type_desc" : None,
                                         "meta" : meta,
                                         "lock" : None
                                        }
                    properties_collection.insert(property_desc)


if __name__ == '__main__':
    randseed(seed)
    
    client = MongoClient(host)
    db = client.monitest
    properties_collection = db.properties
    systems_collection = db.systems
    
    if systems_collection.count():
        raise RuntimeError("systems already exist")
    if properties_collection.count():
        raise RuntimeError("properties already exist")
    
    properties_collection.ensure_index([
                                        ("system name", pymongo.ASCENDING),
                                        ("component name", pymongo.ASCENDING),
                                        ("property name", pymongo.ASCENDING)
                                       ])
    
    for system_type, n_systems, n_properties_per_system in systems:
        if n_systems and n_properties_per_system:
            create_systems(systems_collection, properties_collection,
                           system_type, n_systems, n_properties_per_system)

