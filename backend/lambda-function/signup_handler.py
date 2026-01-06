import boto3
import json

# --- CONFIGURATION ---
CLUSTER_ARN = "arn:aws:rds:us-east-1:211125648950:cluster:database"
SECRET_ARN = "arn:aws:secretsmanager:us-east-1:211125648950:secret:rds!cluster-9612de0f-e8f6-4fbf-bdc2-4c049d164573-M3FKzF"
DATABASE_NAME = "emeka" 
SENDER_EMAIL = "emeka.iwu@hotmail.com" 

# Initialize Clients
rds_client = boto3.client('rds-data')
ses_client = boto3.client('ses', region_name='us-east-1')

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }
    
    try:
        # 1. Parse the incoming data
        body = json.loads(event.get('body', '{}'))
        print(f"DEBUG - Received Body: {body}") 
        
        # 2. Extract values using keys matching the HTML/JS payload
        full_name = body.get('name', 'Gamer')       
        email = body.get('email', '')               
        console = body.get('console', 'Not Specified') 
        gamer_id = body.get('gamer_id', None)      

        # 3. Insert into RDS
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
            secretArn=SECRET_ARN, resourceArn=CLUSTER_ARN,
            database=DATABASE_NAME, sql=sql, parameters=sql_params
        )

        # 4. Send Welcome Email
        ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': "Welcome to the Elite Gamers Waitlist!"},
                'Body': {
                    'Text': {'Data': f"Hi {full_name},\n\nSuccess! You have been added to the waitlist for your {console}. Your Gamer ID: {gamer_id if gamer_id else 'N/A'}.\n\nWe will notify you as soon as we launch."}
                }
            }
        )

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"message": "Successfully registered!"})
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
