import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('url-shortener')

def lambda_handler(event, context):
    try:
        short_code = event['pathParameters']['short_code']
        
        # Get the URL from DynamoDB
        response = table.get_item(Key={'short_code': short_code})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Short URL not found'})
            }
        
        item = response['Item']
        original_url = item['original_url']
        
        # Update click count
        table.update_item(
            Key={'short_code': short_code},
            UpdateExpression='SET click_count = click_count + :val',
            ExpressionAttributeValues={':val': 1}
        )
        
        # Redirect to original URL
        return {
            'statusCode': 302,
            'headers': {
                'Location': original_url,
                'Access-Control-Allow-Origin': '*'
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }