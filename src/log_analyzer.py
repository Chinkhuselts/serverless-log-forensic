import boto3
import re
import urllib.parse

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ThreatsTable')

PATTERNS = {
    'SQL_Injection': re.compile(r"(' OR '1'='1|UNION SELECT|admin' --)", re.IGNORECASE),
    'XSS': re.compile(r"(<script>|javascript:)", re.IGNORECASE)
}

def lambda_handler(event, context):
    # Get bucket and file name
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    print(f"Scanning file: {key}")
    
    # Read file from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    lines = response['Body'].read().decode('utf-8').split('\n')
    
    threats_found = 0
    
    with table.batch_writer() as batch:
        for line in lines:
            if not line: continue
            
            for attack_name, pattern in PATTERNS.items():
                if pattern.search(line):)
                    ip = line.split(' ')[0]
                    

                    batch.put_item(Item={
                        'AttackID': f"{ip}-{attack_name}-{random_id()}",
                        'IP': ip,
                        'Type': attack_name,
                        'Payload': line
                    })
                    threats_found += 1
                    print(f"ALERT: {attack_name} detected from {ip}")

    return {"status": "Success", "threats_detected": threats_found}

def random_id():
    import uuid
    return str(uuid.uuid4())