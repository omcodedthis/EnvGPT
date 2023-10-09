# EnvGPT
EnvGPT is an AI chatbot built & hosted on [Steamship.](https://www.steamship.com/) It acts as a assistant / consultant that answers the user's queries with an environmental viewpoint. It has the ability to lookup various terms, translate text, summarise text, rephrase text, analyse text & generate images or speech when specified to answer the user's queries using [OpenAI's GPT-4.](https://openai.com/gpt-4) It takes into consideration the environment wherever possible & includes it in its reply to the user. This is an early preview of AI-based software (AI Agents).


## Demo

https://github.com/omcodedthis/EnvGPT/assets/119602009/4d91e700-0a55-4709-acc7-1643040041d3

Above is a demo of EnvGPT in action, hosted on Steamship. Apologies for the poor quality, it is due to GitHub's file size limits & video compression. As shown above, all its replies are given with an environmental lens.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
![EnvGPTQnA](https://github.com/omcodedthis/EnvGPT/assets/119602009/dede7f53-96a2-47c6-9081-ba14764ad048)

Above shows how EnvGPT interacts with the user's query by using the tools it has to generate its response. This was taken using the CLI (Terminal) when testing EnvGPT before deploying it to Steamship. Click on the image to view an enlarged version in a new tab.


## Changelog & Future Updates
Workaround found, branch `yet-to-be-pushed` has merged with `main`. The changes that were made locally have been pushed to Steamship.

* Added support for Telegram Bots, you can do so [here.](https://github.com/steamship-packages/telegram-buddy/blob/main/README.md)
  
* Added the ability to keep track of the user's preferences by default.

* Added support for Image Generation from text prompts if specified.
  
* Added sentiment analysis for articles or text queried by the user.

* Added support for Speech Generation from text prompts if specified.

* Added support for rephrasing text provided by the user.

* Added the ability to classify a piece of text if specified.
  

## Getting Started
I really wanted to provide a live instance of EnvGPT but Steamship has usage limits for free-tier accounts. You can still use EnvGPT by creating your own instance using the links provided below.

* Make a [Steamship](https://www.steamship.com/) account.
  
* Create your own instance of EnvGPT using the links below.
  * Latest (Telegram-supported as well) version [here.](https://www.steamship.com/packages/envgpt-4-bot)
  * Telegram-supported version [here.](https://www.steamship.com/packages/envgpt4-bot)
  * Web-based version [here.](https://www.steamship.com/packages/envgpt-bot)

* If you want to use EnvGPT as a base for your own projects, use these command lines.
  * To run it in the terminal,
 
  ```
  PYTHONPATH=src python3.8 src/api.py
   ```
  
  * To deploy to Steamship,
  ```
  ship deploy
   ```
