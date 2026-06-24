# gensokanji-bot

This is [元素の漢字bot (@gensokanji_bot)](https://twitter.com/gensokanji_bot), a Twitter bot that regularly tweets the Chinese names of elements and related trivia. It runs on GitHub Actions using scheduled workflows.

## License

This project uses a dual licensing approach:

### Source Code - MIT License

The source code is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Content - All Rights Reserved

The content in `resources/tweet_content/` (including `tweets.yml` and all images) is NOT covered by the MIT License and remains under exclusive copyright. See [resources/tweet_content/LICENSE](resources/tweet_content/LICENSE) for details.

## Optional Xquik post backend

The bot posts through Tweepy by default. To route text-only tweets, or tweets
with public media URLs, through Xquik instead, set:

```env
X_POST_BACKEND=xquik
XQUIK_API_KEY=xq_YOUR_KEY
XQUIK_ACCOUNT=@your_account
XQUIK_CREATE_TWEET_URL=https://xquik.com/api/v1/x/tweets
```

Xquik accepts public media URLs. Keep `X_POST_BACKEND=twitter` for the bundled
local image files.
