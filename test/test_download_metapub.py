from metapub import PubMedFetcher,CrossRefFetcher
import time
import requests
from metapub import FindIt
import socket
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager



def setup_logging():
    hostname = socket.gethostname()
    pid = os.getpid()
    
    log_format = f'%(asctime)s {hostname} %(module)s[{pid}] %(levelname)s %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 创建一个名为 'download_pdf' 的日志记录器
    logger = logging.getLogger('download_pdf')
    return logger

# 初始化日志
log = setup_logging()

def init_selenium():
    # 设置 Chrome 选项
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--disable-gpu')  # 禁用 GPU 加速
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # 模拟浏览器
    
    # 添加自定义请求头
    options.add_experimental_option('prefs', {
        'profile.default_content_settings.pdf': 2,
        'download.prompt_for_download': False,
        'download.default_directory': os.getcwd(),
    })
    
    # 添加额外的请求头
    options.add_argument('--disable-blink-features=AutomationControlled')

    # 使用 webdriver-manager 获取最新的 ChromeDriver
    service = Service(ChromeDriverManager().install())
    log.info(f"Initailizing ChromeService{service}")
    # 启动 Chrome 浏览器
    driver = webdriver.Chrome(service=service, options=options)
    log.info(f"Initailizing ChromeDriver{driver}")
    return driver

def call_selenium_pass_cloudflare(driver: webdriver.Chrome, url:str):
    try:
        # 打开网页
        driver.get(url)
        time.sleep(5)  # 增加等待时间
        
        # 获取页面源代码
        page_source = driver.page_source
        
        # 如果是PDF文件，应该直接下载而不是获取页面源代码
        if url.lower().endswith('.pdf'):
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/pdf',
                'Content-Type': 'application/pdf'
            })
            if response.status_code == 200:
                return response.content
            
        log.info(f"Page source: {page_source[:200]}...")  # 记录页面源码的前200个字符
        return None
    except Exception as e:
        log.error(f"浏览器打开{url}时发生错误: {str(e)}")
        return None

def close_selenium(driver):  
    # 确保浏览器被关闭
    if 'driver' in locals():
        try:
            driver.quit()
        except Exception as e:
            print(f"关闭浏览器时发生错误: {str(e)}")

def PubMedArticle2doi(pma):
    '''Starting with a PubMedArticle object, use CrossRef to find a DOI for given article.

    Args:
        pma (PubMedArticle)

    Returns:
        doi (str) or None
    '''
    cr_fetch = CrossRefFetcher()
    try:
        # 获取CrossRef结果
        results = cr_fetch.cr.works(
            query_bibliographic=pma.title, 
            query_container_title=pma.journal, 
            limit=5
        )
        
        if results and 'message' in results and 'items' in results['message']:
            # 获取第一个匹配结果
            items = results['message']['items']
            if items:
                work = items[0]  # 取第一个结果
                doi = work.get('DOI')
                log.info(f'CrossRefWork found DOI: {doi}')
                
                # 尝试获取PDF URL
                if 'link' in work:
                    links = work['link']
                    for link in links:
                        if isinstance(link, dict):
                            url = link.get('URL', '')
                            content_type = link.get('content-type', '')
                            if content_type == 'application/pdf' or url.lower().endswith('.pdf'):
                                return doi, url
                    # 如果没有找到PDF链接，返回第一个链接
                    if links and isinstance(links[0], dict):
                        return doi, links[0].get('URL')
                
                return doi, None
                
    except Exception as e:
        log.error(f"CrossRef查询失败: {str(e)}")
    return None, None

def convert_pmid_to_doi(pmid):
    pm_fetch = PubMedFetcher()
    pma = pm_fetch.article_by_pmid(pmid)
    # if pma.doi:
    #     log.info('PMID %s: Found DOI in MedLine XML.', pma.doi)
    #     log.info('PMID %s: Found URL in MedLine XML.', pma.url)
    #     return pma.doi
    return PubMedArticle2doi(pma)

def get_pdf_url_by_pmid(pmid, max_retries=3):
    for attempt in range(max_retries):
        try:
            src = FindIt(pmid)
            if src.url is not None:
                return src.url
            
            doi, url = convert_pmid_to_doi(pmid)
            log.info(f"doi: {doi}")
            log.info(f"url: {url}")
            if url is not None:
                return url
                
        except Exception as e:
            log.warning(f"第{attempt + 1}次尝试失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))  # 递增等待时间
                continue
            log.error(f"获取PDF URL失败，已重试{max_retries}次")
    return None

def download_article_pdfs(pmid_list, download_dir, driver):
    fetch = PubMedFetcher()
    for pmid in pmid_list:
        try:
            article = fetch.article_by_pmid(pmid)
            log.info(f"article: {article}")

            pdf_url = get_pdf_url_by_pmid(pmid)
            log.info(f"pdf_url: {pdf_url}")
            if pdf_url:
                try:
                    pdf_content = call_selenium_pass_cloudflare(driver, pdf_url)
                    if pdf_content:
                        os.makedirs(download_dir, exist_ok=True)
                        with open(f"{download_dir}/{pmid}.pdf", 'wb') as f:
                            f.write(pdf_content)
                        log.info(f"Downloaded PDF for PMID {pmid}")
                    else:
                        log.warning(f"无法获取PDF内容: {pdf_url}")
                    
                    time.sleep(5)
                    
                except Exception as e:
                    log.error(f"下载PDF时发生错误 PMID {pmid}: {e}")
                time.sleep(2)
            else:
                log.info(f"No PDF available for PMID {pmid}")
        except Exception as e:
            log.error(f"处理PMID {pmid}时发生错误: {e}")
            continue

# Example usage
pmid_list = [ '39951613']
download_dir = "./download"
driver=init_selenium()
download_article_pdfs(pmid_list, download_dir, driver)

close_selenium(driver)