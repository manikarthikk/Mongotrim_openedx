from pymongo import MongoClient
from bson import ObjectId
client = MongoClient()

db = client.edxapp


collection = db.modulestore.structures
available_version_listwith_prev_original = []

available_version_listwith_id_val = []
for j in db.modulestore.structures.find({ },{"previous_version":1,"original_version":1} ):
    available_version_listwith_prev_original.append(j)
    #print j

for j in db.modulestore.structures.find({ },{"_id":1} ):
    available_version_listwith_id_val.append(j)
#print available_version_listwith_id_val
list_of_avail_id =  [d['_id'] for d in available_version_listwith_id_val if '_id' in d]
#print list_of_avail_id
#print available_version_listwith_prev_original 

def search_dictionaries(key, value, list_of_dictionaries):
    for element in list_of_dictionaries:
        if element[key] == value:
            return element

for each in available_version_listwith_prev_original:
    #while each["previous_version"] not in list_of_avail_id and each["previous_version"] != None:
    if each["previous_version"] == None:
        print "Hi None"
    elif each["previous_version"] not in list_of_avail_id and each["previous_version"] != None:
        a = []
        b = []
        c = []
        a.append(each['_id'])
        b.append(each['previous_version'])
        c.append(each['original_version'])
        print a
        print b
        print c
        db.modulestore.structures.update({ '_id': {'$in':a}}, { '$set': { "previous_version" : c[0]}   })
    else:
        print "Hi from else"
    """else:
        if each["previous_version"] == None:
            print "hi"
        else:
            print "hi2"
"""

