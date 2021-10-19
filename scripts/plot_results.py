"""Python script for plotting result data from wrk2."""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import argparse
import csv
import os

import matplotlib.pyplot as plt

data_dict = {}

parser = argparse.ArgumentParser(description="Graphing script for wrk2_wrapper.sh")
parser.add_argument("--input_files", "-if", nargs="+", help="CSV output files from wrk_wrapper.sh")
parser.add_argument(
    "--output_file", "-of", type=str, help="The file in which the Matplotlib graph will be saved"
)


def check_for_file(filename: str) -> bool:
    """Check if a file exists."""
    return os.path.exists(filename)


def read_file(file_desc: str) -> csv.DictReader:
    """Given a filename return a csv.DictReader object."""
    return csv.DictReader(file_desc)


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[: -len(suffix)]
    return input_string


def remove_prefix(input_string, prefix):
    if prefix and input_string.endswith(prefix):
        return input_string[len(prefix) :]
    return input_string


def process_file(filepath: str, data_dict: dict) -> None:
    """Read a CSV file and iterate through all rows.

    Stores all records in an in-memory dict.
    """
    # We're expecting the node_name in the file path
    # e.g., test-result-10.0.3.128.csv
    filename = filepath.split("/")[-1]
    no_ext = remove_suffix(filename, ".csv")
    node_name = remove_prefix(no_ext, "test-result-")

    with open(filepath, newline="") as open_file:
        dict_reader = read_file(file_desc=open_file)
        for row in dict_reader:
            _rps = row.get("Requests Per Second")
            dict_title = f"{_rps} - {node_name}"
            rps = data_dict.get(dict_title)

            if rps:
                # it exists, append
                rps["percentile"].append(float(row.get("Percentile")))
                rps["latency"].append(float(row.get("Value (ms)")))
            else:
                data_dict[dict_title] = {}
                data_dict[dict_title]["percentile"] = [float(row.get("Percentile"))]
                data_dict[dict_title]["latency"] = [float(row.get("Value (ms)"))]


def generate_plot(data_dict: dict, output_file: str):
    """Use matplotlib.pyplot to generate a graph from the given data dictionary."""

    for k, v in data_dict.items():
        plt.plot(v["percentile"], v["latency"], label=str(k), alpha=0.7)

        plt.suptitle(
            "API Server latency distribution by percentile",
            fontsize=14,
        )
        plt.xlabel("Percentile")
        plt.ylabel("Latency in MS")
        plt.legend(loc="center left", bbox_to_anchor=(1, 0))
        plt.grid()
        plt.savefig(output_file, bbox_inches="tight")


if __name__ == "__main__":
    # Create an empty container for results
    data_dict = {}

    args = parser.parse_args()

    for file in args.input_files:
        if check_for_file(file):
            process_file(filepath=file, data_dict=data_dict)
        else:
            print(f"Cannot find file {file}")

    if data_dict:
        generate_plot(data_dict=data_dict, output_file=args.output_file)
