#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Create a document on RSpace.

Either add the text in this code () or pass a markdown or json file as input to convert them to html syntax and add them to RSpace.

@author: Emil Frang Christiansen (emil.christiansen@ntnu.no)
Created 2025-01-16
"""

import argparse
import os
from pathlib import Path
from typing import List, Union
import markdown
import json2html

from rspace_client.eln.eln import ELNClient


def create_document(
    client: ELNClient,
    name: str,
    text: str,
    tags: Union[str, List[str]] = None,
    parent_id: int = None,
) -> list:
    """
    Create a RSpace document

    Parameters
    ----------
    client : ELNClient
        RSpace ELNClient object
    name : str
        The name of the document
    text : str
        Content of the document. HTML syntax is accepted.
    tags: List[str], Optional.
        A list of RSpace tags. The tag "API" will always be added.
    parent_id: int, Optional.
        Where to put the document. Should be the ID of a folder or notebook.

    Returns
    -------
    response : dict
        The response from the RSpace client after creating the document.
    """

    response = client.get_documents()
    n_docs = response["totalHits"]
    print(f"There are {n_docs} documents on RSpace before creating the document.")

    if tags is None:
        tags = ["API"]

    if isinstance(tags, str):
        tags = [tags]

    if not "API" in tags:
        tags.append("API")

    document = client.create_document(
        name=name, fields=[{"content": text}], tags=tags, parent_folder_id=parent_id
    )
    print(f'Created document with ID: {document["id"]}')

    response = client.get_documents()
    n_docs = response["totalHits"]
    print(f"There are {n_docs} documents on RSpace after creating the document.")

    return document


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("name", type=str, help="The name of the document")

    parser.add_argument(
        "--rspace_url", type=str, default=r"https://rspace.ntnu.no/", help="URL to ELN"
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default=None,
        help="User API key to access ELN. Be careful how you use this, as the key should be treated the same as your "
        'password! If not provided, it will look for it in an environment variable called "RSPACE_API_KEY". See '
        "the official RSpace API documentation on how to set the API key in an environment variable and keep it "
        "secure.",
    )

    parser.add_argument(
        "-s",
        "--source",
        type=Path,
        default=None,
        help="Path to a source document. It should either be plain text (with html syntax), a markdown file, or a json file. JSON files will be rendered as tables, whereas markdown files will be converted to html syntax.",
    )

    parser.add_argument(
        "-t",
        "--tags",
        type=str,
        default=None,
        nargs="+",
        help="List of tags to add to the document. The API tag is always added.",
    )

    parser.add_argument(
        "-i",
        "--parent_id",
        type=int,
        default=None,
        help="Where to put the document. Should be the ID of a folder or notebook.",
    )

    parser.add_argument(
        "-p",
        "--print",
        action="store_true",
        help="Whether to print the document to stdout",
    )

    parser.add_argument(
        "-d",
        "--dry",
        action="store_true",
        help="Whether to perform a dry run without uploading/creating the document on RSpace. Useful for only printing the html content with `--print`",
    )

    args = parser.parse_args()

    if args.api_key is None:
        try:
            api_key = os.getenv("RSPACE_API_KEY")
        except KeyError as e:
            raise ValueError(f"Could not get API key from environment variable") from e
    else:
        api_key = args.api_key

    client = ELNClient(args.rspace_url, api_key)

    if args.source is None:
        text = ""  # Enter text of document here.

        # Example text:
        # text = "<h1> My First API Document </h1><p>This is a document that was created with the Python API of RSpace. I can put HTML code here to e.g. <em>emphasize</em> text or put them in <strong>bold</strong>. I can also add lists that are useful for <ul><li>Organizing my thoughts</li><li>Listing results</li><li>Remembering stuff</li></ul>"
    else:
        text = args.source.read_text()
        if args.source.suffix == ".md":
            text = markdown.markdown(
                text,
                extensions=[
                    "tables",
                    "sane_lists",
                    "fenced_code",
                    "pymdownx.arithmatex",
                ],
            )  # More extenstions can be added if required. The sky is the limit!!
        elif args.source.suffix == ".json":  # To render json files as tables
            text = json2html.json2html.convert(text)

    if args.print or args.dry:
        print(text)

    if not args.dry:
        document = create_document(
            client, args.name, text, args.tags, parent_id=args.parent_id
        )
