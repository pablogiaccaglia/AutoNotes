import os

import md2pdf
from config import settings
from AutoNotes import AutoNotes
from collections import namedtuple
from prompts import Prompts

chatgpt_token = settings.chatgpt_token

cloudnary_cloud_name = settings.cloudnary_cloud_name
cloudnary_api_key = settings.cloudnary_api_key
cloudnary_api_secret = settings.cloudnary_api_secret
cloudnary_secure = settings.cloudnary_secure

notionToken = settings.notionToken
notion_email = settings.notion_email
notion_password = settings.notion_password

CloudnaryConfig = namedtuple("CloudnaryConfig",
                             ["cloudnary_cloud_name", "cloudnary_api_key", "cloudnary_api_secret", "cloudnary_secure"])
NotionConfig = namedtuple("NotionConfig", ["token", "email", "password"])

cloudnary_config = CloudnaryConfig(cloudnary_cloud_name, cloudnary_api_key, cloudnary_api_secret, cloudnary_secure)
notion_config = NotionConfig(notionToken, notion_email, notion_password)

pdf_path = "/Users/pablo/Desktop/chatgptPARSER/Biofisica01_07Mar23.pdf"
page_id = 'd90a1937-b27b-406b-a443-42992f57ae75'
cloudinary_folder_name = 'BIOFISICA-Media'

page_id = "0e46556a-2938-4beb-932f-b8dbc0feb63d"

autonotes = AutoNotes(chat_gpt_token = chatgpt_token,
                      cloudnary_config = cloudnary_config,
                      notion_config = notion_config)

autonotes.generate(pdf_path = pdf_path,
                   base_query = Prompts.BIOFISICA_SLIDES.value,
                   first_page = 2,
                   last_page = None,
                   notion_page_id = page_id,
                   images_folder_name = cloudinary_folder_name,
                   generate_title = False,
                   create_toc = True, verbose = True)

autonotes.generate_pdf(page_id = page_id, base_images_url = "http://res.cloudinary.com")
