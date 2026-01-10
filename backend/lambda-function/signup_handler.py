import boto3
import json
import os

# --- CONFIGURATION (SECURELY FETCHED FROM AWS ENVIRONMENT) ---
# Ensure these keys (CLUSTER_ARN, SECRET_ARN, DATABASE_NAME, SENDER_EMAIL) 
# are set in the Lambda 'Environment variables' console.
CLUSTER_ARN = os.environ.get('CLUSTER_ARN')
SECRET_ARN = os.environ.get('SECRET_ARN')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')

# Initialize Clients
# Note: Data API and SES are used here
rds_client = boto3.client('rds-data')
ses_client = boto3.client('ses', region_name='us-east-1')

def lambda_handler(event, context):
    # Professional CORS Headers: Restricted to your domain
    headers = {
        "Access-Control-Allow-Origin": "https://emeka.cloud",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }
    
    # Handle preflight OPTIONS requests from the browser
    if event.get('httpMethod') == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": headers,
            "body": ""
        }

    try:
        # 1. Parse the incoming data from the HTML form/API Gateway
        body = json.loads(event.get('body', '{}'))
        
        # 2. Extract values (Matching your HTML form 'name' attributes)
        full_name = body.get('name', 'Gamer')
        email = body.get('email', '')
        console = body.get('console', 'Not Specified')
        gamer_id = body.get('gamer_id', None)

        if not email:
            raise ValueError("Email is required for registration.")

        # 3. Insert into Aurora PostgreSQL via Data API
        # Using Parameters protects against SQL Injection
        sql = """
        INSERT INTO elite_gamers_waitlist (full_name, email_address, console, gamer_id)
        VALUES (:f_name, :email, :console, :g_id)
        """
        sql_params = [
            {'name': 'f_name', 'value': {'stringValue': full_name}},
            {'name': 'email', 'value': {'stringValue': email}},
            {'name': 'console', 'value': {'stringValue': console}},
            {'name': 'g_id', 'value': {'stringValue': gamer_id} if gamer_id else {'isNull': True}}
        ]

        rds_client.execute_statement(
            secretArn=SECRET_ARN, 
            resourceArn=CLUSTER_ARN,
            database=DATABASE_NAME, 
            sql=sql, 
            parameters=sql_params
        )

        # 4. Send Welcome Email via Amazon SES
        ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': "Welcome to the Elite Gamers Waitlist!"},
                'Body': {
                    'Text': {
                        'Data': (
                            f"Hi {full_name},\n\n"
                            f"Success! You have been added to the waitlist for your {console}. "
                            f"Your Gamer ID: {gamer_id if gamer_id else 'N/A'}.\n\n"
                            "We will notify you as soon as we launch. Thanks for joining!"
                        )
                    }
                }
            }
        )

        # 5. Success Response
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"message": "Successfully registered!"})
        }

    except Exception as e:
        # Logging for CloudWatch (Internal Debugging)
        print(f"ERROR: {str(e)}")
        
        # Friendly response for the user (Doesn't leak internal DB errors)
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Submission failed. Please check your data and try again."})
        }
