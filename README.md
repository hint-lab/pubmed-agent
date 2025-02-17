# PubMed文献助手

## 项目描述

中文：PubMed文献助手是一个基于Python开发的文献搜索与处理工具，旨在帮助科研人员更高效地获取和处理PubMed数据库中的学术文献。该项目提供了文献搜索、详情获取、自动翻译和PDF下载等功能，并支持通过命令行和API两种方式使用。通过简单的配置，用户可以快速搭建自己的文献搜索系统，实现自动化文献处理流程。

## 功能

- 搜索文献
- 获取文献详情
- 翻译文献
- 下载文献PDF

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python src/main.py --query "leukemia [AND] bronchiolitis obliterans"
```

## 配置

```bash
cp config.yaml.example config.yaml
```

## API部署

```bash
python src/api_server.py
```

## 测试 

```bash
python test/test_search_metapub.py --query "leukemia [AND] bronchiolitis obliterans"
```

