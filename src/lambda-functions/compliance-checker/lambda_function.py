import json
import boto3
import time

_DEBUG_ON = True

def lambda_handler(event, context):
    compliance_check = {
        "compliant": True,
        "input": True,
        "output_encryption": True
    }
    
    job = json.loads(json.dumps(event))
    _debug_print("event json is: ")
    _debug_print(json.dumps(event))
    
    if (job["source"] == 'aws.mediaconvert' and job["detail"] and job["detail"]["eventName"] == 'CreateJob'):
        inputs = job["detail"]["requestParameters"]["settings"]["inputs"]
        if (inputs):
            for ain in inputs:
                if not ( ain["fileInput"].startswith("s3://") or ain["fileInput"].startswith("s3ssl://") ):
                    compliance_check["compliant"] = False;
                    compliance_check["input"] = False;
                    _debug_print ("noncompliant input ain.fileinput="+ain["fileInput"])
                    break;
                else:
                    _debug_print ("compliant input ain.fileinput="+ain["fileInput"])
                    
        outgroups = job["detail"]["requestParameters"]["settings"]["outputGroups"]
        if (compliance_check["compliant"] and outgroups):
            for og in outgroups:
                ogencrytion_setting = True
                _debug_print("Checking outputGroup name: " + og["name"])
                ogsetting = og["outputGroupSettings"]
                if ogsetting:
                    _debug_print("process outputGroupSettings type = " + ogsetting["type"])
                    if ogsetting["type"] == 'CMAF_GROUP_SETTINGS':
                        ogencrytion_setting=compliance_check_encryption(ogsetting["cmafGroupSettings"])
                    elif ogsetting["type"] == 'FILE_GROUP_SETTINGS':
                        ogencrytion_setting=compliance_check_encryption(ogsetting["fileGroupSettings"])
                    elif ogsetting["type"] == 'HLS_GROUP_SETTINGS':
                        ogencrytion_setting=compliance_check_encryption(ogsetting["hlsGroupSettings"])
                    elif ogsetting["type"] == 'DASH_ISO_GROUP_SETTINGS':
                        ogencrytion_setting=compliance_check_encryption(ogsetting["dashIsoGroupSettings"])
                    elif ogsetting["type"] == 'MS_SMOOTH_GROUP_SETTINGS':
                        ogencrytion_setting=compliance_check_encryption(ogsetting["msSmoothGroupSettings"])
                else:
                    _debug_print (og["name"] + "'s outputGroupSettings is empty, you should not see this message for MediaConvert Job json!")
                if not ogencrytion_setting:
                    compliance_check["compliant"] = False;
                    compliance_check["output_encryption"] = False;
                    break;    
        
        print_compliance_status(compliance_check);
        
        # process log with default lambda function log group
        logs = boto3.client('logs')
        
        # You can even do this with watchtower! Use this instead, client = watchtower_handler.cwl_client
        logs.meta.events.register_first('before-sign.cloudwatch-logs.PutLogEvents', add_emf_header)

        LOG_GROUP='/aws/lambda/emc_job_compliance_check'
        LOG_STREAM='{}-{}'.format(time.strftime('%Y-%m-%d'),'logstream_compliance_check')
        
        try:
           logs.create_log_group(logGroupName=LOG_GROUP)
        except logs.exceptions.ResourceAlreadyExistsException:
           pass
        
        try:
           logs.create_log_stream(logGroupName=LOG_GROUP, logStreamName=LOG_STREAM)
        except logs.exceptions.ResourceAlreadyExistsException:
           pass
        
        response = logs.describe_log_streams(
           logGroupName=LOG_GROUP,
           logStreamNamePrefix=LOG_STREAM
        )
        _debug_print("describe_log_streams output: ")
        _debug_print(response)

        jobId=''
        responseElements = job["detail"]["responseElements"]
        if responseElements:
            respJob = responseElements["job"]
            if respJob:
                jobId = respJob["id"]
                
        emf = {
          "_aws": {
            "Timestamp": int(round(time.time() * 1000)),
            "CloudWatchMetrics": [
              {
                "Namespace": 'mediaconvert-compliant-metrics',
                "Dimensions": [['account']],
                "Metrics": [
                  {
                    "Name": "noncompliant_count",
                    "Unit": "Count"
                  }
                ]
              }
            ]
          },
          "account": job["account"],
          "region": job["detail"]["awsRegion"],
          "id": jobId,
          "noncompliant_count": 1
        }
        event_log = {'logGroupName': LOG_GROUP,
           'logStreamName': LOG_STREAM,
           'logEvents': [
               {
                   'timestamp': int(round(time.time() * 1000)),
                   'message': json.dumps(emf)
               }
           ],
        }
        
        #emmsg = {
        #    'message': '[Embedded Metric]',
        #    
        #}
        
        if 'uploadSequenceToken' in response['logStreams'][0]:
           event_log.update({'sequenceToken': response['logStreams'][0] ['uploadSequenceToken']})
        
        response = logs.put_log_events(**event_log)
        _debug_print(response)
        
        return {
            'statusCode': 200,
            'body': "Compliant:" + str(compliance_check["compliant"])
        }
    else:
        return {
            'statusCode': 500,
            'body': 'Invalid mediaconvert job json in lambda_handler event'
        }
        
def print_compliance_status(check):
    _debug_print("compliance_check.compliant = " + str(check["compliant"]))

def compliance_check_encryption(outputGroupSettings):
    if outputGroupSettings:
        dstSettings = outputGroupSettings.get("destinationSettings")
        if dstSettings:
            encryption = dstSettings["s3Settings"]["encryption"]
            if encryption:
                _debug_print("encryptionType="+encryption["encryptionType"])
                if encryption["encryptionType"] != 'SERVER_SIDE_ENCRYPTION_KMS':
                    _debug_print("encryptionType is " + encryption["encryptionType"] + ", expect SERVER_SIDE_ENCRYPTION_KMS!")
                    return False
            else:
                return False
        
            accessControl = dstSettings["s3Settings"]["accessControl"]
            if accessControl:
                if accessControl["cannedAcl"] == 'PUBLIC_READ':
                    _debug_print("Output accessControl should not be " + accessControl["cannedAcl"] + "!")
                    return False
            else:
                return False
            return True
        else:
            return False
    else:
        _debug_print("OutputGroupSettings are empty! The MediaConvert Job Json is invalid!")
        return False
        
def add_emf_header(request, **kwargs):
    request.headers.add_header('x-amzn-logs-format', 'json/emf')
    #_debug_print(request.headers) # Remove this after testing of course.
    
def _debug_print(message):
    if _DEBUG_ON:
        print(message)