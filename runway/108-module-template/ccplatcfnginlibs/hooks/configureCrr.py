"""hook to configure source and destination buckets for cross region replication"""
import boto3
from ccplatcfnginlibs.ccplatlogger import CCPLAT_LOGGER as LOGGER
import os
import yaml

from ccplatcfnginlibs.helpers import cloudformation, sts
from botocore.exceptions import ClientError


def get_s3_client():  # pragma: no cover
	"""
	boto3 client for s3
	This is here for unit testing
	:return:
	"""
	return boto3.client("s3")


def get_iam_client():  # pragma: no cover
	"""
	boto3 client for IAM
	This is here for unit testing
	:return:
	"""
	return boto3.client("iam")


def replication_hook(provider, context, **kwargs):
	"""
	hook to configure source and destination buckets for
	cross region replication
	"""

	# get module config file name
	module_config = context.environment["module_config"]

	# load module config and configure source bucket
	with open(module_config) as file:
		bucket_list = yaml.load(file, Loader=yaml.FullLoader)["vBucketList"]
		configure_replication_rules(context, bucket_list)

	return True


def get_tags(context):
    """get tags"""
    # construct list of tags based on context environment
    tags = [
        # business service
        {
            "Key": "SWA:BusinessService",
            "Value": context.environment["business_service"]
        },
        # compliance
        {
            "Key": "SWA:Compliance",
            "Value": context.environment["compliance"]
        },
        # confidentiality
        {
            "Key": "SWA:Confidentiality",
            "Value": context.environment["confidentiality"]
        },
        # cost center
        {
            "Key": "SWA:CostCenter",
            "Value": context.environment["cost_center"].replace('"','')
        },
        # environment
        {
            "Key": "SWA:Environment",
            "Value": context.environment["environment"]
        },
        # name
        {
            "Key": "SWA:Name",
            "Value": context.environment["department"]
        },
        # pid
        {
            "Key": "SWA:PID",
            "Value": context.environment["swa_pid"]
        },
        # create date
        {
            "Key": "CreateDate",
            "Value": context.environment["createDate"].replace("'", "")
        },
        # module name
        {
            "Key": "CCPModuleName",
            "Value": context.environment["module_name"]
        },
        # module version
        {
            "Key": "CCPModuleVersion",
            "Value": context.environment["module_version"]
        },
        # namespace
        {
            "Key": "CCPNamespace",
            "Value": context.environment["namespace"]
        }
    ]
    return tags


def create_role_for_crr(tags, account_id, bucket_name):
	"""create IAM role for source bucket"""
	LOGGER.info(f"Creating IAM role for source bucket {bucket_name}")
	# determine role name
	role_name = f"s3crr_role_for_{bucket_name}"

	# attempt to create role
	try:
		LOGGER.info(f"Creating IAM role {role_name}")
		cr_resp = get_iam_client().create_role(
			Path = "/service-role/",
			RoleName = role_name,
			# trust policy
			AssumeRolePolicyDocument = '{ \
				"Version":"2012-10-17", \
				"Statement":[ \
					{ \
						"Effect":"Allow", \
						"Principal":{ \
							"Service":"s3.amazonaws.com" \
						}, \
						"Action":"sts:AssumeRole" \
					} \
				] \
			}',
			# added SWACS permission boundary
			PermissionsBoundary = f"arn:aws:iam::{account_id}:policy/swa/SWACSPermissionsBoundary",
			# include tags on resource
			Tags = tags
		)
		LOGGER.debug(f"Create role response: {cr_resp}")
	# skip if role is already exists else raise exception
	except ClientError as error:
		if error.response['Error']['Code'] == 'EntityAlreadyExists':
			LOGGER.info(f"Role {role_name} already exists. Skipping.")
		else:
			LOGGER.error(f"Error occurred while creating role {role_name}: {str(error)}")
			raise Exception(f"Error occurred while creating CRR role {role_name}")
	except Exception as exp:
		LOGGER.error(f"Error occurred while creating role {role_name}: {str(exp)}")
		raise Exception(f"Error occurred while creating CRR role {role_name}")


	return role_name


