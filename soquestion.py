import requests
import re
import time
from sqlite3 import dbapi2 as sqlite
import sys
from multiprocessing import Pool, freeze_support


def get_account_code(account):
    accounturl = requests.get('https://instagram.com/' + account)
    try:
        accountid = re.search(r"(?:\"owner\": \{\"id\": \")([0-9]+)(?:\")", accounturl.text).group(1)
        return accountid
    except AttributeError:
        display(account + "'s account is fucked, check it brosskkiiiiiiiiiiiiiiiiiiiiiiiiIIIIIIIIIIIIIIIii")
        return False

def check_account(account, request):
    global username_global
    account_url = instagram_session.get("https://instagram.com/{}".format(account))
    check = html_checks(account_url, account)
    display(username_global + " Already Followed " + account if request=="follow" and check=="true" else username_global + " Isn't Following" + account if request=="unfollow" and check=="false" else None)
    return True if request=="follow" and check=="false" or request=="unfollow" and check =="true" else False


def html_checks(url_text, account=None):
    try:
        re.search(r"(Sorry\, this page isn\&\#39\;t available.)",
            url_text.text).group(1)
        display(account + "'S ACCOUNT WAS DELETED")
        followed = None
    except AttributeError:
        try:
            private = re.search(r"(?:\"is_private\"\: )([a-z]+)", url_text.text).group(1)
            if private == "true":
                display(account + "'S ACCOUNT IS PRIVATE")
            else:
                if int(re.search(r"(?:\"followed_by\"\: \{\"count\"\: )([0-9]+)", url_text.text).group(1)) > threshold:
                    followed = re.search(r"(?:\"followed\_by\_viewer\"\: )([a-z]+)", url_text.text).group(1)
                    return followed
                else: 
                    display(account + " is below threshold") if account != None else display("Account is below threshold")
        except TypeError:
            return None
        except AttributeError:
            return None


