# askso

实现命令行方式查询StackOverFlow。调用 StackExchange API 搜索关键字，返回StackOverFlow上相关度最高的提问列表及回答（按投票排序）。

---

# 效果
![](https://raw.githubusercontent.com/Kunkgg/askso/master/askso_test.gif)
---

# 安装

1. 克隆github仓库: `git clone `
2. 安装：`python setup.py install`

---

# 使用
- 命令行非常简单
```
Usage: askso.py [OPTIONS] KEYWORDS

Options:
  --searchlistsize INTEGER  搜索多少个与关键字相关性最高的提问，default=10
  --queslistsize INTEGER    显示多少个与关键字相关性最高的提问，default=10
  --answerlistsize INTEGER  解析关于某个提问投票得分前多少名的回答，default=5
  --help                    Show this message and exit.
```

- **举例**
搜索关键字python decorator,在命令行输入: `askso "python decorator"`即可

---

# 参考
- [Stack Exchange API](http://api.stackexchange.com/docs)
- github:[gautamkrishnar/socli](https://github.com/gautamkrishnar/socli)
- github:[gleitz/howdoi](https://github.com/gleitz/howdoi)
