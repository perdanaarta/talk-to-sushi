from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

import dacite
import yaml
import os 
import discord

from .base import Config, Message, Prompt, Conversation, SEPARATOR_TOKEN
from .utils import split_into_shorter_messages, close_thread
from main import logger

import openai


CONFIG: Config = dacite.from_dict(
    Config, yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "config.yaml"), "r"))
)
BOT_NAME = CONFIG.name
BOT_INSTRUCTIONS = CONFIG.instructions
BOT_EXAMPLE_CONVOS = CONFIG.example_conversations


class CompletionResult(Enum):
    OK = 0
    TOO_LONG = 1
    INVALID_REQUEST = 2
    OTHER_ERROR = 3


@dataclass
class CompletionData:
    status: CompletionResult
    reply_text: Optional[str]
    status_text: Optional[str]


async def generate_completion_response(
    messages: List[Message], user: str
) -> CompletionData:
    try:
        prompt = Prompt(
            header=Message(
                "System", f"Instructions for {BOT_NAME}: {BOT_INSTRUCTIONS}"
            ),
            examples=BOT_EXAMPLE_CONVOS,
            convo=Conversation(messages + [Message(BOT_NAME)]),
        )
        rendered = prompt.render()
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=rendered,
            temperature=1.0,
            top_p=0.9,
            max_tokens=512,
            stop=[SEPARATOR_TOKEN],
        )
        reply = response.choices[0].text.strip()

        return CompletionData(
            status=CompletionResult.OK, reply_text=reply, status_text=None
        )
    except openai.error.InvalidRequestError as e:
        if "This model's maximum context length" in e.user_message:
            return CompletionData(
                status=CompletionResult.TOO_LONG, reply_text=None, status_text=str(e)
            )
        else:
            logger.exception(e)
            return CompletionData(
                status=CompletionResult.INVALID_REQUEST,
                reply_text=None,
                status_text=str(e),
            )
    except Exception as e:
        logger.exception(e)
        return CompletionData(
            status=CompletionResult.OTHER_ERROR, reply_text=None, status_text=str(e)
        )

async def process_response(
    user: str, thread: discord.Thread, response_data: CompletionData
):
    status = response_data.status
    reply_text = response_data.reply_text
    status_text = response_data.status_text

    
    if status is CompletionResult.OK:
        sent_message = None
        if not reply_text:
            sent_message = await thread.send(
                embed=discord.Embed(
                    description=f"**Invalid response** - empty response",
                    color=discord.Color.yellow(),
                )
            )
        else:
            shorter_response = split_into_shorter_messages(reply_text)
            for r in shorter_response:
                sent_message = await thread.send(r)

    elif status is CompletionResult.TOO_LONG:
        await close_thread(thread)

    elif status is CompletionResult.INVALID_REQUEST:
        await thread.send(
            embed=discord.Embed(
                description=f"**Invalid request** - {status_text}",
                color=discord.Color.yellow(),
            )
        )
    else:
        await thread.send(
            embed=discord.Embed(
                description=f"**Error** - {status_text}",
                color=discord.Color.yellow(),
            )
        )
