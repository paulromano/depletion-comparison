from tempfile import TemporaryDirectory
from pathlib import Path
import zipfile

from openmc._utils import download


filename = {
    'decay': 'sss_endfb71.dec',
    'nfy': 'sss_endfb71.nfy'
}

md5s = {
    'decay': 'ad346888d55427c3f25d39f7fed3e659',
    'nfy': '0420894a296871cd08f68def84526d0e',
}

with TemporaryDirectory() as tmpdir:
    for sublib in ('decay', 'nfy'):
        # download and extract from zip file
        download(
            f'https://www.nndc.bnl.gov/endf/b7.1/zips/ENDF-B-VII.1-{sublib}.zip',
            checksum=md5s[sublib])
        with zipfile.ZipFile(f'ENDF-B-VII.1-{sublib}.zip') as z:
            z.extractall(path=tmpdir)

        # concatenate ENDF files
        with open(filename[sublib], 'w') as out:
            for f in sorted(Path(tmpdir).joinpath(sublib).glob('*.endf')):
                out.write(open(f).read())
