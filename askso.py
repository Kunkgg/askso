import os
import sys
import random
import logging
from datetime import date
import textwrap
import re
import unicodedata

from lxml import html
import requests
import click

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

logging.basicConfig(
                format='%(asctime)s - %(levelname)s - %(message)s',
                filename='log',
                level=logging.INFO
                            )

API_STACKEXCHANGE_SEARCH = 'http://api.stackexchange.com/2.2/search/advanced'
SITE ='stackoverflow'
stackoverflow_session = requests.session()
terminal_size = os.get_terminal_size()
text_width = int(terminal_size.columns*0.8)
text_heigh = int(terminal_size.lines*0.9)
#查找可能是代码的字符串，一合适的方式打印
code_pattern = re.compile(r'\n[ ]{4,}')
#生成translate字典,用于清理文本
cmb_chrs = dict.fromkeys(
    c for c in range(sys.maxunicode) if unicodedata.combining(chr(c))
                        )

def cleantext(text):
     text = unicodedata.normalize('NFD',text)
     text = text.translate(cmb_chrs)
     return text

def get_html(url,params=None):
    try:
        res = stackoverflow_session.get(
                                url,
                                params=params,
                                headers={'User-Agent':random.choice(user_agent)})
        res.raise_for_status()
    except requests.exceptions.Timeout:
        logging.error("**requests请求超时**")
    except Exception:
        logging.error("**requests请求失败**")
    else:
        return res

def search_question(keywords,url=API_STACKEXCHANGE_SEARCH,search_list_size=10,
                    sort_method='relevance',site=SITE):
    """
    sort_method:
    按相关度排序 relevance
    按最新回答时间排序 creation
    按投票数排序 votes
    按活跃程度排序 activity
    """
    params = {
            'page':1,
            'pagesize':search_list_size,
            'order':'desc',
            'sort':sort_method,
            'q':keywords,
            'closed':False,
            'site':site
            }
    logging.info('Search Keywords:{}'.format(keywords))
    res = get_html(url,params=params)
    return res.json()

def get_questions_infos(search_res):
    questions_infos = search_res.get('items')
    if questions_infos:
        return questions_infos
    else:
        logging.info("**没有找到相关的问题结果**")

def display_questions_info(questions_infos,display_limit=10):
    print("\u2605"*text_width)
    print(
    "The Top {} Similar Questions From Site:{}.".format(len(questions_infos),SITE)
        )
    print("Questions information is following:")
    title_width = text_width*0.8 - 36
    template_title = '|{0:^6}|{1:^' + str(title_width) + '}|{2:^10}|{3:^10}|{4:^10}|{5:^10}|'
    template_line = '|{0:^6}|{1:<' + str(title_width) + '}|{2:^10}|{3:^10}|{4:^10}|{5:^10}|'
    print("-"*text_width + '\n')
    print(template_title.format('Num','Title','Score','Viewed','Answered','Creation_Date'))
    display_questions = (questions_infos if len(questions_infos) <= display_limit
                                            else questions_infos[:display_limit])
    num = 0
    for question in display_questions:
        num += 1
        creation_date = date.fromtimestamp(question.get('creation_date')).isoformat()
        print("-"*text_width)
        print(template_line.format(
                            num,
                            question.get('title'),
                            question.get('score'),
                            question.get('view_count'),
                            question.get('answer_count'),
                            creation_date
                            )
            )
        print("\u2605 link:",question.get('link'))

def choice_question():
    while True:
        num = input('输入提问编号(1-10),查看对应回答;输入q退出:')
        if num == 'q':
            print('退出...')
            break
        else:
            try:
                if 1 <= int(num) <= 10:
                    return int(num)
                else:
                    print('输入有误，请重新输入！')
            except:
                print('输入有误，请重新输入！')

def get_question_link(questions_infos,choice_question_num):
    question_link = questions_infos[choice_question_num-1].get('link')
    if question_link:
        return question_link
    else:
        logging.info('查询失败')

def get_question_html(question_link):
    question_html = get_html(question_link).content
    if question_html:
        return question_html
    else:
        logging.info('查询失败')

def get_answers(question_html,answer_limit=5):
    tree = html.fromstring(question_html)
    answer_div_elements = tree.xpath(
        '//div[@class="answer" or @class="answer accepted-answer"]//div[@class="post-text"]'
        )
    answer_div_elements = (answer_div_elements if len(answer_div_elements) <= answer_limit
                                            else answer_div_elements[:answer_limit])
    return [get_one_answer(answer_div) for answer_div in answer_div_elements]

