import abc
import glob
import json
import os
import re
import time
from enum import Enum
import requests
from abc import ABC
from copy import deepcopy
from playwright.sync_api import sync_playwright
import utils
from md2pdf import *


class HEADING(Enum):
    TYPE1 = "heading_1"
    TYPE2 = "heading_2"
    TYPE3 = "heading_3"


class LIST_ITEM_PREFIX(Enum):
    DASH = "^- "
    ASTERISK = "^\* "
    PLUS = "^\+ "
    N_DASH = "^    - "
    N_ASTERISK = "^  \* "
    NUMBERED = '^([0-9]+).'
    N_NUMBERED = '^    ([0-9]+).'
    N_PLUS = "^    + "


class LIST_ITEM_TYPE(Enum):
    BULLET = "bulleted_list_item"
    NUMBERED = "numbered_list_item"


class Block(ABC):
    type = "block"

    def __init__(self, fatherBlock):
        self.fatherBlock = fatherBlock
        self.block_id = None
        self._standaloneDict = None

    @abc.abstractmethod
    def render(self):
        pass


class FatherBlock(Block):

    def __init__(self, fatherBlock):
        super().__init__(fatherBlock)

        self.childs = []
        self.childDict = {
            "children": []
        }

    @property
    @abc.abstractmethod
    def standaloneDict(self):
        pass

    @standaloneDict.setter
    @abc.abstractmethod
    def standaloneDict(self, value):
        pass

    def render(self, standalone = False):
        if standalone:
            return self.standaloneDict
        else:
            return self._build_child_dict()

    def append_child(self, child):
        self.childs.append(child)

    @abc.abstractmethod
    def _build_child_dict(self):
        pass


class TableBlock(FatherBlock):
    type = "table"

    def __init__(self, fatherBlock):
        super().__init__(fatherBlock)

        self._standaloneDict = {
            "object": "block",
            "type":  "table",
            "table":  {
                "table_width":       2,
                "has_column_header": False,
                "has_row_header":    False,
                "children":          []
            }
        }

    @property
    def standaloneDict(self):
        return self._standaloneDict

    @standaloneDict.setter
    def standaloneDict(self, value):
        self._standaloneDict = {
            "object": "block",
            "type":  "table",
            "table":  {
                "table_width":       value['table_width'],
                "has_column_header": value['has_column_header'],
                "has_row_header":    value['has_row_header'],
                "children":          []
            }
        }

    def append_rich_text(self, rich_text):
        self.childs.append(rich_text)

    def _build_child_dict(self):
        rowsList = []

        for row in self.childs:
            rowsList.append(row.render(standalone = False))

        self._standaloneDict['table']['children'] = rowsList
        return self._standaloneDict


class TableRow(FatherBlock):
    type = "table_row"

    def __init__(self, fatherBlock):
        self.fatherBlock = fatherBlock
        self._standaloneDict = {
            "type":     "table_row",
            "table_row": {
                "cells": []
            }
        }

        self.richTexts = []

    @property
    def standaloneDict(self):
        return self._standaloneDict

    @standaloneDict.setter
    def standaloneDict(self, value):
        self._standaloneDict = {

            "type":     "table_row",
            "table_row": {
                "cells": []
            }

        }

    def append_rich_text(self, rich_text):
        self.richTexts.append(rich_text)

    def _build_child_dict(self):
        cellsList = []

        for cell in self.richTexts:
            cellsList.append([cell.render(standalone = False)])

        self._standaloneDict['table_row']['cells'] = cellsList
        return self._standaloneDict


class DividerBlock(Block):
    type = "divider"

    def __init__(self, fatherBlock):
        super().__init__(fatherBlock)
        self._standaloneDict = {
            "object":  "block",
            "type":   "divider",
            "divider": {}
        }

    @property
    def standaloneDict(self):
        return self._standaloneDict

    @standaloneDict.setter
    def standaloneDict(self, value):
        pass

    def render(self, standalone = True):
        return self.standaloneDict


