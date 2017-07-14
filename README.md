# Mongotrim_openedx

This script is used to trim the mongodb size in OpenEdx




# Pseudo Code: 

Get all active versions 

Get all structures 
 
Generate list of versions that should not be deleted (targetA):  
  o incorporating draft-branch, published-branch & library versions from active versions 
 
Iterate all items in targetA & build a “tree” of previous nodes (from structures) for each item in targetA 
 
Generate list of versions that should be deleted (targetB) 
  o Split & filter each trees to find middle nodes 
  o “middle nodes” are those calculated as between the active version and original version in a “tree” that accounts for the user-specified retention policy (ie: user wants to keep last x versions) 
 
Delete all items in targetB 
 
find all items with disconnected from its original version and relink it.  
# TODO 

consider deleting the data in modulestore_versions for courses that are deleted/not available in modulestore_active_versions.

consider deleting Chunks/files in mongo 
