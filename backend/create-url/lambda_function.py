import json
import boto3
import hashlib

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('url-shortener-simple')

def lambda_handler(event, context):
    print("Event:", json.dumps(event))
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token',
        'Access-Control-Allow-Credentials': 'true'
    }
    
    # Handle preflight OPTIONS request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight'})
        }
    
    try:
        body = json.loads(event['body'])
        url = body.get('url', '')
        
        if not url.startswith(('http://', 'https://')):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'URL must start with http:// or https://'})
            }
        
        # Generate short code
        short_code = hashlib.md5(url.encode()).hexdigest()[:6]
        
        # Store in DynamoDB
        table.put_item(Item={
            'short_code': short_code,
            'original_url': url,
            'click_count': 0
        })
        
        # Build the short URL
        short_url = f"https://{event['requestContext']['domainName']}/Prod/r/{short_code}"
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'short_code': short_code,
                'short_url': short_url,
                'original_url': url
            })
        }
        
    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