def display(string):
    if string != None:
        hyphons = 100 - len(string)
        print(("-" * int(hyphons//2)) + string.upper() + ("-" * int(hyphons//2)))
        sys.stdout.flush()


def check_health(start=False):
    global last_check, switch

    follows_url = requests.get("http://instagram.com/{}".format(username_global))
    follows = re.search(r"(?:\"follows\"\: \{\"count\"\: )([0-9]+)", follows_url.text).group(1)
    if start==False:
        succesful_changes = abs(int(last_check) - int(follows))
        if succesful_changes < 50:
            display("Only " + succesful_changes + " went through")
    last_check = follows
    print(last_check)


def get_insta_session(user, secret):
    s = requests.Session()
    s.get('https://www.instagram.com/')
    csrf = s.cookies['csrftoken']

    before_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'referer': 'https://www.instagram.com/',
        'cookie': ("csrftoken=" + csrf),
        'x-csrftoken': (csrf),
    }

    data = 'username={}&password={}'.format(user, secret)

    s.post('https://www.instagram.com/accounts/login/ajax/', headers=before_headers , data=data)
    return s


def instagram_login(session, login_url, csrf_token, username, password):
    data = {
        "csrfmiddlewaretoken": csrf_token,
        "username": username,
        "password": password}

    redirects = send_insta_post_req(session, login_url, data)
    login_failed = re.search(
        'id="login\\-form".*?action="(.+?)"', redirects.text)
    if login_failed:
        print("Instagram Login Failed, Username or Password is wrong, both fields are case-sensitive.")
        sys.stdout.flush()

    return redirects

def send_insta_post_req(session, login_url, data):
    headers = {
        "referer": ("https://www.instagram.com" + login_url),
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"
    }
    redirects = session.post(("https://www.instagram.com" + login_url),
                             data=data,
                             headers=headers,
                             allow_redirects=True)
    return redirects

def get_pikore_session(user, secret):
    session = requests.Session()
    session.get('http://pikore.com')
    redirects = session.get('http://pikore.com/session/new?from=/', allow_redirects=True)
    auth_url = str(redirects.history[-1].url)
    token_access = session.get(auth_url)
    login_required = re.search('id="login\\-form".*?action="(.+?)"', token_access.text)
    if login_required:
        middleware_token = re.search('csrfmiddlewaretoken.*?value="(.+?)"', token_access.text)
        login_url = login_required.group(1)
        csrf_token = middleware_token.group(1)
        token_access = instagram_login(session, login_url, csrf_token, user, secret)
    session.headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"
    return session

def send_insta_request(account, account_code, request): 
    global start_time, sent_counter, username_global
    try: 
        instagram_session.headers['referer'] = 'https://www.instagram.com/{}/'.format(account)
        instagram_session.headers['x-csrftoken'] = instagram_session.cookies['csrftoken']
        request_send = instagram_session.post('https://www.instagram.com/web/friendships/{}/{}/'.format(account_code, request))
        
        display(username_global + "'s account " + 'succesfully ' + request + 'ed' +  ' With ' + ("Instagram - " if switch==0 else "Pikore - ") + account + " " + str(db_user_list.index(account)) + "/" + str(len(db_user_list)) + " - " + str(sent_counter) + " sent")
        sent_counter += 1
        display("Sleeping " + str((30 + start_time) - time.time()) + " seconds")
        time.sleep((32 + start_time) - time.time())

    except TypeError:
        print("TypeError")
        sys.stdout.flush()
        time.sleep(60)
    #check_post(account, request)

def send_pikore_request(account, account_code, request):
    global start_time, sent_counter, username_global
    try:
        request_sent = pikore_session.get('http://www.pikore.com/{}/{}'.format(request, account_code))

        display(username_global + "'s account " + 'succesfully ' + request + 'ed' +  ' With ' + ("Instagram - " if switch==0 else "Pikore - ") + account + " " + str(db_user_list.index(account)) + "/" + str(len(db_user_list)) + " - " + str(sent_counter) + " sent")
        sent_counter += 1
        display("Sleeping " + str((30 + start_time) - time.time()) + " seconds")
        time.sleep((32 + start_time) - time.time())
    except TypeError:
        print("TypeError")
        sys.stdout.flush()
        time.sleep(60)
    #check_post(account, request)

def check_success(account, request):
    account_html = requests.get("https://instagram.com/{}".format(account), headers=headers, cookies=cookies)
    relation_status = re.search(r"(?:\"followed\_by\_viewer\"\: )([a-z]+)", account_html.text).group(1)
    print("Success" if (request=="follow" and relation_status=="true") or (request=="unfollow" and relation_status=="false") else "Failure")
    sys.stdout.flush()

def run(username, secret, request, start_pos, origon, threshold_global, switch_param):
    global instagram_session, pikore_session, sent_counter, db_user_list, switch, threshold, start_time, username_global
    threshold = threshold_global
    switch = switch_param
    username_global = username

    instagram_session = get_insta_session(username, secret)
    pikore_session = get_pikore_session(username, secret)
    sessions = [instagram_session, pikore_session]

    connection = sqlite.connect('scrapedata.db')
    cursor = connection.cursor()
    cursor.execute('SELECT username FROM accounts WHERE origin = ? AND followers > ?', [origon, threshold])
    db_user_list = [a[0] for a in cursor.fetchall()]

    check_health(start=True)
    sent_counter = 1
    while True:
        for account in db_user_list[start_pos::]:
            if sent_counter % 60 == 0:
                switch = 1 if (sent_counter / 60) % 2 == 0 else 0
                display("Switching to Pikore" if switch==0 else "Switching to Instagram")
                check_health()
                if switch == 0:
                    switch = 1 
                else:
                    switch = 0
                sent_counter += 1
            else:
                start_time = time.time()
                if check_account(account, request):
                    send_insta_request(account, get_account_code(account), request) if switch == 0 else send_pikore_request(account, get_account_code(account), request)
                else:
                    display("Sleeping 7 Seconds")
                    time.sleep(7)

        if request == "follow":
            request = "unfollow" 
        else:
             request = "follow"
        start_pos=0

if __name__ == "__main__":
    freeze_support()

    #(username, secret, request, start_pos, origon, threshold_global, switch_param)


    account1 = (username, secret, request, start_pos, origon, threshold_global, switch_param)
    account2 = (username, secret, request, start_pos, origon, threshold_global, switch_param)
    account3 = (username, secret, request, start_pos, origon, threshold_global, switch_param)

    accounter = [account1,account2,account3]
    with Pool() as pool:
        pool.starmap(run, accounts)