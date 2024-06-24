from app import scheduler
from constants import DATA_DIR


class TestScheduler:
    def test_bot_job(self, mocker):
        # Given:
        mock_bot_init = mocker.patch("bot.Bot.__init__", return_value=None)
        mock_bot_post_regular_tweet = mocker.patch("bot.Bot.post_regular_tweet")

        bot_job = scheduler.get_job("do_bot_job").func

        assert bot_job is not None

        # When:
        bot_job()

        # Then:
        mock_bot_init.assert_called_once_with(DATA_DIR)
        mock_bot_post_regular_tweet.assert_called_once()
