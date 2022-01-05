This is a python code sample showing how to retrieve binary files from Salesforce in Bulk.

Currently when you issue a `query` API call and the SOQL statement contains a Base64 field (i.e. `VersionData` on `ContentVersion`), you can only retrieve one record at a time. This means if you want to retrieve 20 files from Salesfeorce, you will need 20 API calls.

However, Salesforce does have another API call to get around this limitation. The [`retrieve`](https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_calls_retrieve.htm) API call allows you to retrieve multiple records with a Base64 field included.

The algorithm for using these API calls together would be to `query` all other fields first and then grabbing the set of Ids from that operation and then issuing a `retrieve` API call that gets the Base64 field for multiple records. So in this case, you would only be consuming 2 API calls. One for `query` and one for `retrieve`