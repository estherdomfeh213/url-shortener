import json
import boto3
import hashlib
import os
from urllib.parse import urlparse
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('url-shortener')

def is_valid_url(url):
    """Validate URL format - FIXED VERSION"""
    try:
        result = urlparse(url)
        
        # More flexible validation
        if not result.scheme:
            # Try adding https:// if no scheme provided
            url = 'https://' + url
            result = urlparse(url)
            
        # Check if it has either netloc or path (for very short URLs)
        has_netloc = bool(result.netloc)
        has_valid_scheme = result.scheme in ['http', 'https', 'ftp']
        
        return has_netloc and has_valid_scheme
        
    except Exception as e:
        print(f"URL validation error: {e}")
        return False

def generate_short_code(url, length=6):
    """Generate a unique short code for the URL"""
    # Add some randomness to avoid collisions for same URLs
    import time
    import random
    random_seed = str(time.time()) + str(random.random())
    return hashlib.md5((url + random_seed).encode()).hexdigest()[:length]

def lambda_handler(event, context):
    # Enable CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # Handle preflight OPTIONS request
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight'})
        }
    
    if event['httpMethod'] == 'POST':
        try:
            body = json.loads(event['body'])
            original_url = body.get('url', '').strip()
            
            print(f"Received URL: {original_url}")  # Debug log
            
            # Validate URL with auto-fix for common issues
            if not original_url:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'URL is required'})
                }
            
            # Auto-fix common URL issues
            if not original_url.startswith(('http://', 'https://')):
                original_url = 'https://' + original_url
                print(f"Auto-corrected URL to: {original_url}")  # Debug log
            
            if not is_valid_url(original_url):
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': f'Invalid URL format: {original_url}'})
                }
            
            # Generate short code
            short_code = generate_short_code(original_url)
            
            # Store in DynamoDB
            table.put_item(Item={
                'short_code': short_code,
                'original_url': original_url,
                'created_at': datetime.now().isoformat(),
                'click_count': 0
            })
            
            # Construct short URL
            domain = event['requestContext']['domainName']
            stage = event['requestContext']['stage']
            short_url = f"https://{domain}/{stage}/r/{short_code}"
            
            print(f"Created short URL: {short_url}")  # Debug log
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'short_code': short_code,
                    'short_url': short_url,
                    'original_url': original_url
                })
            }
            
        except Exception as e:
            print(f"Error: {str(e)}")  # Debug log
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': f'Internal server error: {str(e)}'})
            }
    
    return {
        'statusCode': 405,
        'headers': headers,
        'body': json.dumps({'error': 'Method not allowed'})
    }