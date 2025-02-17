import os
import sys
import argparse
import asyncio
# 获取当前文件的父目录的父目录（即项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到系统路径
sys.path.append(project_root)
from src.logger import logger
from src.config import Config
from src.logger import logger
from src.agents.pubmed_assistant import PubMedAssistant
 
async def async_main():
    parser = argparse.ArgumentParser(description='Search PubMed using dictionary parameters.')
    parser.add_argument('--journal', type=str, help='Journal name')
    parser.add_argument('--author1', type=str, help='First author')
    parser.add_argument('--year', type=str, help='Year of publication')
    parser.add_argument('--keyword', type=str, help='Keyword')
    parser.add_argument('--query', type=str, help='Traditional PubMed query string')
    parser.add_argument('--topk', type=int, default=10, help='Number of results to return')
    args = parser.parse_args()

    config = Config(config_file="./config.yaml")
    agent = PubMedAssistant(name="PubMedAssistant", config=config)

    params = {}
    if args.journal:
        params['journal'] = args.journal
    if args.author1:
        params['first author'] = args.author1
    if args.year:
        params['year'] = args.year
    if args.keyword:
        params['keyword'] = args.keyword

    try:
        # 优先使用query参数，如果不存在则使用参数字典
        if args.query:
            results = await agent.search_pubmed(query=args.query, topk=args.topk)
            logger.info(f"使用查询字符串搜索结果: {results}")
        elif params:
            results = await agent.search_pubmed(**params, topk=args.topk)
            logger.info(f"使用参数字典搜索结果: {results}")
        else:
            logger.warning("未提供任何搜索参数")
            return

        if results:
            # 统一使用并发获取详细信息
            tasks = [agent.get_article_details(pmid) for pmid in results]
            details = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 添加结果输出
            success_count = 0
            for pmid, detail in zip(results, details):
                if isinstance(detail, Exception):
                    logger.error(f"PMID {pmid} 详情获取失败: {str(detail)}")
                else:
                    success_count += 1
                    logger.info(f"详细信息 PMID {pmid}: {detail}")
                    # 添加控制台输出
                    print(f"\nPMID: {pmid}")
                    print(f"标题: {detail.get('title', '无')}")
                    print(f"摘要: {detail.get('abstract', '无')[:200]}...")
            
            print(f"\n成功获取 {success_count}/{len(results)} 篇文献的详细信息")

    except Exception as e:
        logger.error(f"搜索过程中发生错误: {str(e)}")

def main():
    # 修改为运行参数解析函数
    asyncio.run(async_main())

if __name__ == "__main__":
    main()