from pymongo import MongoClient

client = MongoClient()

db = client.edxapp

collection = db.modulestore.structures
available_version_list_with_prev_original = []

available_version_list_with_id_val = []
for j in db.modulestore.structures.find({}, {"previous_version": 1, "original_version": 1}):
    available_version_list_with_prev_original.append(j)
    # print j

for j in db.modulestore.structures.find({}, {"_id": 1}):
    available_version_list_with_id_val.append(j)
# print available_version_listwith_id_val
list_of_avail_id = []
for d in available_version_list_with_id_val:
    if '_id' in d:
        list_of_avail_id.append(d['_id'])


# print list_of_avail_id

# print available_version_list_with_prev_original

def search_dictionaries(key, value, list_of_dictionaries):
    for element in list_of_dictionaries:
        if element[key] == value:
            return element


for each in available_version_list_with_prev_original:
    if each["previous_version"] is None:
        print "Hi None"
    elif each["previous_version"] not in list_of_avail_id and each["previous_version"] is not None:
        a = []
        b = []
        c = []
        a.append(each['_id'])
        b.append(each['previous_version'])
        c.append(each['original_version'])
        print a
        print b
        print c
        db.modulestore.structures.update({'_id': {'$in': a}}, {'$set': {"previous_version": c[0]}})
    else:
        print "*"
