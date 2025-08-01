import time
import random
import pandas as pd
import undetected_chromedriver as uc

from scraper import get_price_from_woolworths, get_price_from_coles

def main():
    product_list = [
        "Huggies Thick Baby Wipes",
        "U by Kotex Pads 14 pack",
        "Arnott's Family Favourites",
        "TCC coconut Milk",
        "Pepsi Cola Soft Drink Bottle 1.25l",
        "Pringles potato chips 134g",
        "spam ham Turkey 340g",
        "Annalise butter beams",
        "Libra Maternity Pads 10 pack",
        "Schweppes Soft Drink Bottle 1.1L",
        "Schweppes Soda Water soft drink Bottle mixers 1.1L"
    ]

    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.add_argument("--blink-settings=imagesEnabled=false")

    driver = uc.Chrome(options=options)

    print("Fetching live product prices...\n")
    results = []

    for product in product_list:
        print(f"\nSearching for: {product}")
        wool_price, wool_discount = get_price_from_woolworths(driver, product)

        # Allow time between searches
        time.sleep(random.uniform(3, 5))

        coles_price = get_price_from_coles(driver, product)
        cheaper = None
        coles_full_price = coles_price[0] if coles_price else None

        if wool_discount is not None and coles_full_price is not None:
            cheaper = "Woolworths" if wool_discount < coles_full_price else "Coles"
            print(f"Cheapest: {cheaper}")
        else:
            print("Unable to compare prices due to missing data.")

        results.append({
            "Product": product,
            "Woolworths Price": wool_price,
            "Woolworths 4% Off": wool_discount,
            "Coles Price": coles_price,
            "Cheaper": cheaper
        })

    driver.quit()

    df = pd.DataFrame(results)
    print("\nFinal price comparison:\n")
    print(df.to_string(index=False))

    # Optional: save to file
    # df.to_excel("price_comparison.xlsx", index=False)
    # print("Saved result to price_comparison.xlsx")

if __name__ == "__main__":
    main()
