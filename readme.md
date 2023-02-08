# 计算机论文爬取

从dblp上根据**年份**、**会议/期刊名称**、**关键词**爬取会议及期刊论文

## Requirements

```text
lxml==4.9.2
requests==2.25.1
tqdm==4.62.3
```

## 使用

### 第一步：安装依赖

```shell
pip install -r requirements.txt
```

### 第二步：main.py

```python
python main.py -t 2022 -k edge_computing
```

* "-t" or --time" 期刊/会议年份.
* "-k" or "--keyword" 关键词，空格用下划线_代替.
* "--save_dir" 保存目录.
* 保存的条目有：标题、作者、链接
