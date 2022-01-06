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

# Assign Session Id to the SOAP Header Envelop, also added batch size to query from Salesforce
client._default_soapheaders ={'SessionHeader':{"sessionId" : sessionId},'QueryOptions':{"batchSize" : 200}} 

# Create Salesforce Service from WSDL
clientService = client.create_service( '{urn:partner.soap.sforce.com}SoapBinding', serverUrl)

#Initial Query from Salesforce
print('Initial Query')
query_result = clientService.query("Select Id,ContentSize FROM ContentVersion ORDER BY ContentSize ASC")

currRecSet = query_result.body.result.records
currQryDone = query_result.body.result.done
currQryLoc = query_result.body.result.queryLocator

cvIds = []
cvSize = 0

# print(query_result.body.result.queryLocator)

def retrieveFiles():
    global cvIds
    global cvSize
    print('Downloading files from SF')
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

    cvIds = []
    cvSize = 0

    if(len(currRecSet)>0):
        loopThroughSet()
    elif(currQryDone is False):
        sfQryMore()

def sfQryMore():
    print('Query more Ids')
    global query_result
    global currQryLoc
    global currQryDone
    global currRecSet
    query_result = clientService.queryMore(currQryLoc)
    currRecSet = query_result.body.result.records
    currQryDone = query_result.body.result.done
    currQryLoc = query_result.body.result.queryLocator
    loopThroughSet()

def loopThroughSet():
    while len(currRecSet)>0:
        global cvIds
        global cvSize

        myDict = {}

        # Store the results in a dict so we can access easily instead of by position
        for k in currRecSet[0]._value_1:
            myDict[k.tag] = k.text

        cvIds.append(currRecSet[0].Id)
        cvSize+=int(myDict['{urn:sobject.partner.soap.sforce.com}ContentSize'])

        del currRecSet[0]

        #Pull down files from Salesforce if we hit 200 records or 500MB of files
        if(len(cvIds)==200 or cvSize>=500000000):
            retrieveFiles()
            #If we have not hit the limits above but we have no records to loop over
            #And the is still another query to run, pull them down from Salesforce
        elif(len(currRecSet)==0 and currQryDone is False):
            sfQryMore()
            #If we did not hit either condition above, we are at the end and need
            #and need to pull down the last set of files
        elif len(currRecSet)==0:
            retrieveFiles()

loopThroughSet()