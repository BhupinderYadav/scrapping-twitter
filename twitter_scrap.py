from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
from access_google_api import access_google_api
import datetime

############# accessing google api to read the keyword #############

api = access_google_api(cred_path='google_api_cred.json')
data_read_access = api.access(worksheet='hash_tags', spread_sheet_name='scrap_proj')

search_key = api.spread_sheet_reader(read_range_start='A1', read_range_finsh='A4')

######################################################################

counter = 0

while (counter < len(search_key)):

    # invoking chrome driver
    driver = webdriver.Chrome()

    # url building

    base_url = u'https://twitter.com/search?q='
    query = str(search_key[counter])
    url = base_url + str(query.upper()) + r'&src=typd'

    # invoking driver and extracting body of the loaded page
    driver.get(url)
    body = driver.find_element_by_tag_name('body')


    # scrolling the loaded page
    for _ in range(1):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)

    time.sleep(60)


    # passing the full length html in to beautiful soup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # print(soup.prettify())

    # creating a empty panda data frame
    df_twitter = pd.DataFrame({'time_stamp': [], 'username': [], 'tweet_text': [], \
                               're_tweets': [], 'likes': []})

    # Extract information from url using bs4 methods
    for t in soup.find_all('div', {'class': 'content'}):

        # finding timestamp
        try:
            time_stamp = t.find('a', {'class': 'tweet-timestamp'})['title']
        except KeyError:
            print('key error')
            time_stamp = 'un_retrivalble'

        # finding username
        username = t.find('span', {'class': 'username'}).find('b').text

        # finding tweet
        try:
            tweet_text = t.find('p', {'class': 'TweetTextSize'}).text
        except:
            pass

            # handling comments

        # commnet_count = t.find('span', {'class': 'ProfileTweet-actionCountForPresentation'}).find('span', \
                                                 #{'class':'ProfileTweet-action--reply'}).find('span',{'class': 'ProfileTweet-actionCountForAria'}).content

        # handling the count data
        thumbs = t.find_all('span', {'class': 'ProfileTweet-actionCountForPresentation'})
        try:
            re_tweets = thumbs[0].text

            # handling the tweets number if its in thousands
            if re_tweets[-1] == 'K':
                re_tweets = int(float(re_tweets[:-1]) * 1000)
            else:
                re_tweets = int(float(re_tweets))

            if len(re_tweets) == 0:
                re_tweets = int(0)

        except:
            pass

       # counting likes
        try:
            likes = thumbs[2].text
            if likes[-1] == 'K':
                likes = int(float(likes[:-1]) * 1000)
            else:
                likes = int(float(likes))

            if len(likes) == 0:
                likes = int(0)

        except:
            pass

        # passing the extracted data into the dictionary used to build panda data frame
        entry = {'time_stamp': str(time_stamp), 'username': [str(username)], 'tweet_text': str(tweet_text), \
                 're_tweets': re_tweets, 'likes': likes}

        df_twitter = df_twitter.append([pd.DataFrame(entry)], ignore_index=True, sort=False)

        df_twitter = df_twitter.sort_values(by=['re_tweets', 'likes'], ascending=False)

    # print(datetime.datetime.now())
    # print('dataframe ended')
    #
    # closing the selenium web driver
    driver.close()

    ############ writing back to google spread sheet##################

    api_writer = access_google_api(cred_path='google_api_cred.json', worksheet='facebook_scrap',
                                   spread_sheet_name='scrap_proj')
    data_writer = api_writer.spread_sheet_writer(df_twitter)

    ####################################################################

    # temp files for to monitor the status

    temp_file_name = 'temp_' + str(search_key[counter]) + '.csv'
    try:

        df_twitter.to_csv(temp_file_name)

    except:
        print('issue with file')

    print('scrapped ' + str(counter + 1) + ' item')

    counter = counter + 1

print('sucsses : all item searched successfuly')