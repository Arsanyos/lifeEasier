import requests
import json

def send_request_and_record_response(item, base_url, bearer_token):
    method = item['request']['method']
  
    if 'url' in item['request']:
        url_parts = item['request']['url']
        if isinstance(url_parts, dict):
            url_raw = url_parts.get('raw', '')
            url = url_raw.replace('{{convexURL}}', base_url)
        else:
            url = item['request']['url'].replace('{{convexURL}}', base_url)
    else:
        raise ValueError("No URL found in the request item.")
    
    headers = {header['key']: header['value'] for header in item['request'].get('header', [])}
    headers['Authorization'] = f'Bearer {bearer_token}'  # Add the Bearer token to the headers

    body = item['request'].get('body', {}).get('raw', None)

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=body)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, data=body)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, data=body)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, data=body)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response_record = {
            'url': url,
            'method': method,
            'status_code': response.status_code,
            'response_body': response.json() if response.headers.get('Content-Type') == 'application/json' else response.text,
            'headers': dict(response.headers),
        }
        return response_record
    
    except requests.RequestException as e:
        print(f"Request failed for {method} {url}: {e}")
        return {
            'url': url,
            'method': method,
            'status_code': None,
            'response_body': str(e),
            'headers': {}
        }

def process_items(items, base_url, bearer_token):
    responses = []
    for item in items:
        if 'item' in item: 
            responses.extend(process_items(item['item'], base_url, bearer_token))
        else: 
            response_record = send_request_and_record_response(item, base_url, bearer_token)
            responses.append(response_record)
    return responses

if __name__ == "__main__":
    # Prompt user for inputs
    file_path = input("Enter the path to the Postman collection file: ")
    base_url = input("Enter the base URL for the API: ")
    bearer_token = input("Enter the bearer token for authentication: ")

    # Read the Postman collection file
    with open(file_path, 'r') as file:
        postman_collection = json.load(file)

    # Process the items and send requests
    responses = process_items(postman_collection['item'], base_url, bearer_token)

    # Save the responses to a JSON file
    with open('responses.json', 'w') as response_file:
        json.dump(responses, response_file, indent=4)

    print("All requests have been sent and responses recorded.")
