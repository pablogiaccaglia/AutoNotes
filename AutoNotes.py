from services.gdrive import *
from pdf2image import convert_from_path
from services.ocr import img2text
import numpy as np
from services.notion import Notion
from services.cloudinary_ import Cloudinary
from revChatGPT.V3 import Chatbot


class AutoNotes:

    def __init__(self,
                 cloudnary_config,
                 chat_gpt_token,
                 notion_config
                 ):

        self.chatgpt = Chatbot(api_key = chat_gpt_token, system_prompt = "Sei un professore universitario che mi dovrà spiegare concetti di biofisica cellulare e molecolare, rispondi correttamente usando tutte le parole che vuoi")
        self.notion = Notion(notion_token = notion_config.token,
                             email = notion_config.email,
                             password = notion_config.password)

        self.cloudinary = Cloudinary(
                cloud_name = cloudnary_config.cloudnary_cloud_name,
                api_key = cloudnary_config.cloudnary_api_key,
                api_secret = cloudnary_config.cloudnary_api_secret,
                secure = cloudnary_config.cloudnary_secure)

    def __ask_chat_gpt(self, query, curr_text, continue_if_needed = True):

        prev_text = ""
        prev_text = self.chatgpt.ask(
                query
        )

        curr_text += prev_text

        if prev_text[-1] != '.' and continue_if_needed:
            prev_text = self.chatgpt.ask(
                    "Continue"
            )
            curr_text = curr_text[:-1] + prev_text[1:]

        return curr_text

    def generate(self,
                 pdf_path,
                 base_query,
                 notion_page_id,
                 images_folder_name,
                 first_page = None,
                 last_page = None,
                 generate_title = False,
                 create_toc = False,
                 verbose = False
                 ):

        pages = convert_from_path(pdf_path, 350, thread_count = 300, first_page = first_page, last_page = last_page)
        pdf_filename = os.path.basename(pdf_path)
        pdf_filename = pdf_filename[:-4]

        whole_text = ""
        sep = "---"

        if create_toc:
            self.notion.create_toc(page_id = notion_page_id)

        for idx, page in enumerate(pages):

            img_filename = pdf_filename + "_page_" + str(idx + 1) + ".jpg"
            page.save(img_filename)

            photo_url = self.cloudinary.upload_file(public_id = img_filename[:-4],
                                                    file_name = img_filename,
                                                    folder_name = images_folder_name,
                                                    get_url = True)

            os.remove(img_filename)

            open_cv_image = np.array(page)

            t = img2text(open_cv_image)

            query = base_query + t

            curr_text = self.__ask_chat_gpt(query = query, curr_text = "")

            bold_query = "provide me this exact markdown text but add bold words when needed: \n\n" + curr_text

            curr_text = self.__ask_chat_gpt(query = bold_query, curr_text = "")

            if verbose:
                print(curr_text)

            if generate_title:
                title_query = "give me a concise title for this paragraph, without quotation marks : \n\n" + curr_text

                title = self.__ask_chat_gpt(query = title_query, curr_text = "", continue_if_needed = False)

            else:
                title =None

            self.notion.create_section(page_id = notion_page_id, content = curr_text,
                                       image_url = photo_url, title = title)

            whole_text += "\n" + sep + "\n" + curr_text

            print("DONE PAGE #" + str(idx + 1))

    def generate_pdf(self,
                     page_id,
                     email = None,
                     password = None,
                     unzip_folder = 'unzips',
                     base_images_url = None,
                     css_file_path = None
                     ):
        return self.notion.notion2markdown(page_id = page_id,
                                           email = email,
                                           password = password,
                                           unzip_folder = unzip_folder,
                                           base_images_url = base_images_url,
                                           css_file_path = css_file_path)
