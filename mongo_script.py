from pymongo import MongoClient

client = MongoClient()
# Use Mongo Db URI Format MongoClient('mongodb://localhost:27017/'), empty for localhost

db = client.edxapp


# accessing the edxapp db


def main():
    # Initializing the empty lists
    required_version_list = []
    # versions_not_to_be_deleted = 0
    available_version_list = []
    # available_version_list_with_prev_original = []
    for value in db.modulestore.active_versions.find({}, {"versions.draft-branch": 1, "versions.published-branch": 1,
                                                          "versions.library": 1, }):
        """
        This will extract all the draft,published,library versions of all courses from modulestore.active_versions collection and append
        to list. The example below shows only the first element in that list.
        Example:
             [{u'_id': ObjectId('595d2a6a06aec009c3949d42'), u'versions': {u'draft-branch': ObjectId('595d56cb06aec009b0949d45'), u'published-branch': ObjectId('595d56cb06aec009b0949d44')}}]
        """

        required_version_list.append(value)
    versions = [d['versions'] for d in required_version_list]
    # Extracting the child documents of u'versions' and storing into versions list
    for value in versions:
        """
        we are adding default value for library,draft-branch,published-branch, if doesn't exist in the versions list
        """

        if u'library' not in value:
            value.update({u'library': None})
        elif u'draft-branch' not in value:
            value.update({u'draft-branch': None})
            value.update({u'published-branch': None})
    for previous_version in db.modulestore.structures.find({}, {"previous_version": 1}):
        
        """ 
        
        This will give the list of Dictionary's with _id and previous_version 
        
        """
        
        available_version_list.append(previous_version)
    available_version_list_with_prev_original = []

    available_version_list_with_id_val = []
    for previous_and_original_version in db.modulestore.structures.find({},
                                                                        {"previous_version": 1, "original_version": 1}):
        """

        Extracting the list of Dictionary's with _id ,previous_version and original_version

        """
        available_version_list_with_prev_original.append(previous_and_original_version)
        # print j

    for _id in db.modulestore.structures.find({}, {"_id": 1}):
        available_version_list_with_id_val.append(_id)

        # print available_version_list_with_id_val
    list_of_avail_id = []
    for d in available_version_list_with_id_val:
        if '_id' in d:
            list_of_avail_id.append(d['_id'])
    draft_branch_version = []
    for version_dict in versions:
        # Extracting all draft branch versions
        draft_branch_version.append(version_dict['draft-branch'])
    published_branch_version = []
    for version_dict in versions:
        # Extracting all published-branch versions
        published_branch_version.append(version_dict['published-branch'])
    library_branch_version = []
    for version_dict in versions:
        # Extracting all library versions
        library_branch_version.append(version_dict['library'])

    # Adding all the available required versions into one single list
    all_required_versions = draft_branch_version + published_branch_version + library_branch_version
    all_req_versions = []
    for version in all_required_versions:
        if version is not None:
            """

            removing the values that says None from the all_req_versions

            """

            all_req_versions.append(version)

    # print all_req_versions
    #mongo_version_linker(available_version_list_with_prev_original, list_of_avail_id)
    mongo_version_manager(all_req_versions, available_version_list,2)
    mongo_version_linker(available_version_list_with_prev_original, list_of_avail_id)

def search_dictionaries(key, val, list_of_dictionaries):
    """ 

    This will take key ,value, list of dictionary's as arguments and returns the dictionary
        that contains them.

    """

    for element in list_of_dictionaries:
        if element[key] == val:
            return element


def mongo_version_manager(all_req_versions, available_version_list, req_start_node=2):
    # versions_not_to_be_deleted = 0
    all_versions_tree_list = []
    for each_version in all_req_versions:
        var1 = search_dictionaries('_id', each_version, available_version_list)
        i = 0
        version_tree = []
        #print var1
        if var1 is not None:
            while var1['previous_version'] is not None:
                var1 = search_dictionaries('_id', var1['previous_version'], available_version_list)
                if var1 is None:
                    break
                version_tree.append(var1)
                i += 1
            all_versions_tree_list.append(version_tree)
    print all_versions_tree_list
    # req_sub_tree = []
    head_nodes = []
    middle_nodes = []
    tail_nodes = []
    for each_tree in all_versions_tree_list:
        req_sub_tree = []
        for item in each_tree:
            req_sub_tree.append(item['_id'])
        if len(req_sub_tree) > req_start_node:
            # This will extract the first n version id's from the version_tree
            head_nodes.append(req_sub_tree[:2])
            # This will extract the last n version id's from the version_tree
            middle_nodes.append(req_sub_tree[-1])
            # This will extract the mid range of n t0 n+1 version id's from the version_tree
            tail_nodes.append(req_sub_tree[2:-1])
    versions_not_to_be_deleted = [val for sub_list in head_nodes for val in
                                  sub_list] + middle_nodes + all_req_versions + head_nodes
    #print versions_not_to_be_deleted
    versions_not_to_be_deleted_2 = []
    for each in versions_not_to_be_deleted:
        # removing duplicated in versions_not_to_be_deleted list
        if each not in versions_not_to_be_deleted_2:
            versions_not_to_be_deleted_2.append(each)

    versions_tobe_deleted = []
    for sub_list in tail_nodes:
        for val in sub_list:
            versions_tobe_deleted.append(val)
    # print versions_tobe_deleted

    final_to_be_deleted_versions = []
    for element in versions_tobe_deleted:
        if element not in versions_not_to_be_deleted_2:
            final_to_be_deleted_versions.append(element)
    # print final_to_be_deleted_versions
    # this will delete all the extra or unnecessary versions
    db.modulestore.structures.remove({'_id': {'$in': final_to_be_deleted_versions}})


def mongo_version_linker(available_version_list_with_prev_original, list_of_avail_id):
    for each in available_version_list_with_prev_original:
        if each["previous_version"] is None:
            print "Hi None"
        elif each["previous_version"] not in list_of_avail_id and each["previous_version"] is not None:
            to_be_linked_version_id = []
            # b = []
            original_version_id = []
            to_be_linked_version_id.append(each['_id'])
            # b.append(each['previous_version'])
            original_version_id.append(each['original_version'])
            print to_be_linked_version_id
            print original_version_id
            # we are appending into the array and linking it, Since $in in mongo query is expecting list
            db.modulestore.structures.update({'_id': {'$in': to_be_linked_version_id}},{'$set': {"previous_version": original_version_id[0]}})
        else:
            print "Nothing to delete"


if __name__ == '__main__':
    main()
