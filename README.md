# splunk_search_history_kvstore
A loving place to store the trials and tribulations for backing up, searching and restoring Splunk User Search History that's configured to be stored within the KV Store.


# Backup KV Store - pick your flavor of backing up (rest api, splunk cli, splunk app like "KV Store Tools Redux")
## To backup just Search History
```
/opt/splunk/bin/splunk backup kvstore -archiveName `hostname`-SearchHistory_`date +%s`.tar.gz -appName system -collectionName SearchHistory
```

## To backup entire KV Store (most likely a good idea)
```
/opt/splunk/bin/splunk backup kvstore -archiveName `hostname`-SearchHistory_`date +%s`.tar.gz
```


# Restore archive
## Change directory to location of archive backup
```
cd /opt/splunk/var/lib/splunk/kvstorebackup
```
## Locate archive to restore
```
ls -lst
```
## List archive files (optional, but helpful to see what's inside and how archive will extract to ensure you don't overwrite expected files)
```
 tar ztvf SearchHistory_1731206815.tar.gz
-rw------- splunk/splunk 197500 2024-11-10 02:46 system/SearchHistory/SearchHistory0.json
```
## Extract archive or selected files
```
tar zxvf SearchHistory_1731206815.tar.gz
system/SearchHistory/SearchHistory0.json
```


# Parse archive to prep to restore
## Change directory to where archive was extracted
```
cd /opt/splunk/var/lib/splunk/kvstorebackup/system/SearchHistory
```
## Create/copy splunk_parse_search_history_kvstore_backup_per_user.py script to parse archives in directory to /tmp (or someplace else) and run on archive(s)
```
./splunk_parse_search_history_kvstore_backup_per_user.py /opt/splunk/var/lib/splunk/kvstorebackup/system/SearchHistory/SearchHistory0.json
```
## List files created
```
ls -ls SearchHistory0*
 96 -rw-rw-r-- 1 splunk splunk  95858 Nov 14 23:12 SearchHistory0_admin.json
108 -rw-rw-r-- 1 splunk splunk 108106 Nov 14 23:12 SearchHistory0_nobody.json
```


# Restore archives needed
## NOTE:  To prevent SearchHistory leaking between users, you MUST restore to the corresponding user context
## Either loop/iterate through restored files or do them one at a time calling the corresponding REST API
```
curl -k -u admin https://localhost:8089/servicesNS/<user>/system/storage/collections/data/SearchHistory/batch_save -H "Content-Type: application/json" -d @SearchHistory0_<user>.json
```


## Validate that the SearchHistory KV Store was restored properly for the user through calling the REST API and/or also logging into Splunk as the user to test with, navigate to "Search & Reporting" and selecting "Search History"
```
curl -k -u admin https://localhost:8089/servicesNS/<user>/system/storage/collections/data/SearchHistory
```



## NOTE: There are default limits in KV Store that you need to account for if you're files are large!   If you run into problems, review your splunkd.log and/or the KV Store dashboards within the MC (Search --> KV Store)
```
# /opt/splunk/bin/splunk btool limits list --debug kvstore
/opt/splunk/etc/system/default/limits.conf           [kvstore]
/opt/splunk/etc/system/default/limits.conf           max_accelerations_per_collection = 10
/opt/splunk/etc/system/default/limits.conf           max_documents_per_batch_save = 50000
/opt/splunk/etc/system/default/limits.conf           max_fields_per_acceleration = 10
/opt/splunk/etc/system/default/limits.conf           max_mem_usage_mb = 200
/opt/splunk/etc/system/default/limits.conf           max_queries_per_batch = 1000
/opt/splunk/etc/system/default/limits.conf           max_rows_in_memory_per_dump = 200
/opt/splunk/etc/system/default/limits.conf           max_rows_per_query = 50000
/opt/splunk/etc/system/default/limits.conf           max_size_per_batch_result_mb = 100
/opt/splunk/etc/system/default/limits.conf           max_size_per_batch_save_mb = 50
/opt/splunk/etc/system/default/limits.conf           max_size_per_result_mb = 50
/opt/splunk/etc/system/default/limits.conf           max_threads_per_outputlookup = 1
```


# Troubleshooting
## To delete the entire SearchHistory KV Store (because maybe you inadvertently restored everything to an incorrect user, testing, or due to other shenanigans)
```
/opt/splunk/bin/splunk clean kvstore -app system -collection SearchHistory
```

## To delete a user specific context in the SearchHistory KV Store (because see above)
```
curl -k -u admin:splunk@dmin https://localhost:8089/servicesNS/<user>/system/storage/collections/data/SearchHistory -X DELETE
```
# Additional Notes
It was noted that restoring for a user that has not logged in yet may report messages similar to "Action forbidden".  To remedy this, you might be able to create a local user and then restore again.  
