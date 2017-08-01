import sys
import os
import urllib

# We must add .. to the path so that we can perform the
# import of open-worm-analysis-toolbox while running this as
# a top-level script (i.e. with __name__ = '__main__')
sys.path.append('..')

from zenodio.deposition import Deposition

ACCESS_TOKEN  = 'n2vW3bQz2mVHzGL3KiSrVZzqtAv8Wv3kGE3fOdfkXTlxFserY47r9TASG1Hx'

book_path = 'WealthOfNations.pdf'
urllib.request.urlretrieve(
    "http://www.ibiblio.org/ml/libri/s/SmithA_WealthNations_p.pdf",
    book_path)

book_metadata = {"metadata": {
    "title": "An Inquiry into the Nature and Causes of the Wealth of Nations",
    "upload_type": "publication",
    "publication_type": "book",
# Note: due to a Zenodo bug we cannot use a date prior to 1900, so we cannot
# use the correct publication data of 1776-03-09.
    "publication_date": "1976-03-09",
    "description": "A description of what builds nations' wealth.",
    "creators": [{"name": "Smith, Adam",
                  "affiliation": "University of Glasgow"}]
    }}

# NOTE: Smith's ACCESS_TOKEN is not specified here. He would have to follow
# these steps: https://zenodo.org/dev#restapi-auth to obtain a value.
d = Deposition(ACCESS_TOKEN, use_sandbox=True)
d.append_file(book_path)
d.metadata = book_metadata
d.publish()
# Remove the PDF we downloaded
os.remove(book_path)