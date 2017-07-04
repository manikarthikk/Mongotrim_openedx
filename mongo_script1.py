from pymongo import MongoClient

client = MongoClient()

db = client.edxapp

collection = db.modulestore.active_versions
required_version_list = []
versions_not_to_be_deleted = 0
available_version_list = []
available_version_list_with_prev_original = []
for value in collection.find({}, {"versions.draft-branch": 1, "versions.published-branch": 1, "versions.library": 1, }):
    required_version_list.append(value)
versions = [d['versions'] for d in required_version_list]
for value in versions:
    if u'library' not in value:
        value.update({u'library': None})
    elif u'draft-branch' not in value:
        value.update({u'draft-branch': None})
        value.update({u'published-branch': None})
for j in db.modulestore.structures.find({}, {"previous_version": 1}):
    available_version_list.append(j)
for j in db.modulestore.structures.find({}, {"previous_version": 1, "original_version": 1}):
    available_version_list_with_prev_original.append(j)

draft_branch_version = []
for version_dict in versions:
    draft_branch_version.append(version_dict['draft-branch'])
published_branch_version = []
for version_dict in versions:
    published_branch_version.append(version_dict['published-branch'])
library_branch_version = []
for version_dict in versions:
    library_branch_version.append(version_dict['library'])
all_required_versions = draft_branch_version + published_branch_version + library_branch_version
all_req_versions = []
for version in all_required_versions:
    if version is not None:
        all_req_versions.append(version)
#print "********** ***********all required versions ********* *****************************"
#print all_req_versions


def search_dictionaries(key, val, list_of_dictionaries):
    for element in list_of_dictionaries:
        if element[key] == val:
            return element


def mongo_version_manager():
    global versions_not_to_be_deleted
    all_versions_tree_list = []
    for each_version in all_req_versions:
        var1 = search_dictionaries('_id', each_version, available_version_list)
        i = 0
        version_tree = []
        # print var1
        if var1 is not None:
            while var1['previous_version'] is not None:
                var1 = search_dictionaries('_id', var1['previous_version'], available_version_list)
                if var1 is None:
                    break
                version_tree.append(var1)
                i += 1
            all_versions_tree_list.append(version_tree)
    print all_versions_tree_list
    #req_sub_tree = []
    a11 = []
    a22 = []
    a33 = []
    for each_tree in all_versions_tree_list:
        req_sub_tree = []
        for item in each_tree:
            req_sub_tree.append(item['_id'])
        if len(req_sub_tree) > 3:
            a11.append(req_sub_tree[:2])
            a22.append(req_sub_tree[-1])
            a33.append(req_sub_tree[2:-1])
    versions_not_to_be_deleted = [val for sub_list in a11 for val in sub_list] + a22 + all_req_versions + a11
    #print versions_not_to_be_deleted
    versions_tobe_deleted = []
    for sub_list in a33:
        for val in sub_list:
            versions_tobe_deleted.append(val)
    #print versions_tobe_deleted

    final_to_be_deleted_versions = []
    for element in versions_tobe_deleted:
        if element not in versions_not_to_be_deleted:
            final_to_be_deleted_versions.append(element)
    #print final_to_be_deleted_versions
    db.modulestore.structures.remove({'_id': {'$in': final_to_be_deleted_versions}})


mongo_version_manager()
