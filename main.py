pip install --upgrade selenium

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Selenium için ChromeDriver yolu (Kendi yolunuzu buraya ekleyin)
CHROMEDRIVER_PATH = "C:/chromedriver/chromedriver.exe"  # Windows için örnek

# Kullanıcı agenti
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Platform URL'leri
urls = {
    "alibaba": "https://www.alibaba.com/showroom/{product}.html",
    "made_in_china": "https://www.made-in-china.com/products-search/hot-china-products/{product}.html"
}


def fetch_static_data(product, platform):
    """Statik içerik için veri çekme (Requests + BeautifulSoup)."""
    url = urls[platform].format(product=product)
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    data = []

    if platform == "alibaba":
        items = soup.select(".organic-gallery-offer-outter")
        for item in items[:10]:
            title = item.select_one(".elements-title-normal__content")
            price = item.select_one(".elements-offer-price-normal__price")
            if title and price:
                data.append({"Ürün": title.get_text(strip=True), "Fiyat": price.get_text(strip=True)})

    elif platform == "made_in_china":
        items = soup.select(".product-info")
        for item in items[:10]:
            title = item.select_one(".product-name")
            price = item.select_one(".price")
            if title and price:
                data.append({"Ürün": title.get_text(strip=True), "Fiyat": price.get_text(strip=True)})

    return pd.DataFrame(data)


def fetch_dynamic_data(product, platform):
    """Dinamik içerik için Selenium kullanarak veri çekme."""
    url = urls[platform].format(product=product)
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    time.sleep(5)  # Sayfanın tam yüklenmesi için bekle

    data = []

    if platform == "alibaba":
        items = driver.find_elements(By.CSS_SELECTOR, ".organic-gallery-offer-outter")
        for item in items[:10]:
            try:
                title = item.find_element(By.CSS_SELECTOR, ".elements-title-normal__content").text
                price = item.find_element(By.CSS_SELECTOR, ".elements-offer-price-normal__price").text
                data.append({"Ürün": title, "Fiyat": price})
            except Exception as e:
                print("Bir öğe işlenirken hata oluştu:", e)

    elif platform == "made_in_china":
        items = driver.find_elements(By.CSS_SELECTOR, ".product-info")
        for item in items[:10]:
            try:
                title = item.find_element(By.CSS_SELECTOR, ".product-name").text
                price = item.find_element(By.CSS_SELECTOR, ".price").text
                data.append({"Ürün": title, "Fiyat": price})
            except Exception as e:
                print("Bir öğe işlenirken hata oluştu:", e)

    driver.quit()
    return pd.DataFrame(data)


def visualize_prices(data):
    """Fiyatları görselleştirme."""
    if data.empty:
        print("Görselleştirme için yeterli veri bulunamadı.")
        return

    data["Fiyat (USD)"] = data["Fiyat"].str.extract(r"(\d+\.?\d*)").astype(float)
    plt.figure(figsize=(10, 6))
    plt.bar(data["Ürün"], data["Fiyat (USD)"], color='skyblue')
    plt.title("Ürünlerin Fiyat Analizi")
    plt.xlabel("Ürün")
    plt.ylabel("Fiyat (USD)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# Ana Program
if __name__ == "__main__":
    product = input("Lütfen analiz yapmak istediğiniz ürünü girin: ").strip()
    platform = input("Platform seçin (alibaba / made_in_china): ").strip().lower()

    if platform not in urls:
        print("Geçersiz platform seçimi. Lütfen 'alibaba' veya 'made_in_china' girin.")
    else:
        print(f"{platform.capitalize()} için '{product}' ürünü aranıyor...")

        # Statik veri çekme
        data = fetch_static_data(product, platform)

        # Statik veri boşsa, dinamik veri çekmeyi dene
        if data.empty:
            print("Statik veri çekilemedi, dinamik veri çekme deneniyor...")
            data = fetch_dynamic_data(product, platform)

        # Veri çıktısı ve görselleştirme
        if data.empty:
            print("Veri bulunamadı. Ürün adı veya platform doğru mu kontrol edin.")
        else:
            print(data)
            visualize_prices(data)

            # Veriyi Excel'e kaydetme
            file_name = f"{product}_pazar_arastirma.xlsx"
            data.to_excel(file_name, index=False)
            print(f"Veriler '{file_name}' dosyasına kaydedildi.")
