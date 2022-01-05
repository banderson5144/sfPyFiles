# Python SOAP Client
from zeep import Client
import base64
import os

# Path to Partner WSDL (https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/obtaining_the_partner_wsdl_file.htm)
client = Client('./partner_wsdl.xml')

# Simple login, only for testing purposes
# login_result = client.service.login('username@domain.com', 'PasswordToken')
# print(login_result.sandbox)

# Set the Session Id by whatever means
sessionId = '00DXXXXXXXXXXXXXXXXXXX'

# Set the Server URL by whatever means
serverUrl = 'https://{yourMyDomain}.my.salesforce.com/services/Soap/u/52.0'

client._default_soapheaders ={'SessionHeader':{"sessionId" : sessionId}} 

# Create Salesforce Service from WSDL
clientService = client.create_service( '{urn:partner.soap.sforce.com}SoapBinding', serverUrl)

#Query the ContentVersion Ids first
query_result = clientService.query("Select Id FROM ContentVersion")

# print(query_result.body.result.records[0]['Id'])

# Create Array of ContentVersion Ids
cvIds = []

# Loop over query results to populate ContentVersion Ids
for i in query_result.body.result.records:
    cvIds.append(i.Id)

# Perform retrieve() API call in order get back multiple Files at once
retrieve_result = clientService.retrieve('Title,FileExtension,VersionData','ContentVersion',cvIds)

# Since the Partner WSDL uses a generic sObject type
# the Zeep SOAP client cannot parse the SOAP Response to strongly typed attributes
# In order to access the values, it is by position in an array
# OwnerId[0]
# Title[1]
# VersionData[2]

for j in retrieve_result.body.result:
    testDict = {} # Store the results in a dict so we can access easily instead of by position
    for k in j._value_1:
        testDict[k.tag] = k.text
    file_content=base64.b64decode(testDict['{urn:sobject.partner.soap.sforce.com}VersionData'])
    fileName = testDict['{urn:sobject.partner.soap.sforce.com}Title']
    fileExt = testDict['{urn:sobject.partner.soap.sforce.com}FileExtension']
    if fileExt is not None and fileExt != '':
        try:
            wholeName = 'files/' + fileName + '.' + fileExt
            os.makedirs(os.path.dirname(wholeName), exist_ok=True)
            with open(wholeName,"wb") as f:
                f.write(file_content)
        except Exception as e:
            print(str(e))