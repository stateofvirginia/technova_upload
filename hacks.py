import nltk
import json
from random import shuffle
import requests
import os

#add access token here
token=""

def create_url_for_userID(userName):
    # Specify the usernames that you want to lookup below
    # You can enter up to 100 comma-separated values.
    user_fields = "user.fields=description,created_at"
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
    url = "https://api.twitter.com/2/users/by/username/{}?{}".format(userName, user_fields)
    return url

def create_url_for_timeline(id,tweetNum,nextToken):
    if nextToken:
        url = "https://api.twitter.com/2/users/{}/tweets?max_results={}&pagination_token={}".format(id,tweetNum,nextToken)
    else:
        url = "https://api.twitter.com/2/users/{}/tweets?max_results={}".format(id,tweetNum)
    return url

def is_positive(tweet: str) -> bool:
    """True if tweet has positive compound sentiment, False otherwise."""
    # print(sia.polarity_scores(tweet)["compound"])
    return sia.polarity_scores(tweet)["compound"] > 0

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r

def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth,)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def gatherStats(data,tweetNum):

    feetList = []
    allFeet = []
    for i in range(tweetNum):
        tweetTxt = data["data"][i]["text"]
        feetList.append(tweetTxt)
        allFeet = allFeet + tweetTxt.split()

    firstfeet=feetList[0]

    stopwords = nltk.corpus.stopwords.words("english")
    stopwords.append("rt")
    stopwords.append("&amp;")
    words = [w for w in firstfeet if w.lower() not in stopwords]

    #for all feet!!!!
    allWords = [w for w in allFeet if w.lower() not in stopwords]
    #remove all mentions
    allWords = [w for w in allWords if "@" not in w.lower()]

    # print(allWords)
    lower_fd = nltk.FreqDist([w.lower() for w in allWords])

    lower_fd.most_common(3)
    lower_fd.tabulate(3)

    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    shuffle(feetList)

    totalScore = 0
    avgScore = 0

    for i in range(tweetNum):
        tweetScore = sia.polarity_scores(feetList[i])
        totalScore = totalScore + tweetScore["compound"]

    avgScore = totalScore/tweetNum
    print("Average Score is", avgScore)
    return

def timelineCreate(person, tweetNum):
    resultsFetched=0
    nextToken=""
    allResponses={"data":[]}
    id_url= create_url_for_userID(person)
    userResponse = connect_to_endpoint(id_url)
    id=userResponse["data"]["id"]

    while resultsFetched < 150:
        timeline_url=create_url_for_timeline(id,tweetNum,nextToken)
        timelineResponse = connect_to_endpoint(timeline_url)
        nextToken=timelineResponse["meta"]["next_token"]
        resultsFetched = resultsFetched + timelineResponse["meta"]["result_count"]
        allResponses["data"].extend(timelineResponse["data"])
        if not nextToken:
            return timelineResponse
    return timelineResponse

tweetNum = 80 
persons = ["cherryqian06","benshapiro","ddlovato","heralen"]
# persons = ["cherryqian06"]

for person in persons:
    print(person)
    timelineResponse = timelineCreate(person, tweetNum)
    tweetsLoaded =len(timelineResponse["data"])
    print("using {} tweets:".format(tweetsLoaded))
    gatherStats(timelineResponse,tweetsLoaded)