class PageBlock(FatherBlock):
    type = "page_id"

    def __init__(self, fatherBlock):
        super().__init__(fatherBlock)

    @property
    def standaloneDict(self):
        return None

    @standaloneDict.setter
    def standaloneDict(self, value):
        return

    def _build_child_dict(self):
        childsList = []

        for child in self.childs:
            childsList.append(child.render(standalone = False))

        self.childDict['children'] = childsList
        return self.childDict


class HeadingBlock(FatherBlock):
    type = "heading_1"

    def __init__(self, fatherBlock):
        super().__init__(fatherBlock)
        self.heading_type = 'heading_1'
        HeadingBlock.type = self.heading_type

    @property
    def standaloneDict(self):
        return self._standaloneDict

    @standaloneDict.setter
    def standaloneDict(self, value):
        self.heading_type = value['heading_type']

        self._standaloneDict = {
            "object":              "block",
            "type":               value['heading_type'],
            value['heading_type']: {
                "rich_text":     [{"type": "text", "text": {"content": value['title']}}],
                "color":         "default",
                "is_toggleable": value['is_toggleable'],
                "children":      []
            }

        }

    def _build_child_dict(self):
        childsList = []

        for child in self.childs:
            childsList.append(child.render(standalone = False))

        if self._standaloneDict:
            self._standaloneDict[self.heading_type]['children'] = childsList
            return self._standaloneDict
        else:
            self.childDict['children'] = childsList
            return self.childDict


class ParagraphBlock(FatherBlock):
    type = "paragraph"

    def __init__(self, fatherBlock):
        super().__init__(fatherBlock)
        self.payloads = []
        self.richTexts = []

        self._standaloneDict = {
            "object":    "block",
            "type":     "paragraph",
            "paragraph": {
                "rich_text": [],
                "color":     "default",
                "children":  []
            }

        }

    @property
    def standaloneDict(self):
        return self._standaloneDict

    @standaloneDict.setter
    def standaloneDict(self, value):
        content = value['content']

        self._standaloneDict = {
            "object":    "block",
            "type":     "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text":  {
                        "content": content,
                        "link":    None
                    }
                }],
                "color":     "default",
                "children":  []
            }

        }

    def append_rich_text(self, rich_text):
        self.richTexts.append(rich_text)

    def _build_child_dict(self):

        if len(self.richTexts) > 0:
            return self._build_rich_text_list()

        childsList = []

        for child in self.childs:
            childsList.append(child.render(standalone = False))

        self._standaloneDict['paragraph']['children'] = childsList
        return self._standaloneDict

    def _build_rich_text_list(self):

        richTextList = []

        for richText in self.richTexts:
            richTextList.append(richText.render())

        self._standaloneDict['paragraph']['rich_text'] = richTextList

        return self._standaloneDict


class ImageBlock(Block):
    type = "image"

    def __init__(self, fatherBlock):
        super().__init__(fatherBlock)

    @property
    def standaloneDict(self):
        return self._standaloneDict

    @standaloneDict.setter
    def standaloneDict(self, value):
        self._standaloneDict = {
            "object": "block",
            "type":  "image",
            "image":  {
                "type":    "external",
                "external": {
                    "url": value['image_url']
                }
            }
        }

    def render(self, standalone = True):
        return self.standaloneDict


class TableOfContentsBlock(Block):
    type = "table_of_contents"

    def __init__(self, fatherBlock):
        super().__init__(fatherBlock)
        self._standaloneDict = {
            "object":            "block",
            "type":             "table_of_contents",
            "table_of_contents": {
                "color": "default"
            }
        }

    @property
    def standaloneDict(self):
        return self._standaloneDict

    @standaloneDict.setter
    def standaloneDict(self, value):
        self._standaloneDict = {
            "object":            "block",
            "type":             "table_of_contents",
            "table_of_contents": {
                "color": "default"
            }
        }

    def render(self, standalone = True):
        return self.standaloneDict


