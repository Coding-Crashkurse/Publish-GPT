import json
from pathlib import Path

import typer

from publishgpt.book import BookGenerator

app = typer.Typer()


@app.command()
def init_config():
    """
    Initialize the config.json and .env files
    """
    model_config_file = Path("model_config.json")

    default_model_config = {
        "model": "gpt-3.5-turbo",
        "system_message": {
            "role": "system",
            "content": "You are a creative AI writing assistant. You're writing a book and are provided one chapter at a time. Always consider the entire context of all the chapters while writing a section. They have to fit together in the end.",
        },
        "initial_prompt": "I'm writing a book titled '{}'. Could you please suggest {} chapters? Please return only the titles, without numbering or anything similar. All chapters: {}",
        "text_prompt": "Could you please generate about {} words of text for the '{}' chapter of the book '{}'? Please keep {} in mind when generating the texts.",
        "chars_to_remove": ["-", "#"],
        "pandoc_extra_args": ["--pdf-engine=xelatex"],
    }

    if not model_config_file.exists():
        with open(model_config_file, "w") as f:
            json.dump(default_model_config, f)
            typer.echo("Model configuration file created successfully.")
    else:
        typer.echo("Model configuration file already exists.")

    # Initialize the .env file
    env_file = Path(".env")

    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write("OPENAI_API_KEY=\n")
            typer.echo(
                ".env file created successfully. Please fill in the OPENAI_API_KEY."
            )
    else:
        typer.echo(".env file already exists.")


def prompt_for_book_config():
    book_title = typer.prompt("Please enter the book title")
    description = typer.prompt("Please provide a brief description of the book")
    words = typer.prompt(
        "Please enter the number of words you want each chapter to contain", type=int
    )
    image = typer.prompt("Please enter an image description for the book cover")
    chapter_count = typer.prompt(
        "Please enter the number of chapters you want the book to have", type=int
    )

    config = {
        "book_title": book_title,
        "description": description,
        "words": words,
        "image": image,
        "chapter_count": chapter_count,
    }
    return config


@app.command()
def create_topics_and_chapters():
    """
    Create chapters for your book
    """
    model_config_file = Path("model_config.json")
    book_config_file = Path("book_config.json")
    env_file = Path(".env")

    if not model_config_file.exists() or not env_file.exists():
        typer.echo("Config files are not present.")
        init_config()

    config = None
    regenerate = False
    if book_config_file.exists():
        regenerate = typer.confirm("Do you want to update the book_config.json file?")
        if regenerate:
            config = prompt_for_book_config()
        else:
            with open(book_config_file, "r") as f:
                config = json.load(f)

    if config is None:
        typer.echo(
            "The book_config.json file is not present. Please enter the book details."
        )
        config = prompt_for_book_config()

    gen = BookGenerator()

    regenerate_chapters = False
    if config and not regenerate:
        gen.load_chapters()
        if gen.chapters:
            regenerate_chapters = typer.confirm(
                "Chapters already exist. Do you want to regenerate them?"
            )

    if not gen.chapters or regenerate_chapters:
        gen.initialize_book(
            config["book_title"],
            config["description"],
            config["words"],
            config["image"],
        )
        gen.generate_chapters(config["chapter_count"])
        gen.save_chapters()

        with open(book_config_file, "w") as f:
            json.dump(config, f)
            typer.echo("Book configuration file updated successfully.")

        typer.echo(
            f"Chapters for the book {config['book_title']} generated successfully: {gen.chapters}"
        )


@app.command()
def create_book():
    """
    Create Book from your commandline
    """
    config_file = Path("book_config.json")
    chapters_file = Path("chapters.json")  # Assumes chapters are saved in a JSON file

    if not config_file.exists():
        typer.echo("Please run the 'create-topics-and-chapters' command first.")
        return

    if not chapters_file.exists():
        typer.echo(
            "Chapters have not been generated. Please run the 'create_chapters' command first."
        )
        return

    with open(config_file, "r") as f:
        config = json.load(f)

    book_title = config.get("book_title")

    gen = BookGenerator()
    gen.load_chapters()

    gen.generate_text()
    typer.echo("Text for the chapters generated successfully.")
    gen.create_markdown(book_title=book_title)
    typer.echo(f"Markdown file {book_title}.md created successfully.")


@app.command()
def create_pdf():
    """
    Create PDF from Markdown file
    """
    gen = BookGenerator()
    gen.convert_markdown_to_pdf()


@app.command()
def generate_image():
    """
    Generate an image based on a text description provided by the user.
    """
    gen = BookGenerator()

    image_description = typer.prompt("Please enter a text description for the image")
    image_url = gen.get_image_url(image_description)

    image_file_name = typer.prompt("Please enter a name for the image file")
    image_path = Path(gen.download_image(image_url, image_file_name))

    if image_path.exists():
        typer.echo(f"Image created successfully and saved as {image_path}")
    else:
        typer.echo("Something went wrong, the image could not be saved.")
