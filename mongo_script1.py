
from pymongo import MongoClient
from bson import ObjectId
client = MongoClient()

db = client.edxapp

collection = db.modulestore.active_versions
required_version_list=[]
versions_nottobe_deleted = 0
available_version_list = []
available_version_listwith_prev_original = []
for value in collection.find({ }, { "versions.draft-branch": 1,"versions.published-branch": 1,"versions.library": 1,}):
    required_version_list.append(value)
versions = [d['versions'] for d in required_version_list]
for value in versions:
    if u'library' not in value:
        value.update({u'library': None})
    elif u'draft-branch' not in value:
        value.update({u'draft-branch':None})
        value.update({u'published-branch':None})
for j in db.modulestore.structures.find({ },{"previous_version":1} ):
    available_version_list.append(j)
for j in db.modulestore.structures.find({ },{"previous_version":1,"original_version":1} ):
    available_version_listwith_prev_original.append(j)

draft_branch_version = [version_dict['draft-branch'] for version_dict in versions]
published_branch_version = [version_dict['published-branch'] for version_dict in versions]
library_branch_version = [version_dict['library'] for version_dict in versions]
all_required_versions = draft_branch_version+published_branch_version+library_branch_version
all_req_versions = [version for version in all_required_versions if version != None ]
print "********** ***********all required versions ********* *****************************"
print all_req_versions

def search_dictionaries(key, value, list_of_dictionaries):
    for element in list_of_dictionaries:
        if element[key] == value:
            return element



def mongo_version_manager():
    all_versions_to_be_deleted = []
    global versions_nottobe_deleted
    all_versions_nottobe_deleted = []
    a1 = []
    allversionstree_list = []
    for verions in all_req_versions:
        var1  = search_dictionaries('_id',verions,available_version_list)
        i = 0
        version_tree = []
        #print var1
        if var1 != None:
            while  var1['previous_version'] != None:
                var1 = search_dictionaries('_id',var1['previous_version'],available_version_list)
                if var1 == None:
                   break
                version_tree.append(var1)
                i = i+1
            allversionstree_list.append(version_tree) 
    print allversionstree_list   
    req_sub_tree = []
    del_sub_tree = []
    a11 = []
    a22 = []
    a33 = []
    for each_tree in allversionstree_list:
        for item in each_tree:
            req_sub_tree.append(item['_id'])
        if len(req_sub_tree) > 3:
            a11.append(req_sub_tree[:2])
            a22.append(req_sub_tree[-1])
            a33.append(req_sub_tree[2:-1])
    versions_nottobe_deleted = [val for sublist in a11 for val in sublist] + a22 + all_req_versions 
    print versions_nottobe_deleted  
    versions_tobe_deleted = [val for sublist in a33 for val in sublist]
    print versions_tobe_deleted
    
    final_tobe_deleted_versions = [element for element in versions_tobe_deleted if element not in versions_nottobe_deleted]
    print final_tobe_deleted_versions
    db.modulestore.structures.remove({'_id':{'$in':final_tobe_deleted_versions}})
         
a = mongo_version_manager()
