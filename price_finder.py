import time
import random
import pandas as pd
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def fuzzy_match(search_term, title):
    """模糊匹配：所有关键词都出现在标题中即可"""
    keywords = search_term.lower().split()
    return all(k in title.lower() for k in keywords)

def is_similar_enough(a, b, threshold=0.6):
    return similar(a, b) >= threshold

def get_price_from_woolworths(driver, search_term):
    import time, random
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    url = f"https://www.woolworths.com.au/shop/search/products?searchTerm={search_term.replace(' ', '%20')}"
    driver.get(url)
    time.sleep(random.uniform(3, 5))

    try:
        # 等待 wc-product-tile 出现
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "wc-product-tile"))
        )
        tiles = driver.find_elements(By.CSS_SELECTOR, "wc-product-tile")
        print(f"🔍 Woolworths 共找到 {len(tiles)} 个 wc-product-tile 元素")

        for i, tile in enumerate(tiles[:10]):
            try:
                # 直接使用 execute_script 进入 Shadow DOM 并提取内容
                title = driver.execute_script(
                    "return arguments[0].shadowRoot.querySelector('.product-title-container .title a')?.innerText", tile
                )
                price = driver.execute_script(
                    "return arguments[0].shadowRoot.querySelector('.product-tile-price .primary')?.innerText", tile
                )
                print(f"🎯 抓到标题: {title}")
                # 显示当下块的代码
                # print(driver.execute_script("return arguments[0].shadowRoot.innerHTML", tiles[0]))


                if not title:
                    print(f"⚠️ 第{i+1}个 tile 没有找到标题")
                    continue

                title = title.strip().lower()
                print(f"🔎 第{i+1}个标题: {title}")

                if is_similar_enough(search_term, title):
                    print(f"🎯 Woolworths 匹配成功: {title}")
                    if price:
                        price_clean = price.replace('$', '').strip()
                        print(f"💰 Woolworths 抓到价格文本: {price_clean}")
                        full_price = float(price_clean)
                        discount_price = round(full_price * 0.96, 2)
                        return full_price, discount_price
                    else:
                        print("❌ Woolworths 没有找到价格元素")
                        return None, None
                else:
                    print(f"🔍 Woolworths 标题不匹配: {title}（相似度 {similar(search_term, title):.2f}）")


            except Exception as e:
                print(f"⚠️ 第{i+1}个 tile 抓取失败: {e}")
                print("🔬 tile outerHTML:", tile.get_attribute('outerHTML'))

        print(f"❌ Woolworths 没有匹配商品: '{search_term}'")
        return None, None

    except Exception as e:
        print(f"❌ Woolworths 页面加载失败: {e}")
        print("🔬 页面 HTML 预览：\n", driver.page_source[:2000])
        return None, None



def get_price_from_coles(driver, search_term):
    from bs4 import BeautifulSoup
    import time, random

    driver.get("https://www.coles.com.au")
    time.sleep(random.uniform(2.5, 4.5))

    search_url = f"https://www.coles.com.au/search/products?q={search_term.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(random.uniform(3, 6))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = soup.find_all("section", {"data-testid": "product-tile"})

    if not products:
        print("❌ 没有找到任何产品元素")
        return None

    print(f"🔍 Coles 找到 {len(products)} 个产品,展示前3个:")
    for i, product in enumerate(products[:3]):
        # 名称
        title_tag = product.find("h2", class_="product__title")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        # 价格
        price_tag = product.find("span", {"data-testid": "product-pricing"})
        price_text = price_tag.get_text(strip=True).replace("$", "") if price_tag else None
        try:
            price = float(price_text)
        except:
            price = None

        sim_score = similar(search_term, title)

        print(f"\n🔹 第{i+1}个商品：")
        print(f"📦 名称: {title}")
        print(f"💰 价格: {price if price is not None else '未知'}")
        print(f"📏 相似度: {sim_score:.2f}")

        if is_similar_enough(search_term, title):
            print("🎯 Coles 匹配成功")
            return price, None  # 你可以在这里加打折逻辑 if needed

        print("❌ 没有找到足够相似的商品")
        return None, None

    return None





def main():
    product_list = ["Huggies Thick Baby Wipes",
                    "U by Kotex Pads 14 pack",
                    "Arnott's Family Favourites",
                    "TCC coconut Milk",
                    "Pepsi Cola Soft Drink Bottle 1.25l",
                    "Pringles potato chips 134g",
                    "spam ham Turkey 340g",
                    "Annalise butter beams",
                    "Libra Maternity Pads 10 pack",
                    "Schweppes  Soft Drink Bottle 1.1L",
                    "Schweppes Soda Water soft drink Bottle mixers 1.1L"]

    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.add_argument("--blink-settings=imagesEnabled=false")  # 禁用图片加载



    driver = uc.Chrome(options=options)

    print("📦 正在获取商品实时价格...\n")

    results = []

    for product in product_list:
        print(f"\n🔍 正在查找：{product}")
        wool_price, wool_discount = get_price_from_woolworths(driver, product)

        url = f"https://www.woolworths.com.au/shop/search/products?searchTerm={product.replace(' ', '%20')}"
        driver.get(url)
        time.sleep(random.uniform(3, 5))  # 可适当加长时间

        coles_price = get_price_from_coles(driver, product)
        # 观察页面
        # input("🕵️ 页面已打开，请手动观察页面加载情况，按回车继续...")

        cheaper = None
        coles_full_price = coles_price[0] if coles_price else None

        if wool_discount is not None and coles_full_price is not None:
            cheaper = "Woolworths" if wool_discount < coles_full_price else "Coles"
            print(f"🧮 最便宜的是: {cheaper}")
        else:
            print("⚠️ 无法比较价格，数据不完整")

        results.append({
            "Product": product,
            "Woolworths Price": wool_price,
            "Woolworths 4% Off": wool_discount,
            "Coles Price": coles_price,
            "Cheaper": cheaper
        })

    driver.quit()

    df = pd.DataFrame(results)
    print("\n📊 最终对比结果：\n")
    print(df.to_string(index=False))

    # 可选保存
    # df.to_excel("price_comparison.xlsx", index=False)
    # print("\n✅ 已保存结果到 price_comparison.xlsx")


if __name__ == "__main__":
    main()
