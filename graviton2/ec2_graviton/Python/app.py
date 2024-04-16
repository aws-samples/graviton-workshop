from flask import Flask, render_template, request, jsonify
import short_url
from short_url import create_short_url, retrive_from_dynamo
import boto3

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hi everyone'

# # post parameter from url
# @app.route('/shortenURL', methods=['POST'])
# def short_url_post():
#     data = request.get_json()
#     url = data.get('url')
#     return create_short_url(url)

@app.route('/shortenURL', methods=['POST'])
def short_url_post():
    session = boto3.session.Session()
    return session.region_name
    data = request.get_json()
    original_url = data.get('OriginalURL')  # Use the correct key from your JSON payload
    if not original_url:
        return jsonify({'error': 'Missing URL'}), 400
    short_url = create_short_url(original_url)
    return  short_url  # Make sure to return a JSON object with the shortURL key


#get full url from short url
@app.route('/getFullURL', methods=['GET'])
def redirect_short_url():
    short_url = request.args.get('short_url', default=None, type=str)
    full_url = retrive_from_dynamo(short_url)
    return full_url['url']

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000, debug=True)

