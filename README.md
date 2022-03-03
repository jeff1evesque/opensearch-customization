# opensearch_customization

This [lambda function](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) is intended to configure an [OpenSearch cluster](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html), beyond what is natively exposed/available through cloud provisioning frameworks:

- [configure alerting](https://github.com/jeff1evesque/opensearch_customization#configure-alerting): using SNS topic
- [create mapping](https://github.com/jeff1evesque/opensearch_customization#create-mapping): define field types, such as `double`, [`datetime`](https://opensearch.org/docs/latest/search-plugins/sql/datatypes/#datetime), and more
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
    DependsOn: [OpenSearch, OpenSearchConfigurationNotification]
```

## Create Mapping

An OpenSearch cluster can be defined via CloudFormation using the [`AWS::OpenSearchService::Domain`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opensearchservice-domain.html). However, there are no attributes that allow index fields to be specified. This can be problematic, since all fields will default as a `string` type, preventing the ability to create [time-based visualizations](https://www.elastic.co/guide/en/kibana/current/tsvb.html) within [OpenSearch Dashboards](https://opensearch.org/docs/latest/dashboards/index/).

The following example shows how to define a [`datetime`](https://opensearch.org/docs/latest/search-plugins/sql/datatypes/#datetime) type field, thus opening the ability to configure time-based visualizations.

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
        Mappings: !Sub |
            {
                "properties": {
                    "${OpenSearchTimeStampField}": {
                        "type": "datetime",
                        "format": "${OpenSearchTimeStampFieldFormat}"
                    }, {
                    "${OpenSearchPriceField}": {
                        "type": "double"
                    }
                }
            }
    DependsOn: [OpenSearch, OpenSearchConfigurationNotification]
```

## Helper Functions

Please review functions defined in the following files, and invoke them as desired in [`lambda.py`](https://github.com/jeff1evesque/opensearch_customization/blob/master/lambda.py):

- [`get_configuration.py`](https://github.com/jeff1evesque/opensearch_customization/blob/master/get_configuration.py)
- [`set_configuration.py`](https://github.com/jeff1evesque/opensearch_customization/blob/master/set_configuration.py)
- [`delete_configuration.py`](https://github.com/jeff1evesque/opensearch_customization/blob/master/delete_configuration.py)

## Bug Reporting

Please open [an issue](https://github.com/jeff1evesque/opensearch_customization/issues/new) if a particular bug is found, or a feature is desired.
