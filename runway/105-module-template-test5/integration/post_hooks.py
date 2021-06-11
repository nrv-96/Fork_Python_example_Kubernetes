import boto3

def main():
    print("Post hooks: Do something here")
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    print (f"Account ID: {account_id}")

if __name__ == "__main__":
    main()