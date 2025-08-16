import requests
import csv
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS: Dict[str, str] = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Referer": "https://www.speedquizzing.com/sq-question-manager/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
}

COOKIES: Dict[str, str] = {
    "sq_session": "YOUR_COOKIE"  # 🔑 Replace with your session cookie
}

URL_ROUNDS = "https://www.speedquizzing.com/utils/question_manager/round_launch_ajax/"
URL_QUIZPACK = "https://www.speedquizzing.com/utils/question_manager/launch_quizpack_json/"
URL_OPTIONS = "https://www.speedquizzing.com/utils/question_manager/edit_question_json/"

PARAMS_LIST = [
    {"data": "keypad", "_": str(int(time.time() * 1000))},
    {"data": "advanced", "_": str(int(time.time() * 1000))},
    {"data": "multi tap", "_": str(int(time.time() * 1000))},
    {"data": "nearest", "_": str(int(time.time() * 1000))},
]

OUTPUT_FILE = "all_quizpacks.csv"

session = requests.Session()
session.headers.update(HEADERS)
session.cookies.update(COOKIES)


def fetch_quizpack_keys() -> List[str]:
    keys: List[str] = []
    for params in PARAMS_LIST:
        resp = session.get(URL_ROUNDS, params=params, timeout=10)
        resp.raise_for_status()
        keys.extend(resp.json().keys())
    print("Found %d quizpack keys", len(keys))
    return keys


def fetch_quizpack(key: str) -> List[Dict[str, Any]]:
    payload = {"str": key, "version": "2"}
    resp = session.post(
        URL_QUIZPACK,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def fetch_options(q_id: str) -> Dict[str, Any]:
    params = {"id": q_id, "_": str(int(time.time() * 1000))}
    resp = session.get(URL_OPTIONS, params=params, timeout=10)
    resp.raise_for_status()

    opt_data = resp.json()
    options = [
        opt_data.get(f"option{i}", "").strip()
        for i in range(1, 7)
        if opt_data.get(f"option{i}", "").strip()
    ]

    return {
        "options": options,
        "long_answer": opt_data.get("long_answer", "").strip(),
        "short_answer": opt_data.get("short_answer", "").strip(),
    }


def collect_all_items(keys: List[str]) -> List[Dict[str, Any]]:
    all_items: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_quizpack, k): k for k in keys}
        for future in as_completed(futures):
            key = futures[future]
            try:
                all_items.extend(future.result())
            except Exception as e:
                print("Error fetching quizpack %s: %s", key, e)
    print("Fetched %d questions total", len(all_items))
    return all_items


def enrich_items(items: List[Dict[str, Any]]) -> List[List[Any]]:
    output_rows: List[List[Any]] = []
    total = len(items)

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(fetch_options, item.get("id", "").strip()): item for item in items}
        for i, future in enumerate(as_completed(futures), start=1):
            item = futures[future]
            try:
                opt_data = future.result()
            except Exception as e:
                print("Error fetching options for %s: %s", item.get("id"), e)
                opt_data = {"options": [], "long_answer": "", "short_answer": ""}

            answer = item.get("answer", "").strip()
            additional_info = (
                opt_data["long_answer"]
                if opt_data["long_answer"] not in {opt_data["short_answer"], answer}
                else ""
            )

            output_rows.append([
                item.get("id", "").strip(),
                item.get("question", "").strip(),
                answer,
                additional_info,
                item.get("type_code", "").strip(),
                item.get("obsolete", "").strip(),
                item.get("fav", ""),
                item.get("publish_date", ""),
                item.get("publish_date_str", "").strip(),
                item.get("author_name", "").strip(),
                item.get("user_tags", "").strip(),
                opt_data["options"],
                item.get("image_src1", "").strip(),
            ])

            if i % 10 == 0 or i == total:
                print("Progress: %d/%d (%.0f%%)", i, total, i / total * 100)

    return output_rows


def save_to_csv(rows: List[List[Any]], filename: str) -> None:
    headers = [
        "ID", "Question", "Answer", "Additional Info",
        "Type Code", "Obsolete", "Fav",
        "Publish Date Timestamps", "Publish Date",
        "Author Name", "User Tags", "Options", "Image",
    ]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print("Done! Saved %d rows to %s", len(rows), filename)


def main() -> None:
    quizpack_keys = fetch_quizpack_keys()
    all_items = collect_all_items(quizpack_keys)
    rows = enrich_items(all_items)
    save_to_csv(rows, OUTPUT_FILE)


if __name__ == "__main__":
    main()
