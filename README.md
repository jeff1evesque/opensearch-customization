# opensearch_customization

This [lambda function](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) is intended to configure an [OpenSearch cluster](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html), beyond what is natively exposed/available through cloud provisioning frameworks:

- [configure alerting](https://github.com/jeff1evesque/opensearch_customization#configure-alerting): using SNS topic
- [create mapping](https://github.com/jeff1evesque/opensearch_customization#create-mapping): define field types, such as `double`, [`date`](https://opensearch.org/docs/latest/search-plugins/sql/datatypes/#date), and more
- [initialize dashboard](https://github.com/jeff1evesque/opensearch_customization#initialize-dashboard): initializes an empty [OpenSearch Dashboard](https://opensearch.org/docs/1.1/dashboards/index/) by creating a required [Index Pattern](https://www.elastic.co/guide/en/kibana/current/index-patterns-api-create.html) if not exists
- [document deletion](https://github.com/jeff1evesque/opensearch_customization#document-deletion): specify documents within a date/time range using a `match` [query condition](https://opensearch.org/docs/latest/opensearch/rest-api/document-apis/delete-by-query/) to delete
- [helper functions](https://github.com/jeff1evesque/opensearch_customization#helper-functions): the overall codebase has defined numerous get/set/delete functions that can be invoked as desired to satisfy requirements beyond configuring alerting, or creating mapping

In general, this function can be executed ad-hoc, or as a [custom resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html) invoked by CloudFormation or Terraform. While below will emphasize on CloudFormation, Terraform variation via [`aws_cloudformation_stack`](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudformation_stack), or [custom providers](https://www.terraform.io/plugin) are left as an exercise.

## Configure Alerting

The following CloudFormation segment will configure alerting using an existing [SNS topic](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/US_SetupSNS.html):

```yaml
OpenSearchConfigurationFunction:
    Type: AWS::Lambda::Function
    Properties:
        Description: custom lambda resource configure opensearch cluster
        Code:
            S3Bucket: !Ref DeployBucket
            S3Key: !Ref S3KeyOpenSearchConfiguration
        Layers: !If
          - UseTracing
          - - !Sub '{{resolve:ssm:/${StackSuffixName}/lambda_layer/aws-xray-sdk}}'
            - !Sub '{{resolve:ssm:/${StackSuffixName}/lambda_layer/requests}}'
            - !Sub '{{resolve:ssm:/${StackSuffixName}/lambda_layer/requests_aws4auth}}'
          - - !Sub '{{resolve:ssm:/${StackSuffixName}/lambda_layer/requests}}'
            - !Sub '{{resolve:ssm:/${StackSuffixName}/lambda_layer/requests_aws4auth}}'
        FunctionName: !Ref FunctionNameOpenSearchConfiguration
        Handler: !Ref Handler
        MemorySize: !Ref MemorySize
        Role: !GetAtt OpenSearchConfigurationExecutionRole.Arn
        Runtime: !Ref Runtime
        Timeout: !Ref Timeout

OpenSearchConfiguration:
    Type: Custom::OpenSearchConfigure
    Properties:
        ServiceToken: !GetAtt OpenSearchConfigurationFunction.Arn
        Region: !Ref AWS::Region
        OpenSearchDomain: !Sub https://${OpenSearch.Outputs.NestedOpenSearchDomainEndpoint}
        OpenSearchIndex: !Ref OpenSearchIndex
        SnsAlertName: !Ref OpenSearchIndex
        SnsTopicArn: !GetAtt OpenSearchConfigurationNotification.Outputs.NestedSnsTopicArn
        SnsRoleArn: !GetAtt OpenSearchConfigurationRole.Arn
        MonitorName: OverallFailures
        MonitorInterval: !Ref OpenSearchMonitorInterval
        MonitorUnit: !Ref OpenSearchMonitorUnit
        MonitorCondition: !Ref OpenSearchMonitorCondition
        MonitorRangeField: !Ref OpenSearchMonitorRangeField
        MonitorRangeFrom: now-1h
        MonitorRangeTo: now
        MonitorQueryTerms: !Sub
          - '{
              "${OpenSearchMonitorTerm}": ["${OpenSearchMonitorTermValue}"],
              "boost": 1.0
            }'
          - OpenSearchMonitorTerm: !Ref OpenSearchMonitorTerm
            OpenSearchMonitorTermValue: !Ref OpenSearchMonitorTermValue
        MonitorTriggerSubject: !Sub ${OpenSearchIndex} detected ${OpenSearchMonitorTermValue}
        MonitorTriggerMessage: !Sub |
            specified ${OpenSearchMonitorTerm} detected ${OpenSearchMonitorTermValue}
            satisfying ${OpenSearchMonitorCondition} within ${OpenSearchMonitorInterval} ${OpenSearchMonitorUnit}
    DependsOn: [OpenSearch, OpenSearchConfigurationFunction]
```

## Create Mapping

An OpenSearch cluster can be defined via CloudFormation using the [`AWS::OpenSearchService::Domain`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opensearchservice-domain.html). However, there are no attributes that allow index fields to be specified. This can be problematic, since all fields will default as a `string` type, preventing the ability to create [time-based visualizations](https://www.elastic.co/guide/en/kibana/current/tsvb.html) within [OpenSearch Dashboards](https://opensearch.org/docs/latest/dashboards/index/).

The following example shows how to define a [`date`](https://opensearch.org/docs/latest/search-plugins/sql/datatypes/#date) type field, thus opening the ability to configure time-based visualizations.

```yaml
OpenSearchConfigurationFunction:
    Type: AWS::Lambda::Function
    Properties:
        Description: custom lambda resource configure opensearch cluster
        Code:
            S3Bucket: !Ref DeployBucket
            S3Key: !Ref S3KeyOpenSearchConfiguration
        Layers: !If
          - UseTracing
          - - !Sub '{{resolve:ssm:/${StackSuffixName}/lambda_layer/aws-xray-sdk}}'
            - !Sub '{{resolve:ssm:/${StackSuffixName}/lambda_layer/requests}}'
            - !Sub '{{resolve:ssm:/${StackSuffixName}/lambda_layer/requests_aws4auth}}'
          - - !Sub '{{resolve:ssm:/${StackSuffixName}/lambda_layer/requests}}'
            - !Sub '{{resolve:ssm:/${StackSuffixName}/lambda_layer/requests_aws4auth}}'
        FunctionName: !Ref FunctionNameOpenSearchConfiguration
        Handler: !Ref Handler
        MemorySize: !Ref MemorySize
        Role: !GetAtt OpenSearchConfigurationExecutionRole.Arn
        Runtime: !Ref Runtime
        Timeout: !Ref Timeout

OpenSearchConfiguration:
    Type: Custom::OpenSearchConfigure
    Properties:
        ServiceToken: !GetAtt OpenSearchConfigurationFunction.Arn
        Region: !Ref AWS::Region
        OpenSearchDomain: !Sub https://${OpenSearch.Outputs.NestedOpenSearchDomainEndpoint}
        OpenSearchIndex: !Ref OpenSearchIndex
        Mappings: !Sub
          - '{
                "properties": {
                    "${OpenSearchTimeStampField}": {
                        "type": "date",
                        "format": "${OpenSearchTimeStampFieldFormat}"
                    }, {
                    "${OpenSearchPriceField}": {
                        "type": "double"
                    }, {
                    "${OpenSearchDateField}" : {
                        "type": "date",
                        "format": "${OpenSearchDateFieldFormat}"
                    }
                }
            }'
          - OpenSearchTimeStampField: !Ref OpenSearchTimeStampField
            OpenSearchTimeStampFieldFormat: !Ref OpenSearchTimeStampFieldFormat
            OpenSearchPriceField: !Ref OpenSearchPriceField
            OpenSearchDateField: !Ref OpenSearchDateField
            OpenSearchDateFieldFormat: !Ref OpenSearchDateFieldFormat
    DependsOn: [OpenSearch, OpenSearchConfigurationFunction]
```

## Initialize Dashboard

While it's possible to fully automate the creation of visualizations, and likely subsequent attachment to desired dashboard(s), this codebase prefers a more minimalist approach. Specifically, any small change in a visualization can easily become many magnitudes complicated for automation. Rather, this codebase setups up a default Index Pattern if one does not exist for a specified Index. Using the Index Pattern, an OpenSearch Dashboard is then created. The provided [`lambda.py`](https://github.com/jeff1evesque/opensearch_customization/blob/master/lambda.py) creates an empty dashboard by default:

```python
if initialize_dashboard:
    #
    # create index pattern: used by dashboard
    #
    index_id = index.replace('*', '').rstrip('-').rstrip('_')
    r = check_index_pattern(endpoint, awsauth, index_id=index_id, title=index)

    if r != index_id:
        set_index_pattern(endpoint, awsauth, index_id=index_id, title=index)

    #
    # create dashboard: if index and index pattern exists
    #
    if (
        check_index(endpoint, awsauth, index) and
        check_index_pattern(endpoint, awsauth, index_id=index_id, title=index) and
        not check_dashboard(endpoint, awsauth, index)
    ):
        set_dashboard(endpoint, awsauth, index)
```

To turn-off this functionality, provide the `InitializeDashboard` parameter:

```yaml
OpenSearchConfiguration:
    Type: Custom::OpenSearchConfigure
    Properties:
        ServiceToken: !GetAtt OpenSearchConfigurationFunction.Arn
        Region: !Ref AWS::Region
        OpenSearchDomain: !Sub https://${OpenSearch.Outputs.NestedOpenSearchDomainEndpoint}
        OpenSearchIndex: !Ref OpenSearchIndex
        InitalizeDashboard: false
    DependsOn: [OpenSearch, OpenSearchConfigurationFunction]
```

## Document Deletion

It's possible to perform index rotation for an OpenSearch Index. However, this segment introduces the ability to delete documents within a specified index, satisfying a `match` [query condition](https://opensearch.org/docs/latest/opensearch/rest-api/document-apis/delete-by-query/). This can be particularly useful when only the latest N days of documents are desired.  Consider the case of a producer sending data to a [Kinesis Stream](https://docs.aws.amazon.com/streams/latest/dev/introduction.html). This data stream could hypothetically be configured with a [Kinesis Firehose](https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html) to buffer data into a datalake for long term storage.  However, the same data stream could be attached with an [event source mapping](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/integrations.html#integrations-kinesis) to an OpenSearch index. This allows the ability to keep the most recent data for visualization using OpenSearch Dashboard, while retaining the ability to perform historical analysis from the tangential datalake.

The following example deletes all documents from a specified `OpenSearchIndex`, where a `message.utc` field from the index is older than or equal to 5 days from now:

```yaml
OpenSearchConfiguration:
    Type: Custom::OpenSearchConfigure
    Properties:
        ServiceToken: !GetAtt OpenSearchConfigurationFunction.Arn
        Region: !Ref AWS::Region
        OpenSearchDomain: !Sub https://${OpenSearch.Outputs.NestedOpenSearchDomainEndpoint}
        OpenSearchIndex: !Ref OpenSearchIndex
        DocumentDeleteRange: !Sub
          - '{
              "${OpenSearchMonitorTerm}": ["${OpenSearchMonitorTermValue}"],
              "boost": 1.0
            }'
          - OpenSearchMonitorTerm: !Ref OpenSearchMonitorTerm
            OpenSearchMonitorTermValue: !Ref OpenSearchMonitorTermValue
    DependsOn: [OpenSearch, OpenSearchConfigurationFunction]
```

**Note:** the above requires `message.utc` to be a [`date`](https://opensearch.org/docs/latest/search-plugins/sql/datatypes/#date) field.

The following CloudWatch [event rule](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/WhatIsCloudWatchEvents.html) triggers `OpenSearchConfigurationFunction`
using a [cron expression](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html#CronExpressions):

```yaml
OpenSearchDeleteDocumentRule:
    Type: AWS::Events::Rule
    Properties:
        Name: !Sub ${FunctionNameOpenSearchConfiguration}DeleteIndexDocuments
        Description: !Sub |
            trigger ${FunctionNameOpenSearchConfiguration} to delete index
            documents older than or equal to 30 days from now
        ScheduleExpression: cron(0 4 * * ? *)
        State: !Ref EnableEventRules
        Targets:
          - Id: OpenSearchDeleteDocumentRule
            Arn: !GetAtt OpenSearchConfigurationFunction.Arn
            Input: !Sub
              - '{
                    "RequestType": "Create",
                    "ResourceProperties": {
                        "OpenSearchDomain": "https://${OpenSearchDomain}",
                        "OpenSearchIndex": "${OpenSearchIndex}",
                        "DocumentDeleteRange": {
                            "message.utc": { "lte": "now-30d" }
                        }
                    }
                }'
              - OpenSearchDomain: !Sub OpenSearch.Outputs.NestedOpenSearchDomainEndpoint
                OpenSearchIndex: !Ref OpenSearchIndex

            RetryPolicy:
                MaximumEventAgeInSeconds: !Ref MaximumEventAgeInSeconds
                MaximumRetryAttempts: !Ref MaximumRetryAttempts
    DependsOn: [OpenSearchConfigurationFunction, OpenSearchConfiguration]

PermissionForEventsToInvokeLambda:
     Type: AWS::Lambda::Permission
     Properties:
         FunctionName: !Ref OpenSearchConfigurationFunction
         Action: lambda:InvokeFunction
         Principal: events.amazonaws.com
         SourceArn: !GetAtt OpenSearchDeleteDocumentRule.Arn
```

## Helper Functions

Please review functions defined in the following files, and invoke them as desired in [`lambda.py`](https://github.com/jeff1evesque/opensearch_customization/blob/master/lambda.py):

- [`get_configuration.py`](https://github.com/jeff1evesque/opensearch_customization/blob/master/get_configuration.py)
- [`set_configuration.py`](https://github.com/jeff1evesque/opensearch_customization/blob/master/set_configuration.py)
- [`delete_configuration.py`](https://github.com/jeff1evesque/opensearch_customization/blob/master/delete_configuration.py)

## Bug Reporting

Please open [an issue](https://github.com/jeff1evesque/opensearch_customization/issues/new) if a particular bug is found, or a feature is desired.
