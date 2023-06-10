import os

import md2pdf
import utils
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

pdf_path = "/Users/pablo/Desktop/chatgptPARSER/1_Introduction (1).pdf"
page_id = utils.format_notion_id('926472e1d53d4432a9c5dabe8396ceba')
cloudinary_folder_name = 'NLP-Media'

autonotes = AutoNotes(chat_gpt_token = chatgpt_token,
                      cloudnary_config = cloudnary_config,
                      notion_config = notion_config)

"""autonotes.generate(pdf_path = pdf_path,
                   base_query = Prompts.NLP_SLIDES.value,
                   first_page = 20,
                   last_page = None,
                   notion_page_id = page_id,
                   images_folder_name = cloudinary_folder_name,
                   generate_title = False,
                   create_toc = True, verbose = True)"""

#autonotes.generate_pdf(page_id = page_id, base_images_url = "http://res.cloudinary.com")
from md2pdf import *
md2pdf(pdf_file_path = pdf_path,
               md_content = None,
               md_file_path = "/Users/pablo/Desktop/chatgptPARSER/unzips/Introduction 926472e1d53d4432a9c5dabe8396ceba.md",
               css_file_path = "markdown.css",
               base_url = "http://res.cloudinary.com")
