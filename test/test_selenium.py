from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

try:
    # 设置 Chrome 选项
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--disable-gpu')  # 禁用 GPU 加速
    
    # 使用 webdriver-manager 获取最新的 ChromeDriver
    service = Service(ChromeDriverManager().install())
    print(service)
    # 启动 Chrome 浏览器
    driver = webdriver.Chrome(service=service, options=options)
    print(driver)
    # 打开网页
    driver.get("https://www.baidu.com")
    
    # 打印网页标题
    print(driver.title)
    
except Exception as e:
    print(f"发生错误: {str(e)}")
finally:
    # 确保浏览器被关闭
    if 'driver' in locals():
        try:
            driver.quit()
        except Exception as e:
            print(f"关闭浏览器时发生错误: {str(e)}")
