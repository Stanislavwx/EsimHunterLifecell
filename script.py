import re
import time
from playwright.sync_api import sync_playwright

def is_beautiful(number: str) -> bool:
    clean_num = re.sub(r'\D', '', number)
    if len(clean_num) < 7:
        return False
        
    # 1. Три і більше однакових цифр підряд (напр. 777, 88888)
    match_rep = re.search(r'(\d)\1{2,}', clean_num)
    if match_rep:
        print(f"\n[!] 3+ однакових підряд: {match_rep.group(0)}")
        return True
        
    # 2. Дублювання коду оператора (напр. 073 073)
    if len(clean_num) >= 6 and clean_num[0:3] == clean_num[3:6]:
        print(f"\n[!] Дублювання коду: {clean_num[0:3]} {clean_num[3:6]}")
        return True
        
    # 3. Повторення трійок (напр. 073 5 123 123)
    # Шукаємо у частині після коду оператора
    match_blocks = re.search(r'(\d{3})\1', clean_num[3:]) 
    if match_blocks:
        print(f"\n[!] Повторення блоку: {match_blocks.group(0)}")
        return True
        
    # 4. Ритм: чергування пар в кінці номера (напр. 15 15 або 72 72 72)
    match_pairs = re.search(r'(\d{2})\1{1,}$', clean_num)
    if match_pairs:
        print(f"\n[!] Парні повторення в кінці: {match_pairs.group(0)}")
        return True
        
    # 5. Сходинки (послідовність з 4+ цифр)
    if re.search(r'(0123|1234|2345|3456|4567|5678|6789|9876|8765|7654|6543|5432|4321|3210)', clean_num):
        print(f"\n[!] Сходинки (послідовність) знайдена!")
        return True
        
    # 6. Дзеркало / Паліндром (4 цифри в самому кінці, напр. 1221 або 8558)
    match_pal = re.search(r'(\d)(\d)\2\1$', clean_num)
    if match_pal:
         print(f"\n[!] Дзеркальне закінчення: {match_pal.group(0)}")
         return True

    return False
        
    # Шукаємо 3 і більше однакових цифр підряд
    match = re.search(r'(\d)\1{2,}', clean_num)
    
    if match:
        print(f"\n[!] Знайдена гарна комбінація підряд: {match.group(0)}")
        return True
        
    return False

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context() 
        page = context.new_page()
        
        page.goto("https://shop.lifecell.ua/uk/catalog/esim/")
        
        print("\n" + "="*60)
        print("1. Додай eSIM у кошик.")
        print("2. Перейди до оформлення замовлення, щоб побачити номер.")
        print("3. ПІСЛЯ ЦЬОГО натисни Enter у терміналі!")
        print("="*60 + "\n")
        
        input("Натисни Enter, коли будеш на сторінці оформлення...")
        
        attempt = 1
        while True:
            try:
                # Оновлюємо сторінку
                page.reload(wait_until="domcontentloaded")
                time.sleep(2) # Даємо 2 секунди сайту, щоб він підтягнув кошик і відмалював номер
                
                # Спосіб 1: Шукаємо по основному селектору (гнучко)
                elements = page.locator("[class*='Radio_radioHelpText']").all()
                number_text = None
                
                for el in elements:
                    if el.is_visible():
                        number_text = el.inner_text()
                        break
                        
                # Спосіб 2: Якщо перший не спрацював, беремо номер з бокового блоку "У кошику"
                if not number_text:
                    alt_elements = page.locator("[class*='CartLine_cartLineInfoProductMsisdn']").all()
                    for el in alt_elements:
                        if el.is_visible():
                            number_text = el.inner_text().replace("Номер:", "").strip()
                            break
                
                # Якщо номер досі не знайдено (наприклад, сторінка зависла), робимо ще одну спробу
                if not number_text:
                    print(f"[{attempt}] Елемент ще вантажиться. Пробуємо ще раз...")
                    continue
                
                print(f"[{attempt}] Випав номер: {number_text}")
                
                if is_beautiful(number_text):
                    print(f"🎉 БІНГО! ЗНАЙДЕНО ГАРНИЙ НОМЕР: {number_text}")
                    break  
                else:
                    attempt += 1
                    
            except Exception as e:
                print(f"Помилка: {e}. Пробуємо ще раз...")
                time.sleep(2)
        
        input("\nСкрипт зупинено. Оформлюй замовлення у відкритому вікні. Коли закінчиш — натисни Enter тут для виходу...")
        browser.close()

if __name__ == "__main__":
    main()
