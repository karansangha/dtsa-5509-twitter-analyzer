from flask import Flask, request, render_template
import tweepy
import os

app = Flask(__name__)


@app.route("/")
def main():
    return '''
     <h1>Twitter Analyzer</h1>
     <form action="/echo_user_input" method="POST">
         <label for="user_input">Enter any text - </label>
         <input name="user_input">
         <input type="submit" value="Submit!">
     </form>
     '''


@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "")
    return "<h1>Thank you for using the form!</h1><p>You entered: " + input_text + "</p>"

# This function authenticates with the Twitter API
def authenticate():
    """Authenticates with the Twitter API.

    Returns:
        tweepy.API: API object to interact with Twitter.
    """
    auth = tweepy.OAuthHandler(os.environ.get("TWITTER_CONSUMER_KEY"), os.environ.get("TWITTER_CONSUMER_SECRET"))
    auth.set_access_token(os.environ.get("TWITTER_ACCESS_TOKEN"), os.environ.get("TWITTER_ACCESS_TOKEN_SECRET"))
    api = tweepy.API(auth)
    return api

# This function returns the tweets of a user
def get_tweets(api, username: str, count: int = 10) -> list:
    """Returns the tweets of a user.

    Args:
        api (tweepy.API): API object to interact with Twitter.
        username (str): Username of the Twitter user.
        count (int, optional): Number of tweets to return. Defaults to 10.

    Returns:
        list: List of tweets.
    """
    tweets = api.user_timeline(screen_name=username, count=count, tweet_mode="extended")
    return tweets

api_model = authenticate()

@app.route("/get_tweets", methods=["POST"])
def get_tweets_route():
    username = request.form.get("username", "")
    if not username:
        return render_template("tweets.html", error="Please enter a username.")
    try:
        tweets = get_tweets(api_model, username)
    except tweepy.TweepError:
        return render_template("tweets.html", error="Error getting tweets.")
    return get_tweets_route_username(username)

@app.route("/get_tweets/<username>")
def get_tweets_route_username(username):
    tweets = get_tweets(api_model, username)
    avg_length = get_average_length(tweets)
    avg_likes = get_average_likes(tweets)
    avg_retweets = get_average_retweets(tweets)
    return render_template("tweets.html", user=username, tweets=tweets, avg_length=avg_length, avg_likes=avg_likes, avg_retweets=avg_retweets)

# Create a function to get the average length of the tweets
def get_average_length(tweets: list) -> float:
    """Returns the average length of the tweets.

    Args:
        tweets (list): List of tweets.

    Returns:
        float: Average length of the tweets.
    """
    tweet_lengths = [len(tweet.full_text) for tweet in tweets]
    avg_length = sum(tweet_lengths) / len(tweet_lengths)
    return avg_length

# Create a function to get the average number of likes
def get_average_likes(tweets: list) -> float:
    """Returns the average number of likes.

    Args:
        tweets (list): List of tweets.

    Returns:
        float: Average number of likes.
    """
    likes = [tweet.favorite_count for tweet in tweets]
    avg_likes = sum(likes) / len(likes)
    return avg_likes

# Create a function to get the average number of retweets
def get_average_retweets(tweets: list) -> float:
    """Returns the average number of retweets.

    Args:
        tweets (list): List of tweets.

    Returns:
        float: Average number of retweets.
    """
    retweets = [tweet.retweet_count for tweet in tweets]
    avg_retweets = sum(retweets) / len(retweets)
    return avg_retweets

# Create a /search route found in tweets.html
@app.route("/search", methods=["POST"])
def search():
    username = request.form.get("username", "")
    tweets = get_tweets(api_model, username)
    avg_length = get_average_length(tweets)
    avg_likes = get_average_likes(tweets)
    avg_retweets = get_average_retweets(tweets)
    return render_template("tweets.html", tweets=tweets, avg_length=avg_length, avg_likes=avg_likes, avg_retweets=avg_retweets)

if __name__ == '__main__':
    app.run(debug=True)