class RichText:
    type = "text"

    def __init__(self, fatherBlock):
        self.fatherBlock = fatherBlock
        self._standaloneDict = {}

    @property
    def standaloneDict(self):
        return self._standaloneDict

    @standaloneDict.setter
    def standaloneDict(self, value):
        self._standaloneDict = {
            "type":       "text",
            "text":        {
                "content": value['content'],
                "link":    None
            },
            "annotations": {
                "bold":          value['bold'],
                "italic":        value['italic'],
                "strikethrough": value['strikethrough'],
                "underline":     value['underline'],
                "code":          value['code'],
                "color":         value['color']
            },
            "plain_text":  value['content'],
            "href":        None
        }

    def render(self, standalone = True):
        return self.standaloneDict


class ListItem(FatherBlock):

    def __init__(self, fatherBlock, type = LIST_ITEM_TYPE.BULLET.value):
        super().__init__(fatherBlock)
        self.richTexts = []
        self.type = type

        self._standaloneDict = {
            "object": "block",
            "type":  type,
            type:     {
                "rich_text": [],
                "color":     "default",
                "children":  []
            }

        }

    @property
    def standaloneDict(self):
        return self._standaloneDict

    @standaloneDict.setter
    def standaloneDict(self, value):
        self._standaloneDict = {
            "object":  "block",
            "type":   self.type,
            self.type: {
                "rich_text": [{
                    "type": "text",
                    "text":  {
                        "content": value['content'],
                        "link":    None
                    }
                }],
                "color":     "default",
                "children":  []
            }

        }

    def _build_child_dict(self):

        if len(self.richTexts) > 0:
            self._build_rich_text_list()

        if len(self.childs) == 0:
            return self._standaloneDict

        childsList = []

        for child in self.childs:
            childsList.append(child.render(standalone = False))

        self._standaloneDict[self.type]['children'] = childsList
        return self._standaloneDict

    def append_rich_text(self, rich_text):
        self.richTexts.append(rich_text)

    def _build_rich_text_list(self):

        richTextList = []

        for richText in self.richTexts:
            richTextList.append(richText.standaloneDict)

        self._standaloneDict[self.type]['rich_text'] = richTextList

        return self._standaloneDict


