import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# 配置浏览器选项
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 无头模式
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# 初始化浏览器
driver = webdriver.Chrome(options=options)


def login_overton(driver):
    # 第一步：输入邮箱
    driver.get("https://app.overton.io/ui/auth/login")

    # 输入邮箱（更稳定的定位方式）
    email_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='eg. user@institution.co']"))
    )
    email_input.send_keys("24110170045@m.fudan.edu.cn")

    # 点击Next按钮
    next_button = driver.find_element(By.XPATH, "//button[contains(.,'Next')]")
    next_button.click()

    # 第二步：输入密码（关键修改部分）
    # 使用XPath精准定位密码输入框
    password_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
    )
    password_input.send_keys("heyunfan410803")

    # 点击登录按钮
    login_button = driver.find_element(By.XPATH, "//button[contains(.,'Log in')]")
    login_button.click()

    # 验证登录成功
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//header[contains(@class,'app-header')]"))
    )
    print("登录成功！")

# 数据提取函数
def extract_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # 更健壮的长摘要提取（增加容错处理）
    long_abstract = ""
    try:
        description_sections = soup.find_all("div", class_="document_description--section")
        for section in description_sections:
            title = section.find("h4", class_="document_description--section-title")
            if title and "Document description" in title.text:
                long_abstract = section.get_text(strip=True).replace("Document description", "").strip()
                break
    except Exception as e:
        print(f"长摘要提取失败: {str(e)}")

    # 更稳定的短摘要提取
    short_abstract = ""
    try:
        snippet = soup.find("div", {"data-name": "snippet"})  # 使用属性选择器
        if snippet:
            short_abstract = snippet.get_text(strip=True)
    except Exception as e:
        print(f"短摘要提取失败: {str(e)}")

    # 改进关键词提取逻辑
    keywords = []
    try:
        tags_div = soup.find("div", class_="tags")
        if tags_div:
            keywords = [a.get_text(strip=True) for a in tags_div.find_all("a") if a.get_text(strip=True)]
    except Exception as e:
        print(f"关键词提取失败: {str(e)}")

    return {
        "long_abstract": long_abstract,
        "short_abstract": short_abstract,
        "keywords": "; ".join(keywords) if keywords else ""
    }

# 主程序
def main():
    try:
        login_overton(driver)
        df = pd.read_csv("E:\input.csv",encoding='gbk')
        results = []

        for index, row in df.iterrows():
            doc_id = row['Policy_document_id']
            url = row['Overton URL']
            print(f"\n处理文档 {index + 1}/{len(df)}: {doc_id}")

            try:
                # 更健壮的页面加载机制
                driver.get(url)
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )

                # 动态等待关键元素加载
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".document_description--section, .editable.snippet, .tags"))
                )

                # 添加重试机制
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        data = extract_data(driver.page_source)
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"第{attempt + 1}次提取失败，重新尝试...")
                            time.sleep(3)
                            continue
                        else:
                            raise e

                data.update({"Policy_document_id": doc_id, "URL": url})
                results.append(data)
                print("√ 抓取成功")

                # 智能等待策略
                time.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f"× 处理失败: {str(e)}")
                # 保存错误页面供调试
                with open(f"error_{doc_id}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                driver.save_screenshot(f"error_{doc_id}.png")
                results.append({
                    "Policy_document_id": doc_id,
                    "URL": url,
                    "long_abstract": "ERROR",
                    "short_abstract": "ERROR",
                    "keywords": "ERROR"
                })
                continue

        result_df = pd.DataFrame(results)
        result_df.to_csv("E:\overton_results.csv", index=False)
        print("\n完成！错误文档已标记为ERROR")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()