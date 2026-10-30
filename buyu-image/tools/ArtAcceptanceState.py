"""Reuse acceptance only while every recorded production input is byte-identical."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parent.parent

def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def accepted_unchanged(root=ROOT):
    report = Path(root) / 'docs/UNITY_FINAL_ACCEPTANCE.json'
    if not report.is_file(): return False
    data = json.loads(report.read_text(encoding='utf-8-sig'))
    return bool(data.get('accepted') and data.get('inputHashes') and all(
        (Path(root)/name).is_file() and digest(Path(root)/name)==value
        for name,value in data['inputHashes'].items()))

def preserve_accepted(root=ROOT):
    if not accepted_unchanged(root): return False
    print(json.dumps({'acceptedInputsUnchanged':True,'operation':'No-op; preserve current final acceptance. Change production inputs and reaccept before refreshing.'}))
    return True
