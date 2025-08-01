import time, random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from utils import similar, is_similar_enough


def get_price_from_woolworths(driver, search_term):

    url = f"https://www.woolworths.com.au/shop/search/products?searchTerm={search_term.replace(' ', '%20')}"
    driver.get(url)
    time.sleep(random.uniform(3, 5))

    try:
        # Wait for wc-product-tile elements to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "wc-product-tile"))
        )
        tiles = driver.find_elements(By.CSS_SELECTOR, "wc-product-tile")
        print(f"Woolworths found {len(tiles)} product tiles")

        for i, tile in enumerate(tiles[:10]):
            try:
                # Access Shadow DOM to extract product title and price
                title = driver.execute_script(
                    "return arguments[0].shadowRoot.querySelector('.product-title-container .title a')?.innerText", tile
                )
                price = driver.execute_script(
                    "return arguments[0].shadowRoot.querySelector('.product-tile-price .primary')?.innerText", tile
                )
                print(f"Product title extracted: {title}")

                if not title:
                    print(f"Product {i+1} has no title")
                    continue

                title = title.strip().lower()
                print(f"Product {i+1} title: {title}")

                if is_similar_enough(search_term, title):
                    print(f"Woolworths match found: {title}")
                    if price:
                        price_clean = price.replace('$', '').strip()
                        print(f"Raw price text from Woolworths: {price_clean}")
                        full_price = float(price_clean)
                        discount_price = round(full_price * 0.96, 2)
                        return full_price, discount_price
                    else:
                        print("Price not found for matching product")
                        return None, None
                else:
                    print(f"Title mismatch: {title} (similarity {similar(search_term, title):.2f})")

            except Exception as e:
                print(f"Failed to extract product {i+1}: {e}")
                print("Outer HTML of tile:", tile.get_attribute('outerHTML'))

        print(f"No matching product found on Woolworths for '{search_term}'")
        return None, None

    except Exception as e:
        print(f"Failed to load Woolworths page: {e}")
        print("Preview of HTML content:\n", driver.page_source[:2000])
        return None, None


def get_price_from_coles(driver, search_term):
    from bs4 import BeautifulSoup
    import time, random

    # Load Coles homepage first to initialize session
    driver.get("https://www.coles.com.au")
    time.sleep(random.uniform(2.5, 4.5))

    # Navigate to search result page
    search_url = f"https://www.coles.com.au/search/products?q={search_term.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(random.uniform(3, 6))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = soup.find_all("section", {"data-testid": "product-tile"})

    if not products:
        print("No product elements found on Coles.")
        return None

    print(f"Coles found {len(products)} products, showing up to top 3:")

    for i, product in enumerate(products[:3]):
        # Extract product title
        title_tag = product.find("h2", class_="product__title")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        # Extract product price
        price_tag = product.find("span", {"data-testid": "product-pricing"})
        price_text = price_tag.get_text(strip=True).replace("$", "") if price_tag else None
        try:
            price = float(price_text)
        except:
            price = None

        sim_score = similar(search_term, title)

        print(f"\nProduct {i+1}:")
        print(f"Title: {title}")
        print(f"Price: {price if price is not None else 'Unknown'}")
        print(f"Similarity: {sim_score:.2f}")

        if is_similar_enough(search_term, title):
            print("Coles match found.")
            return price, None  # Optional: add discount logic here

        print("No sufficiently similar product found.")
        return None, None

    return None
