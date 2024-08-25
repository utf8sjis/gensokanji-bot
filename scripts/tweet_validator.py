import colorama
import script_setup  # noqa: F401
import yaml
from colorama import Fore, Style
from twitter_text import parse_tweet

from constants import DATA_DIR
from data_models import TweetData

BAR_LENGTH = 100


colorama.init(autoreset=True)

with open(DATA_DIR / "tweets.yml") as f:
    print("=== tweets ===")

    tweets_data = TweetData(**yaml.safe_load(f))
    invalid_ids = []
    excess_image_count_ids = []
    no_image_file_names = []
    for tweet in tweets_data.tweets:
        parsed_result = parse_tweet(tweet.text)

        if not parsed_result.valid:
            percent_color = Fore.RED
            bar_color = Fore.RED
            invalid_ids.append(tweet.id)
        elif parsed_result.permillage > 950:
            percent_color = Fore.MAGENTA
            bar_color = Fore.MAGENTA
        elif parsed_result.permillage > 800:
            percent_color = Fore.YELLOW
            bar_color = Fore.YELLOW
        else:
            percent_color = Fore.GREEN
            bar_color = ""

        if tweet.images and len(tweet.images) > 4:
            image_count_color = Fore.RED
            excess_image_count_ids.append(tweet.id)
        else:
            image_count_color = ""

        if tweet.images:
            for image in tweet.images:
                if not (DATA_DIR / "images" / image).exists():
                    no_image_file_names.append(image)
                    images_color = Fore.RED
                    break
            else:
                images_color = ""
        else:
            images_color = ""

        id_sec = f"id: {tweet.id:<7}"
        percent = f"{percent_color}{parsed_result.permillage / 10:>6}%{Style.RESET_ALL}"
        image_count = f"{image_count_color}{len(tweet.images) if tweet.images else 0} image(s){Style.RESET_ALL}"
        images = f"{images_color}{'(' + ', '.join(tweet.images) + ')' if tweet.images else ''}{Style.RESET_ALL}"

        filled_length = int(BAR_LENGTH * parsed_result.permillage // 1000)
        fill = "#" * filled_length
        padding = " " * (BAR_LENGTH - filled_length)
        bar = f"{bar_color}{fill}{padding}{Style.RESET_ALL}"

        print(f"{id_sec}{percent} |{bar}| {image_count} {images}")

    print("=== summary ===")

    print(f"total: {len(tweets_data.tweets)}")

    tweet_ids = [tweet.id for tweet in tweets_data.tweets]
    print(f"{Fore.GREEN}id uniqueness: OK" if len(tweet_ids) == len(set(tweet_ids)) else f"{Fore.RED}id uniqueness: NG")
    duplicate_ids = set(tweet_id for tweet_id in tweet_ids if tweet_ids.count(tweet_id) > 1)
    print(f"- ids: {duplicate_ids}\n" if duplicate_ids else "", end="")

    print(f"{Fore.RED if invalid_ids else Fore.GREEN}invalid tweets: {len(invalid_ids)}")
    print(f"- ids: {invalid_ids}\n" if invalid_ids else "", end="")

    print(f"{Fore.RED if excess_image_count_ids else Fore.GREEN}excess number of images: {len(excess_image_count_ids)}")
    print(f"- ids: {excess_image_count_ids}\n" if excess_image_count_ids else "", end="")

    print(f"{Fore.RED if no_image_file_names else Fore.GREEN}no image files: {len(no_image_file_names)}")
    print(f"- file names: {no_image_file_names}\n" if no_image_file_names else "", end="")
