#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
List files in RSpace

@author: Emil Frang Christiansen (emil.christiansen@ntnu.no)
Created 2025-01-16
"""

import argparse
import os
import tabulate

from rspace_client import ELNClient


def list_documents(client: ELNClient, *args, **kwargs) -> list:
    """
    List files in RSpace

    Parameters
    ----------
    client : ELNClient
        RSpace ELNClient object
    args : list
        Optional positional arguments passed to client.get_documents()
    kwargs : dictionary
        Optional keyword arguments passed to client.get_documents()

    Returns
    -------
    documents : list
        The list of documents found in RSpace.

    """

    response = client.get_documents(*args, **kwargs)
    n_docs = response["totalHits"]
    print(f"There are {n_docs} documents on RSpace")
    documents = []
    i = 0
    while True:
        kwargs.update({"page_number": i})
        response = client.get_documents(*args, **kwargs)
        if len(response["documents"]) == 0:
            break
        documents += response["documents"]
        i += 1
    print(f"Retrieved information about {len(documents)} documents")

    return documents


def print_documents(documents: list, *args, **kwargs) -> None:
    """
    Print a table of documents found in RSpace

    Parameters
    ----------
    documents : list
        A list of documents to tabulate. Each element should be a dictionary as returend by ELNClient.get_documents()
    args: list
        Optional positional arguments passed to tabulate.tabulate()
    kwargs : dictionary
        Optional keyword arguments passed to tabulate.tabulate()

    Returns
    -------

    """
    table = tabulate.tabulate(
        [
            [document["id"], document["name"], document["created"]]
            for document in documents
        ],
        headers=["ID", "Name", "Created"],
        *args,
        **kwargs,
    )
    print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

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

    args = parser.parse_args()

    if args.api_key is None:
        try:
            api_key = os.getenv("RSPACE_API_KEY")
        except KeyError as e:
            raise ValueError(f"Could not get API key from environment variable") from e
    else:
        api_key = args.api_key

    client = ELNClient(args.rspace_url, api_key)

    documents = list_documents(client)

    print_documents(documents)
