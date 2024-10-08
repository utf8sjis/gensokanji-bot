from pathlib import Path

import colorama
import yaml
from colorama import Fore, Style
from pydantic import BaseModel
from twitter_text import ParsedResult, parse_tweet

from constants import DATA_DIR
from data_models import TweetData, TweetDataItem

BAR_LENGTH = 100


colorama.init(autoreset=True)


class Color(BaseModel):
    percent: str
    bar: str
    image_count: str
    images: str


class TweetValidator:
    def __init__(self, tweet_data_path: Path) -> None:
        self.tweet_data: TweetData = self._load_tweet_data(tweet_data_path)
        self.invalid_ids: list[str] = []
        self.excess_image_count_ids: list[str] = []
        self.no_image_file_names: list[str] = []

    def _load_tweet_data(self, tweet_data_path: Path) -> TweetData:
        with open(tweet_data_path) as f:
            return TweetData(**yaml.safe_load(f))

    def _validate_tweet(self, tweet: TweetDataItem, parsed_result: ParsedResult) -> Color:
        if not parsed_result.valid:
            percent_color = Fore.RED
            bar_color = Fore.RED
            self.invalid_ids.append(tweet.id)
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
            self.excess_image_count_ids.append(tweet.id)
        else:
            image_count_color = ""

        if tweet.images:
            for image in tweet.images:
                if not (DATA_DIR / "images" / image).exists():
                    self.no_image_file_names.append(image)
                    images_color = Fore.RED
                    break
            else:
                images_color = ""
        else:
            images_color = ""

        return Color(percent=percent_color, bar=bar_color, image_count=image_count_color, images=images_color)

    def _display_tweets(self) -> None:
        print("=== tweets ===")

        for tweet in self.tweet_data.tweets:
            parsed_result = parse_tweet(tweet.text)
            color = self._validate_tweet(tweet, parsed_result)

            id_sec = f"id: {tweet.id:<7}"
            percent = f"{color.percent}{parsed_result.permillage / 10:>6}%{Style.RESET_ALL}"
            image_count = f"{color.image_count}{len(tweet.images) if tweet.images else 0} image(s){Style.RESET_ALL}"
            images = f"{color.images}{'(' + ', '.join(tweet.images) + ')' if tweet.images else ''}{Style.RESET_ALL}"

            filled_length = int(BAR_LENGTH * parsed_result.permillage // 1000)
            fill = "#" * filled_length
            padding = " " * (BAR_LENGTH - filled_length)
            bar = f"{color.bar}{fill}{padding}{Style.RESET_ALL}"

            print(f"{id_sec}{percent} |{bar}| {image_count} {images}")

    def _display_summary(self) -> None:
        print("=== summary ===")

        print(f"total: {len(self.tweet_data.tweets)}")

        tweet_ids = [tweet.id for tweet in self.tweet_data.tweets]
        duplicate_ids = set(tweet_id for tweet_id in tweet_ids if tweet_ids.count(tweet_id) > 1)
        print(
            f"{Fore.RED}id uniqueness: NG"
            if len(tweet_ids) != len(set(tweet_ids))
            else f"{Fore.GREEN}id uniqueness: OK"
        )
        print(f"- ids: {duplicate_ids}\n" if duplicate_ids else "", end="")

        invalid_tweets_color = Fore.RED if self.invalid_ids else Fore.GREEN
        print(f"{invalid_tweets_color}invalid tweets: {len(self.invalid_ids)}")
        print(f"- ids: {self.invalid_ids}\n" if self.invalid_ids else "", end="")

        excess_image_count_color = Fore.RED if self.excess_image_count_ids else Fore.GREEN
        print(f"{excess_image_count_color}excess number of images: {len(self.excess_image_count_ids)}")
        print(f"- ids: {self.excess_image_count_ids}\n" if self.excess_image_count_ids else "", end="")

        no_image_files_color = Fore.RED if self.no_image_file_names else Fore.GREEN
        print(f"{no_image_files_color}no image files: {len(self.no_image_file_names)}")
        print(f"- file names: {self.no_image_file_names}\n" if self.no_image_file_names else "", end="")

    def display_result(self) -> None:
        self._display_tweets()
        self._display_summary()


if __name__ == "__main__":
    tweet_validator = TweetValidator(DATA_DIR / "tweets.yml")
    tweet_validator.display_result()
