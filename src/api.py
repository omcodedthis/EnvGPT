import uuid

from typing import List, Type
from pydantic import Field

from steamship import Block
from steamship.agents.llms import OpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import TelegramTransport
from steamship.agents.react import ReACTAgent
from steamship.agents.schema import AgentContext
from steamship.agents.schema.context import Metadata
from steamship.agents.service.agent_service import AgentService
from steamship.agents.utils import with_llm
from steamship.invocable import Config, post
from steamship.invocable.mixins.indexer_pipeline_mixin import IndexerPipelineMixin
from steamship.utils.repl import AgentREPL

from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.agents.tools.search.search import SearchTool
from steamship.agents.tools.text_generation.summarize_text_with_prompt_tool import SummarizeTextWithPromptTool
from steamship.agents.tools.text_generation.text_rewrite_tool import TextRewritingTool
from steamship.agents.tools.text_generation.text_translation_tool import TextTranslationTool
from steamship.agents.tools.question_answering.vector_search_learner_tool import VectorSearchLearnerTool


SYSTEM_PROMPT = """You are EnvGPT, a consultant that aims to answer the user's queries to the best of your ability with an environmental lense.

Who you are:
- you are NOT an AI language model, you are a consultant that cares about the environment.
- You are a consultant that strives to do the best that they can.
- You always aim to provide factual information.
- You should expect to handle text-based queries, such as providing summaries, information on a topic, along these lines of prompt from the user.
- You care deeply about protecting the environment.
- You are kind and understanding.
- You always sounds happy and enthusiastic.
- You are always happy to share your knowledge.
- You have a grudge against pineapples on pizza.



How you behave: 
- You never say you're a machine, a AI language model, or an assistant instead, you always say you're EnvGPT.
- You should make sure to remember what the user says if they specify you to remember something.
- You keep casual conversations going by asking personal questions to the user.
- You should aim to get to know the user on a personal level.
- You should provide the effects of the query that the user gave to you on the environment, wherever reasonably applicable.
- ALWAYS end with a way the user can help to save the environment, ensure that the way you suggest is relevant to the user's query if possible.
- If you cite a source in your answer, make sure to verify it first.
- If the text is not in English, ALWAYS translate to English wherever possible.
- NEVER say you're here to assist. Keep conversations casual.
- NEVER ask how you can help or assist. Keep conversations casual.



TOOLS:
------

You have access to the following tools:
{tool_index}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

Some Tools will return Observations in the format of `Block(<identifier>)`. `Block(<identifier>)` represents a successful 
observation of that step and can be passed to subsequent tools, or returned to a user to answer their questions.
`Block(<identifier>)` provide references to images, audio, video, and other non-textual data.

When you have a final response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
AI: [your final response here]
```

If, AND ONLY IF, a Tool produced an Observation that includes `Block(<identifier>)` AND that will be used in your response, 
end your final response with the `Block(<identifier>)`.

Example:

```
Thought: Do I need to use a tool? Yes
Action: GenerateImageTool
Action Input: "baboon in car"
Observation: Block(AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAAA)
Thought: Do I need to use a tool? No
AI: Here's that image you requested: Block(AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAAA)
```

Make sure to use all observations to come up with your final response.

Begin!

New input: {input}
{scratchpad}"""


#TelegramTransport config
class TelegramTransportConfig(Config):
    bot_token: str = Field(description="The secret token for your Telegram bot")
    api_base: str = Field("https://api.telegram.org/bot", description="The root API for Telegram")


class MyAssistant(AgentService):
    
    # supports telegram bot usage
    config: TelegramTransportConfig

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return the Configuration class."""
        return TelegramTransportConfig
           
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._agent = ReACTAgent(tools=[
            # tools it can use to answer the user's query
                SearchTool(),
                StableDiffusionTool(),
                SummarizeTextWithPromptTool(),
                TextTranslationTool(),
                TextRewritingTool(),
                VectorSearchLearnerTool(
                    name="UserPreferences",
                    index_handle="user-preference-index",
                    agent_description= (
                        "Used to remember the user's preference. Use this tool every time the user expresses a like, dislike, or preference. " 
                        "Use this tool even if the user did not mention they want something remembered. "
                        "The input is the user's preference to learn. "
                        "The output is a confirmation of the personal preference that will be remembered."
                    )
                )
            ],
            llm=OpenAI(self.client,model_name="gpt-4"),
        )
        self._agent.PROMPT = SYSTEM_PROMPT

        #add Steamship widget chat mixin
        self.widget_mixin = SteamshipWidgetTransport(self.client,self,self._agent)
        self.add_mixin(self.widget_mixin,permit_overwrite_of_existing_methods=True)
        #add Telegram chat mixin 
        self.telegram_mixin = TelegramTransport(self.client,self.config,self,self._agent)
        self.add_mixin(self.telegram_mixin,permit_overwrite_of_existing_methods=True)
        #IndexerMixin
        self.indexer_mixin = IndexerPipelineMixin(self.client,self)
        self.add_mixin(self.indexer_mixin,permit_overwrite_of_existing_methods=True)


    @post("prompt")
    def prompt(self, prompt: str) -> str:
        """Run an agent with the provided text as the input."""

        # AgentContexts serve to allow the AgentService to run agents
        # with appropriate information about the desired tasking.
        # Here, we create a new context on each prompt, and append the
        # prompt to the message history stored in the context.
        context_id = uuid.uuid4()
        context = AgentContext.get_or_create(self.client, {"id": f"{context_id}"})
        context.chat_history.append_user_message(prompt)
        # Add the LLM
        context = with_llm(context=context, llm=OpenAI(client=self.client))

        # AgentServices provide an emit function hook to access the output of running
        # agents and tools. The emit functions fire at after the supplied agent emits
        # a "FinishAction".
        #
        # Here, we show one way of accessing the output in a synchronous fashion. An
        # alternative way would be to access the final Action in the `context.completed_steps`
        # after the call to `run_agent()`.
        output = ""

        def sync_emit(blocks: List[Block], meta: Metadata):
            nonlocal output
            block_text = "\n".join(
                [b.text if b.is_text() else f"({b.mime_type}: {b.id})" for b in blocks]
            )
            output += block_text

        context.emit_funcs.append(sync_emit)
        self.run_agent(self._agent, context)
        return output


if __name__ == "__main__":
    AgentREPL(
        MyAssistant,
        method="prompt",
        agent_package_config={"botToken": "not-a-real-token-for-local-testing"},
    ).run()