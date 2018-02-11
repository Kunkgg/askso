import random

from lxml import html

import requests

#Some User Agents
user_agent=[
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36'
    ]

test_keywords = 'python decorator'

"""
sort_method:
按相关度排序 relevance
按最新回答时间排序 creation
按投票数排序 votes
按活跃程度排序 activity
"""
API_STACKEXCHANGE_SEARCH = 'http://api.stackexchange.com/2.2/search/advanced'
SITE ='stackoverflow'
stackoverflow_session = requests.session()

def get_html(url,params=None):
    try:
        res = stackoverflow_session.get(
                                url,
                                params=params,
                                headers={'User-Agent':random.choice(user_agent)})
        res.raise_for_status()
    except requests.exceptions.Timeout:
        print("**requests请求超时**")
    except Exception:
        print("**requests请求失败**")
    else:
        return res

def search_question(keywords,url=API_STACKEXCHANGE_SEARCH,search_list_size=10,
                    sort_method='relevance',site=SITE):
    params = {
            'page':1,
            'pagesize':search_list_size,
            'order':'desc',
            'sort':sort_method,
            'q':keywords,
            'site':site
            }
    return get_html(url,params=params).json()


def get_questions_infos(search_res):
    questions_infos = search_res.get('items',False)
    if questions_infos:
        return questions_infos
    else:
        print("**没有找到相关的问题结果**")

def display_questions_info(questions_infos,display_limit=5):
    print("\u2605"*100 + '\n\n')
    print(
    "Found {} similar questions from site:{}.".format(len(questions_infos),SITE)
        )
    print("Questions information is following:")
    template_title = '|{0:^6}|{1:<64}|{2:^10}|{3:^10}|{4:^10}|'
    print("-"*100 + '\n')
    print(template_title.format('Num','Title','Score','Viewed','Answered'))
    display_questions = (questions_infos if len(questions_infos) <= display_limit
                                            else questions_infos[:display_limit])
    num = 0
    for question in display_questions:
        num += 1
        print("-"*100)
        print(template_title.format(
                            num,
                            question.get('title'),
                            question.get('score'),
                            question.get('view_count'),
                            question.get('answer_count')
                            )
            )
        print("\u2605 link:",question.get('link'))

def choice_question():
    choice_question_num = input("想看哪个提问的回答？")
    return int(choice_question_num)

def get_question_link(questions_infos,choice_question_num):
    question_link = questions_infos[choice_question_num-1].get('link')
    if question_link:
        return question_link
    else:
        print('查询失败')

def get_question_html(question_link):
    question_html = get_html(question_link).content
    if question_html:
        return question_html
    else:
        print('查询失败')

def get_one_answer(answer_div):
    try:
        answer_text = '>'.join(answer_div.xpath('.//text()'))
    except Exception:
        print('查询失败')
        return False
    try:
        a_link_elements = answer_div.xpath('.//a[@href]')
        if a_link_elements:
            a_link = [a.get('href') for a in a_link_elements]
        else:
            a_link = []
    except:
        a_link = []
    try:
        code_elements = answer_div.xpath('.//code')
        if code_elements:
            code = [code.text for code in code_elements]
            #print("TEST***codeis",code)
        else:
            code = []
    except:
        code = []
    return {
            'answer_text':answer_text,
            'a_link':a_link,
            'code':code
            }

def get_answers(question_html,answer_limit=3):
    tree = html.fromstring(question_html)
    answer_div_elements = tree.xpath(
        '//div[@class="answer" or @class="answer accepted-answer"]//div[@class="post-text"]'
        )
    answer_div_elements = (answer_div_elements if len(answer_div_elements) <= answer_limit
                                            else answer_div_elements[:answer_limit])
    return [get_one_answer(answer_div) for answer_div in answer_div_elements]

def print_one_answer(one_answer):
    if one_answer.get('a_link'):
        print("-"*100 + '\n')
        print("\u2605"*10 + "Link In The Answer:")
        for n,link in  enumerate(one_answer.get('a_link')):
            print("\u2605"*3 + "Link{}:{}".format(n+1,link))
        print("-"*100 + '\n\n')
    if one_answer.get('answer_text'):
        print("-"*100 + '\n')
        print("\u2605"*10 + "Text In The Answer:")
        print(one_answer.get('answer_text'))
        print("-"*100 + '\n\n')
    if one_answer.get('code'):
        print("-"*100 + '\n')
        print("\u2605"*10 + "CodeBlock In The Answer:")
        for n,code in  enumerate(one_answer.get('code')):
            print("\u2605"*3 + "CodeBlock:{}\n{}".format(n+1,code))
            print("-"*100 + '\n')
        print("-"*100 + '\n\n')

def output_answers(answers):
    i = 0
    flag = True
    while flag:
        one_answer = answers[i]
        print("\u2605"*40 + "The Answer {}".format(i+1) + "\u2605"*40)
        print_one_answer(one_answer)
        while True:
            gotowhere = input("输入n查看下一Answer，输入p查看上一Answer,输入q退出:")
            if gotowhere == 'n':
                i += 1
                if i < len(answers):
                    break
                else:
                    print("所有Answer已打印完毕，自动退出程序!")
                    flag = False
                    break
            elif gotowhere == 'p':
                i -= 1
                if i >= 0:
                    break
                else:
                    print("现在已经是第一个Answer了，不能再往前了！")
                    i = 0
                    break
            elif gotowhere == 'q':
                print("退出～")
                flag = False
                break
            else:
                continue

def test_run():
    questions_infos = get_questions_infos(search_question(test_keywords))

    display_questions_info(questions_infos)
    choice_question_num = choice_question()
    question_link = get_question_link(questions_infos,choice_question_num)
    question_html = get_question_html(question_link)
    answers = get_answers(question_html)
    output_answers(answers)
    stackoverflow_session.close()

def get_parser():
    """
    命令行功能实现
    parser = argparse.ArgumentParser(description='instant coding answers via the command line')
    parser.add_argument('query', metavar='QUERY', type=str, nargs='*',
                        help='the question to answer')
    parser.add_argument('-p', '--pos', help='select answer in specified position (default: 1)', default=1, type=int)
    parser.add_argument('-a', '--all', help='display the full text of the answer',
                        action='store_true')
    parser.add_argument('-l', '--link', help='display only the answer link',
                        action='store_true')
    parser.add_argument('-c', '--color', help='enable colorized output',
                        action='store_true')
    parser.add_argument('-n', '--num-answers', help='number of answers to return', default=1, type=int)
    parser.add_argument('-C', '--clear-cache', help='clear the cache',
                        action='store_true')
    parser.add_argument('-v', '--version', help='displays the current version of howdoi',
                        action='store_true')
    return parser
    """
    pass

def command_line_runner():
    """
    命令行执行逻辑
    """
    """
    #解析参数
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return

    if args['clear_cache']:
        _clear_cache()
        print('Cache cleared successfully')
        return
    #如果参数输入为空，打印帮助信息
    if not args['query']:
        parser.print_help()
        return

    # enable the cache if user doesn't want it to be disabled
    if not os.getenv('HOWDOI_DISABLE_CACHE'):
        _enable_cache()

    if os.getenv('HOWDOI_COLORIZE'):
        args['color'] = True
    #调要howdoi函数
    utf8_result = howdoi(args).encode('utf-8', 'ignore')
    if sys.version < '3':
        print(utf8_result)
    else:
        # Write UTF-8 to stdout: https://stackoverflow.com/a/3603160
        sys.stdout.buffer.write(utf8_result)
    # close the session to release connection
    howdoi_session.close()
    """
    pass

if __name__ == '__main__':
    test_run()
