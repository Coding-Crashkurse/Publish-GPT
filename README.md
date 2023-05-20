# PublishGPT

PublishGPT is a command-line tool that allows you to create books using the OpenAI's GPT-3 model.

## Features

* Prompts for book details (title, description, number of words per chapter, image description, and number of chapters).
* Generates chapter suggestions using GPT-3.
* Generates text for each chapter using GPT-3.
* Converts the generated text into Markdown format.
* Converts the Markdown format into PDF.
* Generates an image based on a provided text description.

## How to use

1. Ensure Python 3.8 or above is installed on your machine.
2. IInstall Poetry, a tool for Python project and dependency management.
3. Install the required packages using poetry install.
4. Set your OpenAI API key in the `.env` file.
5. Use the commands provided by the `typer` CLI to create your book. Here are the available commands:

   * `init_config`: Initialize the `config.json` and `.env` files.
   * `create_topics_and_chapters`: Create chapters for your book.
   * `create_book`: Create the book from your command line.
   * `create_pdf`: Create a PDF from a Markdown file.
   * `generate_image`: Generate an image based on a text description.

## Limitations

Please note that the GPT-3 API usage is billed by OpenAI, and significant usage of this tool may result in charges from OpenAI. Also, the quality of the generated text and images depends on the capabilities of the GPT-3 model.

## Future Enhancements

Service will be refactored and pushed to pypi as soon as it is possible.