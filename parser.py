import os
import csv
import time
import requests

# Put shop id below as a python integer number
SHOP_ID =
# Put items names below as a python list
ITEMS_NAMES =
# Put output file name below as a python string
OUTPUT_FILE =


def write(rows, output_file=OUTPUT_FILE):
    """Expects rows to be a list of tuples."""
    dir_name = "results"
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    with open(dir_name + "/" + output_file, "a", newline="") as review_file:
        review_writer = csv.writer(review_file)
        for row in rows:
            review_writer.writerow(row)


def process_reviews(reviews, items_names=ITEMS_NAMES):
    result = []
    for review in reviews:
        text = review["text"]
        lower_text = text.lower()
        for item_name in items_names:
            if lower_text.find(item_name.lower()) != -1:
                result.append((
                    review["author"]["name"],
                    review["created_at_relative"],
                    review["summary"],
                    review["rating"],
                    text
                ))
    return result


def get_response(url, params, headers):
    try:
        response = requests.get(url, params=params, headers=headers)
    except:
        print("Couldn't get response from server.")
        raise
    if response.status_code == 200:
        print("Page {} is being processed.".format(params["page"]))
        return response.json()
    else:
        print("Bad response.")
        raise


def main():
    url = "https://review.api.onliner.by/catalog/shops/{}/reviews"
    url = url.format(str(SHOP_ID))
    # Only accept header is required to get the correct response
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
    }
    params = {
        "order": "created:desc",
        "page": 1
    }

    try:
        response = get_response(url, params, headers)
    except:
        quit()

    last_page = response["page"]["last"]
    reviews_from_page = response["reviews"]
    all_result_reviews = process_reviews(reviews_from_page)

    write([("Имя", "Когда", "Заголовок", "Оценка", "Отзыв")])

    while params["page"] < last_page:

        if len(all_result_reviews) >= 10: # Clear memory
            write(all_result_reviews)
            all_result_reviews = []

        time.sleep(5)
        params["page"] += 1

        try:
            response = get_response(url, params, headers)
        except:
            continue

        reviews_from_page = response["reviews"]
        all_result_reviews += process_reviews(reviews_from_page)

    if len(all_result_reviews) != 0:
        write(all_result_reviews)


if __name__ == "__main__":
    main()