def create_policy_for_crr(source_region, dest_region, source_bucket, dest_bucket,
                          account_id):
	"""create policy"""
	# get kms key from source region
	source_kms = cloudformation.get_kms_key_id(account_id, source_region)
	# get kms key from cross region
	dest_kms = cloudformation.get_kms_key_id(account_id, dest_region)

	# determine policy name
	policy_name = f"s3crr_kms_for_{source_bucket}_to_{dest_bucket}"
	# define policy document
	policy_doc = {
		"Version":"2012-10-17",
		"Statement":[
			# allow replication of source bucket
			{
				# actions needed for source replication
				"Action":[
					"s3:ListBucket",
					"s3:GetReplicationConfiguration",
					"s3:GetObjectVersionForReplication",
					"s3:GetObjectVersionAcl"
				],
				"Effect":"Allow",
				# allow actions on source and all items inside source bucket
				"Resource":[
					f"arn:aws:s3:::{source_bucket}",
					f"arn:aws:s3:::{source_bucket}/*"
				]
			},
			# allow destination bucket to receive replicated objects
			{
				# actions needed for destination replication
				"Action":[
					"s3:ReplicateObject",
					"s3:ReplicateDelete",
					"s3:ReplicateTags",
					"s3:GetObjectVersionTagging"
				],
				"Effect":"Allow",
				"Condition":{
					"StringLikeIfExists":{
						"s3:x-amz-server-side-encryption":[
							"aws:kms",
							"AES256"
						],
						"s3:x-amz-server-side-encryption-aws-kms-key-id":[
							dest_kms
						]
					}
				},
				# allow actions on all items inside destination bucket
				"Resource":f"arn:aws:s3:::{dest_bucket}/*"
			},
			# allow decryption of objects in source bucket
			{
				# actions needed for kms decryption
				"Action":[
					"kms:Decrypt"
				],
				"Effect":"Allow",
				# decrypt if condition is met
				"Condition":{
					"StringLike":{
					"kms:ViaService":f"s3.{source_region}.amazonaws.com",
					"kms:EncryptionContext:aws:s3:arn":[
						f"arn:aws:s3:::{source_bucket}/*"
					]
					}
				},
				# kms key id of source region
				"Resource":[
					source_kms
				]
			},
			# allow encryption of objects in destination bucket
			{
				# actions needed for kms decryption
				"Action":[
					"kms:Encrypt"
				],
				"Effect":"Allow",
				# decrypt if condition is met
				"Condition":{
					"StringLike":{
						"kms:ViaService":f"s3.{dest_region}.amazonaws.com",
						"kms:EncryptionContext:aws:s3:arn":[
							f"arn:aws:s3:::{dest_bucket}/*"
						]
					}
				},
				# kms key id of destination region
				"Resource":[
					dest_kms
				]
			}
		]
	}
	# policy doc needs to be in the form of a string
	policy_doc = str(policy_doc).replace("'", "\"")

	# attempt to create policy
	try:
		LOGGER.info(f"Creating policy {policy_name}")
		cp_resp = get_iam_client().create_policy(
			PolicyName = policy_name,
			PolicyDocument = policy_doc
		)
		LOGGER.debug(f"Create policy response: {cp_resp}")
	# skip if policy already exists else raise exception
	except ClientError as error:
		if error.response['Error']['Code'] == 'EntityAlreadyExists':
			LOGGER.info(f"Policy {policy_name} already exists. Skipping.")
		else:
			LOGGER.error(f"Error occurred while creating policy {policy_name}: {str(error)}")
			raise Exception(f"Error occurred while creating CRR policy {policy_name}")
	except Exception as exp:
		LOGGER.error(f"Error occurred while creating policy {policy_name}: {str(exp)}")
		raise Exception(f"Error occurred while creating CRR policy {policy_name}")

	return policy_name


def attach_role_policy_for_crr(account_id, role_name, policy_name):
	"""attach policy to role"""
	LOGGER.info(f"Attaching role {role_name} to policy {policy_name}")

	# attach policy to role
	arp_resp = get_iam_client().attach_role_policy(
		RoleName = role_name,
		PolicyArn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
	)
	LOGGER.debug(f"Attach role policy response: {arp_resp}")


