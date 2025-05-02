import colorama
from colorama import Fore, Style
from pydantic import BaseModel
from twitter_text import ParsedResult, parse_tweet

from bot.utils import get_all_tweets_from_file
from constants import DATA_DIR
from models.tweet import TweetItem

BAR_LENGTH = 100


colorama.init(autoreset=True)


class Color(BaseModel):
    percent: str
    bar: str
    image_count: str
    images: str


class TweetValidator:
    def __init__(self) -> None:
        self.tweets = get_all_tweets_from_file()
        self.invalid_ids: list[str] = []
        self.excess_image_count_ids: list[str] = []
        self.no_image_file_names: list[str] = []

    def _validate_tweet(self, tweet: TweetItem, parsed_result: ParsedResult) -> Color:
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

        if len(tweet.image_paths) > 4:
            image_count_color = Fore.RED
            self.excess_image_count_ids.append(tweet.id)
        else:
            image_count_color = ""

        for image in tweet.image_paths:
            if not (DATA_DIR / "images" / image).exists():
                self.no_image_file_names.append(image)
                images_color = Fore.RED
                break
        else:
            images_color = ""

        return Color(
            percent=percent_color,
            bar=bar_color,
            image_count=image_count_color,
            images=images_color,
        )

    def _display_tweets(self) -> None:
        print("=== tweets ===")

        for tweet in self.tweets:
            parsed_result = parse_tweet(tweet.text)
            color = self._validate_tweet(tweet, parsed_result)

            id_sec = f"id: {tweet.id:<7}"
            percent = (
                color.percent + f"{parsed_result.permillage / 10:>6}%" + Style.RESET_ALL
            )
            image_count = (
                color.image_count
                + f"{len(tweet.image_paths)} image(s)"
                + Style.RESET_ALL
            )
            images = (
                color.images
                + (
                    ("(" + ", ".join(tweet.image_paths) + ")")
                    if tweet.image_paths
                    else ""
                )
                + Style.RESET_ALL
            )

            filled_length = int(BAR_LENGTH * parsed_result.permillage // 1000)
            fill = "#" * filled_length
            padding = " " * (BAR_LENGTH - filled_length)
            bar = f"{color.bar}{fill}{padding}{Style.RESET_ALL}"

            print(f"{id_sec}{percent} |{bar}| {image_count} {images}")

    def _display_summary(self) -> None:
        print("=== summary ===")

        print(f"total: {len(self.tweets)}")

        tweet_ids = [tweet.id for tweet in self.tweets]
        duplicate_ids = set(
            tweet_id for tweet_id in tweet_ids if tweet_ids.count(tweet_id) > 1
        )
        print(
            f"{Fore.RED}id uniqueness: NG"
            if len(tweet_ids) != len(set(tweet_ids))
            else f"{Fore.GREEN}id uniqueness: OK"
        )
        print(f"- ids: {duplicate_ids}\n" if duplicate_ids else "", end="")

        invalid_tweets_color = Fore.RED if self.invalid_ids else Fore.GREEN
        print(f"{invalid_tweets_color}invalid tweets: {len(self.invalid_ids)}")
        print(f"- ids: {self.invalid_ids}\n" if self.invalid_ids else "", end="")

        excess_image_count_color = (
            Fore.RED if self.excess_image_count_ids else Fore.GREEN
        )
        print(
            f"{excess_image_count_color}excess number of images: "
            f"{len(self.excess_image_count_ids)}",
        )
        print(
            f"- ids: {self.excess_image_count_ids}\n"
            if self.excess_image_count_ids
            else "",
            end="",
        )

        no_image_files_color = Fore.RED if self.no_image_file_names else Fore.GREEN
        print(f"{no_image_files_color}no image files: {len(self.no_image_file_names)}")
        print(
            f"- file names: {self.no_image_file_names}\n"
            if self.no_image_file_names
            else "",
            end="",
        )

    def display_result(self) -> None:
        self._display_tweets()
        self._display_summary()


if __name__ == "__main__":
    tweet_validator = TweetValidator()
    tweet_validator.display_result()
