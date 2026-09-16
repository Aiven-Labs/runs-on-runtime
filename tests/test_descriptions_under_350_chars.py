import json
import pathlib


def tests_description_char_lengths():
    """
    Loads the manafest and checks whether the descriptions are all under 350 chars

    There is no need to check against the Github description because the it is limited to 350 on their end.
    """

    manifest = json.loads(pathlib.Path("data/manifest.json").read_text())
    too_long_entries = [
        record for record in manifest if len(record.get("description", "")) > 350
    ]
    assert not too_long_entries