class Notion:

    def __init__(self, notion_token, email = None, password = None):
        self.notion_token_v2 = None
        self.notion_token = notion_token
        self.email = email
        self.password = password

        self.headers = {
            "Authorization":  "Bearer " + self.notion_token,
            "Notion-Version": "2022-06-28",
            "content-type":  "application/json"
        }

        self.entities = [Block,
                         FatherBlock,
                         TableBlock,
                         TableRow,
                         DividerBlock,
                         PageBlock,
                         HeadingBlock,
                         ParagraphBlock,
                         ImageBlock,
                         TableOfContentsBlock,
                         RichText,
                         ListItem]

        self.mappings = [
        ]

        self.entitiesMap = self.__init_entities_map(entities = self.entities)

    def __init_entities_map(self, entities):
        map_ = {}
        for entity in entities:
            map_[entity.type] = entity

        return map_

    def create_page(self):
        url = "https://api.notion.com/v1/pages"

        payload = {
            "parent":     {
                "type":       "database_id",
                "database_id": "d9824bdc-8445-4327-be8b-5b47500af6ce"
            },
            "properties": "string"
        }

        response = requests.post(url, json = payload, headers = self.headers)

    def __get_token_v2(self):

        with sync_playwright() as p:
            browser = p.firefox.launch(headless = False)
            context = browser.new_context()
            page = context.new_page()
            page.goto('https://www.notion.so/login')
            # Interact with login form
            page.get_by_label("Email").fill(self.email)

            page.get_by_role("button", name = "Continue with email").click()
            page.get_by_label("Password").fill(self.password)
            page.get_by_role("button", name = "Continue with password").click()
            page.wait_for_timeout(5000)
            cookies = page.context.cookies()
            token_value = next(item['value'] for item in cookies if item["name"] == "token_v2")
            page.close()
            context.close()

            return token_value

    def read_page(self, page_id, headers):
        readUrl = f"https://api.notion.com/v3/blocks/{page_id}/children"
        res = requests.request("GET", readUrl, headers = headers)

        data = res.json()
        if res.status_code == 200:
            with open('db.json', 'w', encoding = 'utf8') as f:
                json.dump(data, f, ensure_ascii = False, indent = 4),
            return data

    def __request(self, type_, url, headers, payload = None):

        res = requests.request(type_, url, json = payload, headers = headers)
        data = res.json()
        if res.status_code == 200:
            with open('db.json', 'w', encoding = 'utf8') as f:
                json.dump(data, f, ensure_ascii = False, indent = 4),
            return res

    def get_heading_block(self, fatherBlock) -> HeadingBlock:

        heading = HeadingBlock(fatherBlock = fatherBlock)
        fatherBlock.append_child(heading)
        return heading

    def get_image_block(self, fatherBlock) -> ImageBlock:

        image = ImageBlock(fatherBlock = fatherBlock)
        fatherBlock.append_child(image)
        return image

    def get_paragraph_block(self, fatherBlock) -> ParagraphBlock:

        paragraph = ParagraphBlock(fatherBlock = fatherBlock)
        fatherBlock.append_child(paragraph)
        return paragraph

    def get_rich_text_block(self, fatherBlock) -> RichText:

        rich_text = RichText(fatherBlock = fatherBlock)
        fatherBlock.append_rich_text(rich_text)
        return rich_text

    def get_page_block(self, page_id) -> PageBlock:

        pageBlock = PageBlock(fatherBlock = None)
        pageBlock.block_id = page_id
        return pageBlock

    def get_list_item_block(self, fatherBlock, type) -> ListItem:

        list_item = ListItem(fatherBlock = fatherBlock, type = type)
        fatherBlock.append_child(list_item)
        return list_item

    def get_divider_block(self, fatherBlock) -> DividerBlock:

        divider = DividerBlock(fatherBlock = fatherBlock)
        fatherBlock.append_child(divider)
        return divider

    def get_heading_data(self, title, heading_type, is_toggleable = True):
        return {
            'heading_type':  heading_type,
            'title':         title,
            'is_toggleable': is_toggleable
        }

    def get_paragraph_data(self, content):
        return {
            'content': content
        }

    def get_rich_text_data(self,
                           content,
                           bold = False,
                           italic = False,
                           strikethrough = False,
                           underline = False,
                           code = False,
                           color = 'default'):

        return {
            "content":       content,
            "bold":          bold,
            "italic":        italic,
            "strikethrough": strikethrough,
            "underline":     underline,
            "code":          code,
            "color":         color

        }

    def get_bullet_data(self, content):
        return {
            'content': content
        }

    def get_image_data(self, image_url):
        return {
            'image_url': image_url
        }

    def get_toc(self, fatherBlock):
        toc = TableOfContentsBlock(fatherBlock = fatherBlock)
        fatherBlock.append_child(toc)
        return toc

    def __check_payload(self, payload):
        for children in payload['children']:
            if children['type'] == 'paragraph' and len(
                    children['paragraph']['rich_text'][0]['text']['content']) > 2000:
                base_payload = children
                content = children['paragraph']['rich_text'][0]['text']['content']
                l = len(content)
                limit = 2000
                pos1 = 0
                pos2 = limit

                payloads = []

                curr_payload = deepcopy(base_payload)

                chunk0 = content[pos1:pos2]
                curr_payload['paragraph']['rich_text'][0]['text']['content'] = chunk0

                curr_payload = {'children': [curr_payload]}

                payloads.append(curr_payload)

                while pos2 < l:
                    pos1 += 2000
                    pos2 += 2000
                    chunk = content[pos1:pos2]

                    curr_payload = deepcopy(base_payload)
                    curr_payload['paragraph']['rich_text'][0]['text']['content'] = chunk
                    curr_payload = {'children': [curr_payload]}
                    payloads.append(curr_payload)

                return payloads

        return [payload]

    def execute_append_block(self, block):
        url = f"https://api.notion.com/v1/blocks/{block.block_id}/children"
        payload = block.render()

        payloads = self.__check_payload(payload)

        if len(payloads) == 1:
            data = self.__request(type_ = 'PATCH', url = url, payload = payloads[0], headers = self.headers)
            return data
        else:
            data = self.__request(type_ = 'PATCH', url = url, payload = payloads[0], headers = self.headers)
            block_id = data['results'][0]['id']
            url = f"https://api.notion.com/v1/blocks/{block_id}/children"
            for idx in range(1, len(payloads)):
                self.__request(type_ = 'PATCH', url = url, payload = payloads[idx], headers = self.headers)
            return data

    def __parse_content(self, content, firstFatherBlock, image_url = None, title = None):

        lines = content.splitlines()
        blocks = []

        fatherBlock = firstFatherBlock
        bulletFatherBlock = firstFatherBlock

        table_lines = []

        for line in lines:

            if re.match(LIST_ITEM_PREFIX.DASH.value, line) \
                    or re.match(LIST_ITEM_PREFIX.ASTERISK.value, line) \
                    or re.match(LIST_ITEM_PREFIX.NUMBERED.value, line) \
                    or re.match(LIST_ITEM_PREFIX.PLUS.value, line):

                if re.match(LIST_ITEM_PREFIX.NUMBERED.value, line):
                    type = LIST_ITEM_TYPE.NUMBERED.value
                else:
                    type = LIST_ITEM_TYPE.BULLET.value

                bullet_list_elem = self.get_list_item_block(fatherBlock = fatherBlock, type = type)
                self.__parse_block_with_blod(fatherBlock = bullet_list_elem, content = line[2:])
                blocks.append(bullet_list_elem)
                bulletFatherBlock = bullet_list_elem

            elif re.match(LIST_ITEM_PREFIX.N_DASH.value, line) \
                    or re.match(LIST_ITEM_PREFIX.N_ASTERISK.value, line) \
                    or re.match(LIST_ITEM_PREFIX.N_NUMBERED.value, line):

                if re.match(LIST_ITEM_PREFIX.N_NUMBERED.value, line):
                    type = LIST_ITEM_TYPE.NUMBERED.value
                else:
                    type = LIST_ITEM_TYPE.BULLET.value

                bullet_list_elem = self.get_list_item_block(fatherBlock = bulletFatherBlock, type = type)
                self.__parse_block_with_blod(fatherBlock = bullet_list_elem, content = line[2:])
                blocks.append(bullet_list_elem)


            elif line.startswith("#"):

                heading_type = HEADING.TYPE1.value
                is_toggleable = False
                clean_line = None
                if line.startswith("# "):
                    heading_type = HEADING.TYPE1.value
                    is_toggleable = True
                    fatherBlock = firstFatherBlock
                    bulletFatherBlock = firstFatherBlock

                    if title:
                        clean_line = title

                elif line.startswith("## "):
                    heading_type = HEADING.TYPE2.value


                elif line.startswith("### "):
                    heading_type = HEADING.TYPE3.value

                line = line.replace("#", "").replace("**", "")
                line = line.strip()

                if clean_line is None:
                    clean_line = line

                heading = self.get_heading_block(fatherBlock = fatherBlock)

                heading_data = self.get_heading_data(title = clean_line, heading_type = heading_type,
                                                     is_toggleable = is_toggleable)

                heading.standaloneDict = heading_data

                if is_toggleable:
                    fatherBlock = heading
                    bulletFatherBlock = heading

                if image_url and heading_type == HEADING.TYPE1.value:
                    image = self.get_image_block(fatherBlock = fatherBlock)
                    image_data = self.get_image_data(image_url = image_url)
                    image.standaloneDict = image_data


            elif len(line) > 0 and line[0] == "|" and line[-1] == "|":
                table_lines.append(line)

            else:
                if len(table_lines) > 0:

                    data = self.execute_append_block(firstFatherBlock)
                    results = data['results']

                    for idx in range(len(results) - 1, -1, -1):
                        if results[idx]['type'] == fatherBlock.type:
                            id = results[idx]['id']
                            fatherBlock = self.entitiesMap[fatherBlock.type](fatherBlock = None)
                            fatherBlock.block_id = id

                    content = '\n'.join(table_lines)
                    self.handle_table_creation(fatherBlock = fatherBlock, content = content)

                    self.execute_append_block(fatherBlock)
                    table_lines = []

                    fatherBlock = self.entitiesMap[fatherBlock.type](fatherBlock = None)
                    fatherBlock.block_id = id
                    firstFatherBlock = fatherBlock

                paragraph = self.get_paragraph_block(fatherBlock = fatherBlock)

                self.__parse_block_with_blod(fatherBlock = paragraph, content = line)
                blocks.append(paragraph)

        dividerBlock = self.get_divider_block(fatherBlock = firstFatherBlock)
        self.execute_append_block(firstFatherBlock)

    def get_json_table(self, content):
        json_table = []

        for n, line in enumerate(content.split('\n')):
            data = {}
            if n == 0:
                header = [t.strip() for t in line.split('|')[1:-1]]
            if n > 1:
                values = [t.strip() for t in line.split('|')[1:-1]]
                for col, value in zip(header, values):
                    data[col] = value
                json_table.append(data)

        return json_table

    def __get_parsed_table(self, content):

        rows = []

        for n, line in enumerate(content.split('\n')):
            if n == 0:
                header = [t.strip() for t in line.split('|')[1:-1]]
            if n > 1:
                values = [t.strip() for t in line.split('|')[1:-1]]
                rows.append(values)

        return header, rows

    def get_table_block(self, fatherBlock):
        table = TableBlock(fatherBlock = fatherBlock)
        fatherBlock.append_child(child = table)
        return table

    def get_table_data(self,
                       width,
                       has_column_header,
                       has_row_header):
        return {
            'table_width':       width,
            'has_column_header': has_column_header,
            'has_row_header':    has_row_header
        }

    def get_table_row(self, fatherBlock):
        row = TableRow(fatherBlock = fatherBlock)
        fatherBlock.append_child(row)
        return row

    def handle_table_creation(self, fatherBlock, content):
        header, rows = self.__get_parsed_table(content = content)
        table = self.get_table_block(fatherBlock = fatherBlock)

        table_data = self.get_table_data(width = len(header), has_row_header = False, has_column_header = True)
        table.standaloneDict = table_data

        rows.insert(0, header)

        for row in rows:
            row_block = self.get_table_row(fatherBlock = table)

            for elem in row:
                self.__parse_block_with_blod(fatherBlock = row_block, content = elem)

        return table

    def __parse_block_with_blod(self, fatherBlock, content):

        found_bolds = list(re.finditer('\*\*(.+?)\*\*', content))

        prev_end = -1

        if len(found_bolds) == 0:
            rich_text = self.get_rich_text_block(fatherBlock = fatherBlock)
            rich_text_data = self.get_rich_text_data(content = content)
            rich_text.standaloneDict = rich_text_data

            return

        if found_bolds[0].start() != 0:
            text = content[0: found_bolds[0].start()]
            rich_text = self.get_rich_text_block(fatherBlock = fatherBlock)
            rich_text_data = self.get_rich_text_data(content = text)
            rich_text.standaloneDict = rich_text_data

            prev_end = found_bolds[0].end()

        for found in found_bolds:

            s = found.start()
            e = found.end()

            if s != prev_end + 1:
                text = content[prev_end: s]
                rich_text = self.get_rich_text_block(fatherBlock = fatherBlock)
                rich_text_data = self.get_rich_text_data(content = text)
                rich_text.standaloneDict = rich_text_data

            bold_text = content[s + 2:e - 2]

            rich_text = self.get_rich_text_block(fatherBlock = fatherBlock)
            rich_text_data = self.get_rich_text_data(content = bold_text, bold = True)
            rich_text.standaloneDict = rich_text_data
            prev_end = e

        if e < len(content):
            rich_text = self.get_rich_text_block(fatherBlock = fatherBlock)
            rich_text_data = self.get_rich_text_data(content = content[e:])
            rich_text.standaloneDict = rich_text_data

    def create_toc(self, page_id):
        page = self.get_page_block(page_id = page_id)
        self.get_toc(fatherBlock = page)
        self.execute_append_block(page)

    def create_section(self, page_id, content, image_url = None, title = None):

        page = self.get_page_block(page_id = page_id)

        self.__parse_content(content = content, firstFatherBlock = page, image_url = image_url, title = title)
        return None

    def test(self, page_id):

        fatherBlock = self.get_page_block(page_id = page_id)

        header = ['**Day**', '**Outlook**', '**Temperature [Humidity]**', '**Wind**', '**Play**']

        rows = [['1', 'Sunny', 'High [Humid]', 'Weak', 'No'], ['2', 'Sunny', 'High [Humid]', 'Strong', 'No'],
                ['3', 'Overcast', 'High [Humid]', 'Weak', 'Yes'], ['4', 'Rain', 'High [Humid]', 'Weak', 'Yes'],
                ['5', 'Rain', 'Normal [Humid]', 'Weak', 'Yes'], ['6', 'Rain', 'Normal [Dry]', 'Strong', 'No'],
                ['7', 'Overcast', 'Normal [Dry]', 'Strong', 'Yes'], ['8', 'Sunny', 'High [Humid]', 'Weak', 'No'],
                ['9', 'Sunny', 'Normal [Dry]', 'Weak', 'Yes'], ['10', 'Rain', 'Normal [Dry]', 'Weak', 'Yes'],
                ['11', 'Sunny', 'Normal [Humid]', 'Strong', 'Yes'], ['12', 'Overcast', 'High [Dry]', 'Strong', 'Yes'],
                ['13', 'Overcast', 'Normal [Humid]', 'Weak', 'Yes'], ['14', 'Rain', 'High [Humid]', 'Strong', 'No']]

        table = self.get_table_block(fatherBlock = fatherBlock)

        table_data = self.get_table_data(width = len(header), has_row_header = True, has_column_header = False)
        table.standaloneDict = table_data

        rows.insert(0, header)

        for row in rows:
            row_block = self.get_table_row(fatherBlock = table)

            for elem in row:
                self.__parse_block_with_blod(fatherBlock = row_block, content = elem)

        self.execute_append_block(fatherBlock)

    def __get_content_download_URL(self, page_id):
        self.notion_token_v2 = self.__get_token_v2()

        enqueue_payload = {"task":
                               {"eventName": "exportBlock",
                                "request":
                                             {
                                                 "block":     {"id": page_id},
                                                 "recursive": False,
                                                 "exportOptions":
                                                              {
                                                                  "exportType": "markdown", "timeZone": "Europe/Rome",
                                                                  "locale":     "en"
                                                              }
                                             }
                                }
                           }
        header = {
            "Cookie": f"token_v2={self.notion_token_v2}",
        }

        res = self.__request(type_ = 'POST', url = "https://www.notion.so/api/v3/enqueueTask", headers = header,
                             payload = enqueue_payload)
        task_id = res.json()['taskId']
        task_payload = {"taskIds": [task_id]}

        completed = False

        while not completed:

            res = self.__request(type_ = 'POST', url = "https://www.notion.so/api/v3/getTasks", headers = header,
                                 payload = task_payload)

            results = res.json()['results']

            task = next(item for item in results if item["id"] == task_id)

            if task['state'] == "in_progress" or task['state'] == "not_started":
                time.sleep(1)
            elif task["state"] == "success" and task['status']['exportURL']:
                completed = True
                exportURL = task['status']['exportURL']

            else:
                raise Exception

        return exportURL

    def notion2markdown(self, page_id,
                        email = None,
                        password = None,
                        unzip_folder = 'unzips',
                        pdf_name = "generated_pdf.pdf",
                        pdf_folder = '',
                        css_file_path = None,
                        base_images_url = None):

        if email:
            self.email = email
        if password:
            self.password = password

        if not (self.email and self.password):
            return

        exportURL = self.__get_content_download_URL(page_id = page_id)

        directory = unzip_folder
        utils.unzip_from_url(url = exportURL, directory = directory)
        filename = glob.glob(directory + '/*.md')[0]
        md_file_path = os.path.join(directory, filename)

        md_content = read_md(md_file_path = md_file_path)
        md_content = replace_line_with_newpage(md_content = md_content)

        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)

        pdf_file_path = os.path.join(pdf_folder, pdf_name)

        md2pdf(pdf_file_path = pdf_file_path,
               md_content = md_content,
               css_file_path = css_file_path,
               base_url = base_images_url)
