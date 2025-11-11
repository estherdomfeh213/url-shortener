import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('url-shortener-simple')

def lambda_handler(event, context):
    # CORS headers for redirect function too
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
        short_code = event['pathParameters']['short_code']
        
        response = table.get_item(Key={'short_code': short_code})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Short URL not found'})
            }
        
        item = response['Item']
        original_url = item['original_url']
        
        # Increment click count
        table.update_item(
            Key={'short_code': short_code},
            UpdateExpression='SET click_count = click_count + :inc',
            ExpressionAttributeValues={':inc': 1}
        )
        
        # Redirect to original URL
        headers['Location'] = original_url
        return {
            'statusCode': 302,
            'headers': headers,
            'body': json.dumps({'message': 'Redirecting...'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
