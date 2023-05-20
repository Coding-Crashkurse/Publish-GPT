import json
import os
import re

import openai
import pypandoc
import requests
import typer
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")


class BookGenerator:
    def __init__(self, config_path="model_config.json"):
        self.load_config(config_path)
        self.words = 0
        self.chapters = []
        self.texts = []
        self.book_title = ""
        self.image_url = ""
        self.description = ""
        self.image_file_path = ""
        self.messages = [self.config["system_message"]]

    def load_chapters(self):
        try:
            with open("chapters.json", "r") as f:
                self.chapters = json.load(f)
        except FileNotFoundError:
            self.chapters = []

    def save_chapters(self):
        with open("chapters.json", "w") as f:
            json.dump(self.chapters, f)

    def load_config(self, path):
        with open(path, "r") as f:
            self.config = json.load(f)

    def initialize_book(
        self, book_title: str, description: str, words: int, image: str
    ):
        self.book_title = book_title
        self.description = description
        self.words = words
        self.image_url = self.get_image_url(image)
        self.download_image(self.image_url, self.book_title)

    def get_image_url(self, image: str):
        response = openai.Image.create(prompt=image, n=1, size="1024x1024")
        return response["data"][0]["url"]

    def download_image(self, image_url: str, image_file_name: str):
        image_response = requests.get(image_url)
        self.image_file_path = f"{image_file_name}_cover.png"
        with open(self.image_file_path, "wb") as f:
            f.write(image_response.content)
        return self.image_file_path

    def generate_chapters(self, chapter_count: int):
        initial_prompt = self.config["initial_prompt"].format(
            self.book_title, chapter_count, self.chapters
        )
        self.add_user_message(initial_prompt)
        response = self.create_chat_completion()
        self.add_assistant_message(response.choices[0].message["content"])
        chapter_list = self.extract_chapters_from_response(response)
        self.chapters = chapter_list

    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})

    def create_chat_completion(self):
        return openai.ChatCompletion.create(
            model=self.config["model"],
            messages=self.messages,
        )

    def extract_chapters_from_response(self, response):
        raw_output = response.choices[0].message["content"]
        chapter_list = raw_output.split("\n")
        chapter_list = [
            chap.split(".")[1].strip() if "." in chap else chap.strip()
            for chap in chapter_list
            if chap.strip() != ""
        ]

        for i in range(len(chapter_list)):
            for char in self.config["chars_to_remove"]:
                chapter_list[i] = chapter_list[i].replace(char, "")

            chapter_list[i] = re.sub(r"\d+", "", chapter_list[i])
            chapter_list[i] = chapter_list[i].strip()

        chapter_list.pop(0)
        chapter_list = [i for i in chapter_list if i]
        return chapter_list

    def generate_text(self):
        for chapter in tqdm(self.chapters, desc="Generating chapter text"):
            prompt = self.config["text_prompt"].format(
                self.words, chapter, self.book_title, self.description
            )
            self.add_user_message(prompt)

            response = self.create_chat_completion()

            self.add_assistant_message(response.choices[0].message["content"])
            self.texts.append(response.choices[0].message["content"])

    def create_markdown(self, book_title: str):
        with open(f"{book_title}.md", "w", encoding="utf-8") as f:
            f.write(f"#<center>{book_title.upper()}</center>\n\n")
            f.write(f"![{book_title}]({book_title}_cover.png)\n\n")
            for chapter, text in zip(self.chapters, self.texts):
                f.write(f"\n## {chapter}\n\n")
                f.write(text)
                f.write("\n")

    def convert_markdown_to_pdf(self):
        markdown_files = [f for f in os.listdir() if f.endswith(".md")]

        if len(markdown_files) == 0:
            typer.echo("No Markdown files found in the current directory.")
            return

        markdown_file_name = typer.prompt(
            "Please choose a file to convert", default=markdown_files[0]
        )

        if markdown_file_name not in markdown_files:
            typer.echo(f"{markdown_file_name} not found in the current directory.")
            return

        pdf_file_name = f"{markdown_file_name.replace('.md', '')}_output.pdf"
        pypandoc.convert_file(
            markdown_file_name,
            "pdf",
            outputfile=pdf_file_name,
            extra_args=self.config["pandoc_extra_args"],
        )
        typer.echo(f"Successfully converted {markdown_file_name} to {pdf_file_name}")
