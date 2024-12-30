import csv
from scholarly import scholarly
from datetime import datetime
import os

HISTORY_FILE = "saved_articles_history.csv"  # 統合履歴管理用ファイル

def fetch_scholar_articles(keyword, num_articles, existing_titles):     #指定したキーワードでGoogle Scholarを検索し、指定された数の新しい論文を取得
    search_query = scholarly.search_pubs(keyword)
    new_articles = []
    try:
        while len(new_articles) < num_articles:
            article = next(search_query)
            if article['bib']['title'] not in existing_titles:
                new_articles.append({
                    'title': article['bib']['title'],
                    'author': article['bib'].get('author', 'N/A'),
                    'year': article['bib'].get('pub_year', 'N/A'),
                    'link': article.get('eprint_url', 'N/A'),
                })
    except StopIteration:
        print("すべての結果を取得しました。")
    
    return new_articles

def load_existing_articles(filename):       # 指定されたCSVファイルから保存済みタイトルをセットとして返す。
    if not os.path.exists(filename):
        return set()
    
    with open(filename, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        return set(row['title'] for row in reader)

def save_to_csv(data, filename, mode='w'):      #指定されたデータをCSVファイルに保存（utf-8-sigのおかげで文字化けしない）。
    file_exists = os.path.exists(filename)
    with open(filename, mode=mode, newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=["title", "author", "year", "link"])
        if not file_exists or mode == 'w':
            writer.writeheader()
        writer.writerows(data)

# 入力
keyword = input("検索したいキーワードを入力してください: ")
num_articles = int(input("取得したい論文数を入力してください: "))

# 日時付きファイル名
current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"scholar_articles_{keyword.replace(' ', '_')}_{current_datetime}.csv"

# 統合履歴ファイルを読み込む
existing_titles = load_existing_articles(HISTORY_FILE)

# 新しい論文を取得
new_articles = fetch_scholar_articles(keyword, num_articles, existing_titles)

if new_articles:
    # 新規データを日時付きファイルに保存
    save_to_csv(new_articles, csv_filename)
    print(f"{len(new_articles)} 件の新しい論文を {csv_filename} に保存しました。")

    # 統合履歴にも追記
    save_to_csv(new_articles, HISTORY_FILE, mode='a')
    print(f"{len(new_articles)} 件のデータを {HISTORY_FILE} に記録しました。")
else:
    print("追加の論文はありません。")
