"""Shared sequential, cached downloader for Samson photos; no automatic 429 retry."""
import contextlib, email.utils, fcntl, hashlib, json, os, shutil, tempfile, time
import urllib.error, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

class SamsonPaused(RuntimeError):
    pass

def is_samson(url):
    return urllib.parse.urlsplit(url).hostname == 's3.ibta.ru'

def valid(path):
    try:
        with Image.open(path) as im: im.verify()
        return True
    except (OSError, ValueError): return False

def download(url, target):
    target = Path(target)
    if valid(target): return
    cache = Path(os.environ.get('WB_SAMSON_CACHE', str(Path(tempfile.gettempdir()) / 'wb-samson-photos')))
    cache.mkdir(parents=True, exist_ok=True)
    cached = cache / (hashlib.sha256(url.encode()).hexdigest() + '.jpg')
    target.parent.mkdir(parents=True, exist_ok=True)
    with (cache / 'download.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if valid(cached):
            shutil.copyfile(cached, target)
            return
        state_path = cache / 'state.json'
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
        if state.get('paused'):
            raise SamsonPaused('Samson downloads stopped after HTTP 429; Retry-After: ' + state.get('retry_after', 'not supplied') + '. Review before resuming; state: ' + str(state_path))
        delay = max(0, state.get('last_finished', 0) + 2 - time.time())
        if delay: time.sleep(delay)
        tmp = cached.with_suffix('.part')
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=35) as response:
                with tmp.open('wb') as out: shutil.copyfileobj(response, out)
            if not valid(tmp): raise ValueError('Downloaded file is not a valid image')
            tmp.replace(cached)
            shutil.copyfile(cached, target)
        except urllib.error.HTTPError as error:
            if error.code == 429:
                value = error.headers.get('Retry-After', '')
                state.update(paused=True, retry_after=value)
                try:
                    until = time.time() + float(value)
                except ValueError:
                    try: until = email.utils.parsedate_to_datetime(value).timestamp()
                    except (TypeError, ValueError): until = None
                state['resume_not_before'] = until
                raise SamsonPaused('HTTP 429: downloads stopped; Retry-After: ' + (value or 'not supplied')) from error
            raise
        finally:
            state['last_finished'] = time.time()
            state_path.write_text(json.dumps(state))
            with contextlib.suppress(FileNotFoundError): tmp.unlink()
