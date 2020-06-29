import constants
import oauth2
import urllib.parse as urlparse
import json
from user import User
from database import Database

consumer = oauth2.Consumer(constants.CONSUMER_KEY, constants.CONSUMER_SECRET)

Database.initialize(user='postgres', password='Mysql#123', host='localhost', database='learning')

user_email = input("Enter your e-mail address: ")
user = User.load_from_db_by_email(user_email)

if not user:
    # Create consumer, who uses CONSUMER_KEY, CONSUMER_SECRET to adentify app uniquely
    client = oauth2.Client(consumer)
    # Use client to perform a request for the request token
    # send request to get a token
    response, content = client.request(constants.REQUEST_TOKEN_URL, 'POST')
    if response.status != 200:
        print('An error occured getting the request token from Twitter')
    # get request token parsing the query string returned
    # parsing information from bytes to a string
    request_token = dict(urlparse.parse_qsl(content.decode('utf-8')))
    # Ask the user to get a pin code and authorize
    print('Go to the following site in your browser: ')
    print('{}?oauth_token={}'.format(constants.AUTHORIZATION_URL, request_token['oauth_token']))

    oauth_verifier = input("What is the Pin? ")

    # create token Objject that contains the request token and verifier

    token = oauth2.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)

    # create client with our consumer and the newly created and verified token
    client = oauth2.Client(consumer, token)
    # Ask tweeter fir an access token, and Twitter knows it should give us it because we've verified the request
    response, content = client.request(constants.ACCESS_TOKEN_URL, 'POST')
    access_token = dict(urlparse.parse_qsl(content.decode('utf-8')))

    print(access_token)
    # Create an "authorized_token" Token object and use to perform Twitter API calls on behalf of the user

    # Uploading user to PostgreSQL
    # email = input("Enter your email: ")

    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")
    user = User(user_email, first_name, last_name, access_token['oauth_token'], access_token['oauth_token_secret'],
                None)
    user.save_to_db()

authorized_token = oauth2.Token(user.oauth_token, user.oauth_token_secret)
# authorized_token = oauth2.Token(access_token['oauth_token'], access_token['oauth_token_secret'])
authorized_client = oauth2.Client(consumer, authorized_token)

# Make Twitter API calls
response, content = authorized_client.request(
    'https://api.twitter.com/1.1/search/tweets.json?q=computers+filter:images', 'GET')
if response.status != 200:
    print("An error occurred when searching!")

tweets = json.loads(content.decode('utf-8'))

for tweet in tweets['statuses']:
    print(tweet['text'])
