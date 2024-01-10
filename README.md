# Mario's Espresso Pipeline Cafe

## Background
This project aims to meet the needs of our client, Maze Cafe Group, a rapidly growing UK coffee chain. Our client faced limitations in technologies used to store and process sales data, with each branch having previously stored data independently and locally. We proposed to build technical infrastructure that met the client needs in both centralising data across branches, as well as providing business intelligence tools for analysis and business decision making. 

This product is a fully scalable ETL pipeline hosted in AWS Cloud Services and has the ability to process large volumes of transactional data per cafe in a single location. This data is stored in a data warehouse can be integrated with data analysis and visualation tools. Our client is now able to access and identify customer trends across their business, aiding business developement.


## Key Features and Impacts
- Raw sales data from different branches are stored in an S3 bucket
- Fully scalable ETL pipeline, cleaning and transforming raw sales data into a preferred format, ready for analysis
- Using Grafana for data visualisation in order to generate reports for business analytics (insights and performance)
- Ability to identify customer trends, allowing for targeted marketing for different groups of customers to enhance customers'experience

# Technical Architecture

## Overview
We developed a fully scalable ETL pipeline using AWS services that can validate, obtain, process, store and analyse data from sources, storing data in one central system (data warehouse). We also integrated data visualisation tools (Grafana) for analysis and monitoring purposes.


### Prerequisites
Ensure you have the following prerequisites:

  1. AWS account with appropriate IAM roles.
  2. Redshift cluster created with the necessary tables (orders, branches, products, orders_details).
  3. An S3 bucket created for deploying a CloudFormation stack and an S3 bucket for storing CSV file uploads.

## S3 Bucket
A deployment bucket is required to store a CloudFormation template file that is used to create a CloudFormation stack which specifies the following AWS resources required to build an ETL pipeline:
- Lamda Function
- IAM Role
- S3 bucket

The following document can be deployed to create a CloudFormation stack that provided the necessary infrasture:
    production_template.yaml

An S3 bucket is also used to store transactional data across branches. The data is saved as a CSV file uploaded to the S3 bucket EOD. The upload of a file into this bucket triggers an ETL process.

## Lambda
Please refer to Lambda_function.py

This Lambda function implements ETL logic to process CSV files uploaded to an S3 bucket, perform data transformations and load processed data into a Redshift database. S3 events trigger the function, and it provides a seamless integration between AWS services for efficient data processing.

### Table of Contents
  * Setup
  * Extraction and transformations
  * Loading transformed data
  * Monitoring and Logging
  * Troubleshooting and debugging
  * Unit testing

### Setup:
As CloudFormation provides infrastructure as code, an S3 trigger was specified in CloudFormation template (see production_template.yaml). The S3 trigger invokes the Lambda function when an object is uploaded in the configured S3 bucket. 

Other basic settings of our Lambda function, including Python runtime, are defined in the CloudFormation template.

The necessary external dependencies packages required were also uploaded as a deployment package. The requirements needed are listed below and were uploaded as a zip package to the Lambda function (mopsycopg.zp):

```
numpy==1.22.1
pandas==1.4.0
python-dateutil==2.8.2
pytz==2021.3
six==1.16.0
boto3
```

Other roles and permissions necessary to setup include:
 - Lambda Executation role to connect to RedShift VPC is required
 - Role to retrieve RedShift database connection details from AWS Systems Manager (SSM). The SSM parameter should be configured with the Redshift cluster information.

### Extraction and Tranformations:
* Reads CSV data from configured S3 bucket.
* Cleans and transforms order data.
* Remove sensitive information.
* Generates pseudo-random IDs for data columns according to database schema.

### Loading transformed data:
* Connects to a Redshift database via SSM parameters 
* Loads processed data into Redshift tables (orders, branches, products, orders_details).

### Monitoring and Logging
AWS resources allow for logging and monitoring via AWS CloudWatch. 

CloudWatch Metrics include:
* Invocations: Number of times the function is invoked.
* Errors: Number of errors during execution.
* CloudWatch Logs: View detailed logs for debugging and troubleshooting.

### Troubleshooting and debugging
Common Issues:
  1. SSM Parameter:
    Ensure the SSM parameter marios_espresso_pipeline_redshift_settings is correctly configured.
  2. IAM Permissions:
     Check Lambda's IAM role for S3, Lambda and Redshift permissions.
  3. Redshift Cluster:
     Ensure the Redshift cluster is properly configured and accessible.
     
