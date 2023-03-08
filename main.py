import os
from config import settings
from AutoNotes import AutoNotes
from collections import namedtuple

chatgpt_token = settings.chatgpt_token

cloudnary_cloud_name = settings.cloudnary_cloud_name
cloudnary_api_key = settings.cloudnary_api_key
cloudnary_api_secret = settings.cloudnary_api_secret
cloudnary_secure = settings.cloudnary_secure

notionToken = settings.notionToken
notion_email = settings.notion_email
notion_password = settings.notion_password

base_query = """write as a book paragraph what i'll provide to you. 
You need to explain the content i give to you, 
using as many words as possible, when needed use bullet points, 
but not overuse them, mix them with plain text. 
Keep in mind that this text needs to be used as a studying resource, so it must be as exhaustive as possible.  Write the answer in markdown, use titles and subtitles
The topic is Natural Language Processing, do not explain what NLP is.
Here's the query, remember to not explain what NLP is.: \n\n"""

CloudnaryConfig = namedtuple("CloudnaryConfig",
                             ["cloudnary_cloud_name", "cloudnary_api_key", "cloudnary_api_secret", "cloudnary_secure"])
NotionConfig = namedtuple("NotionConfig", ["token", "email", "password"])

cloudnary_config = CloudnaryConfig(cloudnary_cloud_name, cloudnary_api_key, cloudnary_api_secret, cloudnary_secure)
notion_config = NotionConfig(notionToken, notion_email, notion_password)

pdf_path = "2_Classification.pdf"
page_id = 'd90a1937-b27b-406b-a443-42992f57ae75'
cloudinary_folder_name = 'NLP-Media'

autonotes = AutoNotes(chat_gpt_token = chatgpt_token,
                      cloudnary_config = cloudnary_config,
                      notion_config = notion_config)

"""autonotes.generate(pdf_path = pdf_path,
                   base_query = base_query,
                   first_page = 63,
                   last_page = 73,
                   notion_page_id = page_id,
                   images_folder_name = cloudinary_folder_name,
                   generate_title = False,
                   create_toc = True)"""

autonotes.generate_pdf(page_id = page_id)
