"""Unpack retained Ubuntu GUI dependencies without NTFS symbolic links."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parent
DEST=(ROOT/'dependencies/linux-root').resolve()
DEST.mkdir(parents=True,exist_ok=True)
records=[]
for package in sorted((ROOT/'dependencies').glob('*.deb')):
    source='/mnt/'+package.drive[0].lower()+'/'+package.as_posix()[3:]
    payload=subprocess.run(['wsl.exe','-d','Ubuntu','--exec','/usr/bin/dpkg-deb','--fsys-tarfile',source],check=True,capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(payload),mode='r:') as archive:
        count=0
        for entry in archive.getmembers():
            if not (entry.isfile() or entry.issym() or entry.islnk()):continue
            target=(DEST/entry.name).resolve()
            if not target.is_relative_to(DEST):raise RuntimeError('Package path leaves local dependency directory')
            stream=archive.extractfile(entry)
            if stream is None:continue
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(stream.read())
            count+=1
    records.append({'package':package.name,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'files':count,'links_materialized_as_regular_files':True})
(ROOT/'dependencies/manifest.json').write_text(json.dumps({'source':'Ubuntu noble amd64 packages, obtained by apt-get download; original packages and copyright notices retained','system_install_performed':False,'records':records,'files_deleted':0},indent=2),encoding='utf-8')
print(json.dumps(records))
