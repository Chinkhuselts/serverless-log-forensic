import boto3
import matplotlib.pyplot as plt

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
table = dynamodb.Table('ThreatsTable')

response = table.scan()
items = response['Items']

# Count attacks
counts = {}
for item in items:
    attack_type = item['Type']
    counts[attack_type] = counts.get(attack_type, 0) + 1

plt.bar(counts.keys(), counts.values(), color=['red', 'blue'])
plt.title('Web Attacks Detected by Serverless Pipeline')
plt.xlabel('Attack Type')
plt.ylabel('Count')
plt.show()