def add_replication(account_id, source_bucket, dest_bucket, dest_region, role_name):
	"""add replication rule onto source bucket"""
	LOGGER.info(f"Adding replicaiton rule to source bucket {source_bucket}")
	# get cross region's kms key id
	dest_kms = cloudformation.get_kms_key_id(account_id, dest_region)

	# add replication rule
	pbr_resp = get_s3_client().put_bucket_replication(
		# replication rule applied to source bucket
		Bucket = source_bucket,
		ReplicationConfiguration = {
			"Role": f"arn:aws:iam::{account_id}:role/service-role/{role_name}",
			# create replication rule
			"Rules": [
				{
					# enable rule
					"Status": "Enabled",
					# without specification of Filter, S3 assumes earlier version (V1)
					# we want latest version of schema
					"Filter": {},
					# enabled replication of kms encrypted objects
					"SourceSelectionCriteria": {
						"SseKmsEncryptedObjects": {
							"Status": "Enabled"
						}
					},
					# currently, the only valid status is disabled
					"DeleteMarkerReplication": {
						"Status": "Disabled"
					},
					# specifies replication destination
					"Destination": {
						# kms key used for encrypted objects in destination
						"EncryptionConfiguration": {
							"ReplicaKmsKeyID": dest_kms
						},
						"Bucket": f"arn:aws:s3:::{dest_bucket}",
						# enable replication time control
						"ReplicationTime": {
							"Status": "Enabled",
							# currently, the only valid value of minutes is 15
							"Time": {
								"Minutes": 15
							}
						},
						# if rtc is enabled, metrics must also be specified
						"Metrics": {
							"Status": "Enabled",
							# currently, the only valid value of minutes is 15
							"EventThreshold": {
								"Minutes": 15
							}
						}
					},
					# rule takes highest priority
					"Priority": 1,
					"ID": f"{source_bucket}-replication"
				}
			]
		}
	)
	LOGGER.debug(f"Put bucket replication response: {pbr_resp}")


def configure_rule(tags, account_id, source_bucket, source_region, dest_bucket, dest_region):
	"""add replication rule to source bucket"""
	# create iam role for source bucket
	role_name = create_role_for_crr(
							tags,
							account_id,
							source_bucket
						)
	# create iam policy for role
	policy_name = create_policy_for_crr(
							source_region,
							dest_region,
							source_bucket,
							dest_bucket,
							account_id
						)
	# attach source policy to source role
	attach_role_policy_for_crr(account_id, role_name, policy_name)
	# add replication rule to source bucket
	add_replication(account_id, source_bucket, dest_bucket, dest_region, role_name)


def configure_replication_rules(context, bucket_list):
	"""
	configure replication rules on both source and destination buckets
	for bi-directional replication
	"""
	# get account id
	account_id = sts.get_account_id()
	# get environment info
	department = context.environment["department"]
	namespace = context.environment["namespace"]
	source_region = context.environment["region"]
	# standard tags on resources
	tags = get_tags(context)

	existing_buckets = get_s3_client().list_buckets()["Buckets"]
	existing_buckets = [bucket["Name"] for bucket in existing_buckets]

	# iterate through bucket list
	for bucket in bucket_list:
		# check that cross region is enabled
		if "crossRegion" in bucket:
			# list of already created buckets
			# determine bucket name
			bucket_name = bucket["name"]
			# source info
			source_bucket = f"{department}-{source_region}-{namespace}-{bucket_name}"
			# dest info
			dest_region = bucket["crossRegion"]
			dest_bucket = f"{department}-{dest_region}-{namespace}-{bucket_name}"

			# check that both buckets have already been created
			LOGGER.debug(f"Existing: {existing_buckets}")
			LOGGER.debug(f"Source: {source_bucket}")
			LOGGER.debug(f"Destination: {dest_bucket}")
			if source_bucket in existing_buckets and dest_bucket in existing_buckets:
				# source bucket replication rule
				LOGGER.info(f"Configuring replication rule on {source_bucket}")
				configure_rule(
					tags,
					account_id,
					source_bucket,
					source_region,
					dest_bucket,
					dest_region
				)
				# destination bucket replication rule
				LOGGER.info(f"Configuring replication rule on {dest_bucket}")
				configure_rule(
					tags,
					account_id,
					dest_bucket,
					dest_region,
					source_bucket,
					source_region
				)
	return True