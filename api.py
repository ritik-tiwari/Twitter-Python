import nltk
import requests
import jwt
#nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from flask import Flask, request, jsonify
from flask_cors import CORS
# Initialize the VADER sentiment analyzer
sid = SentimentIntensityAnalyzer()

#constants
SECRET_KEY = 'greeenprem'
outj=[]
times=2
query="cybertruck"
ex_resp= {}
url = "https://twitter-api45.p.rapidapi.com/search.php"
querystring = {"query":query,"cursor":""}
headers = {
	"X-RapidAPI-Key": "876b464d06msha4ee142ef327c07p16e67cjsn4619f32d4d59",
	"X-RapidAPI-Host": "twitter-api45.p.rapidapi.com"
}

def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}


#determine sentiment

def determine(sentence):
    # Get sentiment scores
    sentiment_scores = sid.polarity_scores(sentence)
    
    # Determine sentiment based on compound score
    if sentiment_scores['compound'] >= 0.05:
        return 'positive'
    elif sentiment_scores['compound'] <= -0.05:
        return 'negative'
    else:
        return 'neutral'



# Function to determine sentiment

app = Flask(__name__)
CORS(app)
@app.route('/sentiment', methods=['GET'])
def get_sentiment():
    outj={"data":[],"tweets":""}
    ex_resp=[]
    auth_header = request.headers.get('Authorization')
    if (not auth_header):
        return jsonify({"error":"Token not in header"})
    token = auth_header.split(' ')[1]
    decoded_token = verify_token(token)
    if 'error' in decoded_token:
        return jsonify(decoded_token)
    try:
        query = request.args.get('q')
        if not query:
            raise ValueError('Missing query parameter')
        
        # Perform sentiment analysis or any other operation based on the query
        #fetching from twitter
        for i in range(0,times):
            print("hello world",query)
            querystring['query']=query
            response = requests.get(url, headers=headers, params=querystring)
            ex_resp.append(response.json())
            print(ex_resp)
            querystring["cursor"]=ex_resp[i]["next_cursor"]
        #determining scores
        for req in ex_resp:
            for i in req['timeline']:
                sentiment = determine(i["text"])
                likes=i['favorites']
                time=i['created_at']
                outj["tweets"]=outj["tweets"]+i["text"]
                outj["data"].append({"sentiment":sentiment,"likes":likes,"time":time})
                print(len(outj))
        # For simplicity, let's just return the query in uppercase
        response = outj
        outj={"data":[],"tweets":""}
        return jsonify(response)
    except Exception as e:
        error_message = {'error': str(e)}
        return jsonify(error_message), 400

if __name__ == '__main__':
    app.run(debug=True)