For detailed debugging, check CloudWatch Logs for the Lambda function.
The function logs errors to CloudWatch Logs, providing insights into any issues during the execution.

### Unit testing
Please refer to the unit testing folder.

To ensure both functionality and quality, unit tests were designed to test the extraction and transformation processes

To run a unit test, please run the following command:

For Windows:
```
py -m pytest
```
For Mac:
```
python3 -m pytest
```

## Grafana
### EC2 Instance
Creation of Security Group
1) Locate the Security  Group page of EC2 Instance on console and select create security group.
2) Create a security group with a new name with specification:
VPC - RedshiftVPC
Inbound Rules: SSH -  0.0.0.0/0 , HTTP -  0.0.0.0/0 ,
Outbound Rule: TCP -  0.0.0.0/0

Creation and connection of EC2 Instance
1) Name the EC2 Instance and tag.
2) Modify EC2 Instance following the specification list.
3) Click connect of the instance and follow the instruction from the console.
```
Specification:
    Application and OS Images - Amazon Linux 2023
    Instance Type - t2.micro
    Key pair - create your own / team key pair
    VPC - RedshiftVPC
    Subnet - PublicRedshiftSubnet0
    Auto-assign Public IP - Enable
    Firewall(security group) - security group you created at  security group step
    IAM Instance profile - ec2-role
```

## Docker
After connected to EC2 Instance, install docker:

    ```
    sudo yum install docker -y
    sudo service docker start
    sudo usermod -a -G docker ec2-user
    sudo chkconfig docker on
    ```
Docker checking commands:
```
List all containers: docker ps -a
Stop container: docker stop <container-id>
Remove container: docker rm <container-id>
Create a docker volume:
docker volume create grafana-storage
List all the create volume:
docker volume ls
```
Create Grafana container:
```
sudo docker run -d -p 80:3000 --rm --volume grafana-storage:/var/lib/grafana grafana/grafana ;
```
1) Stop EC2 Instance and edit user data with this information and save it:
```
Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0

--//
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="cloud-config.txt"

#cloud-config
cloud_final_modules:
- [scripts-user, always]

--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash
sudo docker run -d -p 80:3000 --rm --volume grafana-storage:/var/lib/grafana grafana/grafana
--//--
```
### Grafana
Grafana serves as our visualisation tool, providing insightful representations of the data collected from multiple cafes. It allows us to:
- **Aggregate data:** Combine and analyse data gained from daily csv files
- **Create visual dashboards:** Utilise Grafana's interface to design an informative dashboard highlighting key metrics and data gathered from the cafes
- **Enable data-driven solutions:** Allow stakeholders to make informed decisions based on the visualisations

#### How to access Grafana
To access Grafana you can create an EC2 instance and obtain the public IP address.

#### Why Grafana?
Grafana transforms raw data into meaningful visual representations, providing actionable insights.

### CloudWatch
Cloudwatch metrics displayed in Grafana include:
- EC2 instance CPU usage
- Lambda invocations

### CI/CD Pipeline
A common tool and critical process for new features and services deployment within devops operation as automated integration of new codes and features mingled into the operating software or products. Within this project, we used GitHub Actions as our CI/CD pipeline for the control of software compatability with new features.

### Upfront Setting
 Creation of new directory on the repository
 >.github/workflows

Connect AWS and repository
1) Search for 'github-cicd-role' in the roles tab of IAM.
2) If the role exists, copy ARN and store in the secret section of GitHub repository.
3) If role does not exist, create a 'github-cicd-role', copy ARN and store in the secret section of GitHub repository.

Deployment of CI/CD pipeline
1) Copy 'aws_cicd.yml' for our repository or create your own template to path of repository '.github/workflows'
2) Create a template that stores the services needed to be implemented in ci/cd pipeline in ymal format , and save on repository.
3) Create a yaml template for configuration of services or applications with related role and permission, and save on repository.

Operation of CI/CD pipeline
1) As long as the pipeline was triggered, the workflows automatically process with the sign in the repository.
2) If a tick appeared, the procedure was completed successfully.
3) If a cross appeared, the procedure was not completed successfully.

