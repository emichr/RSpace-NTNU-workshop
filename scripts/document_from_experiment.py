#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Upload files and create a summary document in RSpace.

Be careful when using this script in other scripts and inputting the user API key rather than fetching it from an
environment variable! See the official RSpace API documentation for more information on how to keep your RSpace
access secure.

This script will upload data "flat" to the gallery. This is a WIP, and it is intended eventually to sort the uploaded
data into folders.

@author: Emil Frang Christiansen (emil.christiansen@ntnu.no)
Created 2024-11-05
"""

import argparse
import os
import logging
import sys
import datetime
import markdown
import json2html

from rspace_client.eln.eln import ELNClient
from pathlib import Path
from typing import Union, Dict, Iterable
from tabulate import tabulate

logger = logging.Logger(__file__)

# Create formatter
format_string = "%(asctime)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(format_string)

# Set up initial logging
logging.basicConfig(format=format_string, level=logging.ERROR)
logging.captureWarnings(True)

# Create custom logger
logger = logging.getLogger(__file__)
logger.propagate = False

# Create handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logger.setLevel(ch.level)

# Add formatter to handler
ch.setFormatter(formatter)

# Add handler to logger
logger.addHandler(ch)

logger.info(f"This is {__file__} working from {os.getcwd()}:\n{__doc__}")


def file2html(filename: Union[str, Path]) -> str:
    """
    Read a file and return a html representation

    Formats markdown and json files especially. Other files are just returned as-is.

    Arguments
    ---------
    filename: Union[str, Path]
        The path of the file

    Returns
    -------
    text : str
        A string with the contents formatted as html
    """

    filename = Path(filename)

    if filename.exists():
        if filename.is_file():
            text = filename.read_text()
            logger.debug(f"Read text {text} from file {filename}")
            if filename.suffix == ".md":
                logger.debug(f"Formatting markdown text as html")
                text = markdown.markdown(text)
            elif filename.suffix == ".json":
                logger.debug(f"Converting .json text to html")
                text = json2html.json2html.convert(text)
        else:
            raise ValueError(f"File {filename.absolute()} is not a file")
    else:
        raise ValueError(f"File {filename.absolute()} does not exist")

    return text


def list_files(directory: Union[str, Path], process_subdir: bool = True) -> list:
    """
    List the files in a directory.

    Be careful using this with `process_subdir=True` on folders high in a tree.

    Arguments
    ---------
    directory : Union[str, Path]
        The directory to process
    process_subdir : bool, optional
        Whether to include files found in subdirectories as well. Default is True

    Returns
    -------
    files : list
        A list of files in the directory. If `process_subdir=True`, the list also includes files in subdirectories.
    """

    directory = Path(directory)
    logger.debug(f"Processing directory {directory}...")
    files = []
    if directory.is_dir() and directory.exists():
        for child in directory.iterdir():
            logger.debug(f"Processing child {child} in {directory}")
            if child.is_dir():
                logger.debug(f"Child {child} is another directory")
                if process_subdir:
                    logger.debug(f"Processing subdirectory {child}")
                    subdir_children = list_files(child, process_subdir=process_subdir)
                    [files.append(subdir_child) for subdir_child in subdir_children]
                else:
                    logger.info(
                        f"Ignoring child {child} in {directory} as it is a subdirectory. If you want to process this "
                        f"subdirectory as well, please provide pass `process_subdir=True` to this function."
                    )
            elif child.is_file():
                logger.debug(f"Child {child} is a file, processing it.")
                files.append(child)
            else:
                raise ValueError(
                    f"Could not recognize directory content {child} in {directory.absolute()}"
                )
    else:
        raise ValueError(
            f"Cannot process directory {directory.absolute()}. It is either not a directory or does not exist."
        )
    return files


def response_to_table(response: Union[Iterable, Dict], **kwargs) -> str:
    """
    Format a client response as a table

    Parameters
    ----------
    response : Union[Iterable, Dict]
        The response from a RSpace client

    Returns
    -------
    table : str
        A table with the response details.

    """

    kwargs.update({"headers": kwargs.get("headers", ["Key", "Value"])})
    if isinstance(response, dict):
        return tabulate([[key, response[key]] for key in response], **kwargs)
    else:
        return "\n".join([response_to_table(r, **kwargs) for r in response])


def upload_file_from_path(
    client: ELNClient, path: Union[str, Path], filesize_limit=2.0
) -> Dict:
    """
    Upload a file to RSpace, preserving the folder structure as far as it is given in the path
    .
    Parameters
    ----------
    client : ELNClient
        The client to use to upload files
    path : Union[str, Path]
        The path to the file to upload
    filesize_limit : float
        The maximum file size in MB to upload

    Returns
    -------
    response : Dict
        The upload response from the API

    Raises
    ------
    ValueError if filesize exceeds filesize limit.
    """

    path = Path(path)

    if path.stat().st_size * 1e-6 <= filesize_limit:
        logger.debug(
            f"Uploading file {path} of filesize {path.stat().st_size * 1E-6} MB"
        )
        with path.open("rb") as f:
            upload_response = client.upload_file(
                f,
                caption=f'Uploaded from "{path.absolute()} at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            )
        logger.info(
            f'Uploaded file "{path}" with global ID:\n{response_to_table(upload_response)}'
        )
        return upload_response
    else:
        raise ValueError(
            f'Cannot upload file from path "{path}" with filesize {path.stat().st_size * 1E-6} MB as it is larger than threshold {filesize_limit} MB'
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="Path to the experiment directory")
    parser.add_argument("--ignore", type=str, nargs="?", help="Filetypes to ignore")
    parser.add_argument(
        "--max_filesize",
        type=float,
        default=2.0,
        help="Maximum individual filesize to upload in MB.",
    )
    parser.add_argument(
        "--location",
        type=str,
        help="The id of the location to put the document. E.g. the ID of a notebook or a folder.",
    )
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
        "--tags",
        type=str,
        nargs="?",
        default=["API"],
        help="Tags to associate with the form",
    )
    parser.add_argument(
        "-v", "--verbosity", action="count", default=0, help="Increase the verbosity"
    )

    args = parser.parse_args()

    if args.ignore is None:
        ignore_files = []
    else:
        ignore_files = args.ignore

    if args.verbosity == 0:
        logger.setLevel(30)  # WARNING
    elif args.verbosity == 1:
        logger.setLevel(20)  # INFO
    else:
        logger.setLevel(10)  # DEBUG

    logger.debug(f"Got input arguments: {args}")

    if args.api_key is None:
        logger.debug("Getting API key from environment variable")
        api_key = os.getenv("RSPACE_API_KEY")
    else:
        api_key = args.api_key

    client = ELNClient(args.rspace_url, api_key)

    files = list_files(args.path)

    document = (
        ""  # Variable to store the document contents to be created on RSpace server
    )
    document += f"<h1>Autogenerated document for {args.path}</h1>\n"
    document += f"<h2>List of files</h2>\n"
    document += f"<div>\n<ul>\n\t"

    logger.debug("Uploading files")
    uploaded_files = []
    for file in files:
        if file.suffix in ignore_files:
            logger.debug(
                f"Ignoring file {file} as it's filetype is ignored (one of {ignore_files})"
            )
            pass
        else:
            try:
                uploaded_file = upload_file_from_path(client, file, args.max_filesize)
                uploaded_files.append(uploaded_file)
            except Exception as e:
                logger.info(
                    f"Ignoring file {file} due to error {e}\nAdding the file information to the summary document "
                    f"anyways."
                )
                document += f"<li>{file} ({file.stat().st_size * 1E-6} MB > {args.max_filesize} MB) </li>\n"
            else:
                document += f"<li>{file}: <fileId={uploaded_file['id']}></li>\n"

    document += f"</ul>\n</div>\n"

    for file in files:
        try:
            document += f"<hr>```{file}```\n{file2html(file)}\n<hr>"
        except Exception as e:
            logger.error(e)
            logger.info(f"Did not append file contents of {file} to document text.")

    logger.info(
        f"""
Finished uploading files.
Will now create document

*** DOCUMENT CONTENT START ***
{document}
*** DOCUMENT CONTENT END ***

"""
    )

    response = client.create_document(
        name=args.path.stem,
        parent_folder_id=args.location,
        tags=args.tags,
        fields=[{"content": document}],
    )
    logger.info(f"Created document {response_to_table(response)}")