def get_one_answer(answer_div):
    try:
        answer_text = ''.join(answer_div.xpath('.//text()'))
    except Exception:
        logging.info('查询失败')
        return False
    try:
        a_link_elements = answer_div.xpath('.//a[@href]')
        if a_link_elements:
            a_link = [(a.text,a.get('href')) for a in a_link_elements]
        else:
            a_link = []
    except:
        a_link = []
    try:
        code_elements = answer_div.xpath('.//code')
        if code_elements:
            code = [code.text for code in code_elements]
        else:
            code = []
    except:
        code = []
    return {
            'answer_text':answer_text,
            'a_link':a_link,
            'code':code
            }

def print_one_answer(one_answer):
    answer_text = cleantext(one_answer.get('answer_text').strip())
    a_link = one_answer.get('a_link')
    code = [cleantext(c) for c in one_answer.get('code')]
    if answer_text:
        print("-"*text_width + '\n')
        print("\u2605"*10 + "Text In The Answer:")
        for line in answer_text.split('\n\n'):
            if code_pattern.search(line):
                print(line+'\n')
            elif len(line) > text_width:
                print(textwrap.fill(line+'\n',text_width))
            else:
                print(line+'\n')
        print("-"*text_width + '\n\n')
    while True:
        if a_link:
            print(
                '该Answer中包含{}条链接，输入a查看链接详情:'
                .format(len(a_link))
                )
        if code:
            print(
                '该Answer中包含{}个代码块，输入c查看代码块详情:'
                .format(len(code))
                )
        control = input('如不需要查看链接和代码块详情，按其他任意键继续:')
        if control == ('a' or 'A'):
            print("-"*text_width + '\n')
            print("\u2605"*10 + "Link In The Answer:")
            for n,link in  enumerate(a_link):
                print("\u2605"*3 + "{}.{}:{}".format(n+1,link[0],link[1]))
            print("-"*text_width + '\n\n')
        elif control == ('c' or 'C'):
            print("-"*text_width + '\n')
            print("\u2605"*10 + "CodeBlock In The Answer:")
            for n,code in  enumerate(code):
                print("\u2605"*3 + "CodeBlock:{}\n{}".format(n+1,code))
                print("-"*text_width + '\n')
            print("-"*text_width + '\n\n')
        else:
            break
    print('该Answer显示完毕')

def output_answers(answers):
    i = 0
    while True:
        one_answer = answers[i]
        print("\u2605"*40 + "The Answer {}".format(i+1) + "\u2605"*40)
        print_one_answer(one_answer)
        while True:
            if i == 0:
                gotowhere = input("这是第一个Answer,输入n查看下一Answer,输入q退出,输入r返回提问选择:")
            elif 0 < i < len(answers)-1:
                gotowhere = input("输入n查看下一Answer,输入p查看上一Answer,输入q退出,输入r返回提问选择:")
            elif i == len(answers)-1:
                gotowhere = input("所有Answer已打印完毕,输入p查看上一Answer,输入q退出,输入r返回提问选择:")
            else:
                logging.error("Answer队列出错")

            if gotowhere == ('n' or 'N'):
                i += 1
                break
            elif gotowhere == ('p' or 'P'):
                i -= 1
                break
            elif gotowhere == ('q' or 'Q'):
                print("退出...再见:)")
                return None
            elif gotowhere == ('r' or 'R'):
                print("返回提问选择...")
                return "Trun Back Questions List"
            else:
                continue

@click.command()
@click.option('--searchlistsize',default=10,help='搜索多少个与关键字相关性最高的提问，default=10')
@click.option('--queslistsize',default=10,help='显示多少个与关键字相关性最高的提问，default=5')
@click.option('--answerlistsize',default=5,help='显示关于某个提问投票得分前多少名的回答，default=5')
@click.argument('keywords')
def cli_runner(searchlistsize,queslistsize,answerlistsize,keywords):
    """命令行查询stackoverflow"""
    questions_infos = get_questions_infos(
                search_question(
                        keywords,
                        search_list_size=searchlistsize
                        )
                                    )
    while True:
        display_questions_info(questions_infos,display_limit=queslistsize)
        choice_question_num = choice_question()
        if choice_question_num:
            question_link = get_question_link(questions_infos,choice_question_num)
            question_html = get_question_html(question_link)
            answers = get_answers(question_html,answer_limit=answerlistsize)
            if output_answers(answers):
                continue
            else:
                break
        else:
            break
    stackoverflow_session.close()

if __name__ == '__main__':
    cli_runner()
