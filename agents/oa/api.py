import logging
from openai import OpenAI

client = OpenAI()
logger = logging.getLogger(__name__)

def initialize_assistant(name, system_prompt, model, tools=None, files=[]):
    logger.info('Initializing agent')
    try:
        assistant_kwargs = {
            "name": name,
            "instructions": system_prompt,
            "model": model
        }

        if tools is not None:
            assistant_kwargs["tools"] = tools

        if len(files) > 0:
            assistant_kwargs["tool_resources"] = {
                "code_interpreter": {
                    "file_ids": files
                }
            }

        assistant = client.beta.assistants.create(**assistant_kwargs)
        logger.info("Assistant initialized")
        return assistant
    except Exception as e:
        logger.error(f"Failed to initialize agent: Caught {e.__class__.__name__}: {e}")



def retrieve_assistant(assistant_id):
    try:
        logger.info('retrieving assistant')
        return client.beta.assistants.retrieve(assistant_id=assistant_id)
    except Exception as e:
        logger.error(f"Failed to retrieve assistant: Caught {e.__class__.__name__}: {e}")

def retrieve_thread(thread_id):
    try:
        logger.info('retrieving thread')
        return client.beta.threads.retrieve(thread_id=thread_id)
    except Exception as e:
        logger.error(f"Failed to retrieve thread: Caught {e.__class__.__name__}: {e}")

def initialize_thread():
    try:
        logger.info('Creating thread')
        thread = client.beta.threads.create()
        return thread
    except Exception as e:
        logger.error(f"Failed to initialize thread: Caught {e.__class__.__name__}: {e}")

def list_threads():
    try:
        logger.info('Listing threads')
        threads = client.beta.threads.list()
        return threads
    except Exception as e:
        logger.error(f"Failed to list threads: Caught {e.__class__.__name__}: {e}")
        return []

def get_run_steps(run, thread_id):
    try:
        logger.info('getting run steps')
        return client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id, order="asc")
    except Exception as e:
        logger.error(f"Failed to get run steps: Caught {e.__class__.__name__}: {e}")

def get_messages_from_thread(thread_id, after=None, order='asc'):
    params = {
        "thread_id": thread_id,
        "order": order,
    }
    if after:
        params["after"] = after

    messages_page = client.beta.threads.messages.list(**params)
    return list(messages_page)