from app import scheduler
from constants import DATA_DIR


class TestScheduler:
    @staticmethod
    def test_bot_job(mocker):
        # Given:
        bot_init = mocker.patch("app.Bot.__init__", return_value=None)
        bot_post_regular_tweet = mocker.patch("app.Bot.post_regular_tweet")

        bot_job = scheduler.get_job("do_bot_job").func

        assert bot_job is not None

        # When:
        bot_job()

        # Then:
        bot_init.assert_called_once_with(DATA_DIR)
        bot_post_regular_tweet.assert_called_once()
