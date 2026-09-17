import pytest

from github import enrich_manifest


def test_description_char_lengths():
    """
    enrich_manifest raises ValueError for any entry whose description
    (manifest-supplied or GitHub-fetched) is over 350 chars.

    There is no need to check against the GitHub description because it is
    limited to 350 on their end -- this guards manifest-supplied overrides.
    """

    entry = {
        "name": "Too Long",
        "owner": "aiven-labs",
        "repo": "runs-on-runtime",
        "description": "x" * 351,
    }

    with pytest.raises(ValueError, match="Too Long"):
        enrich_manifest([entry])
