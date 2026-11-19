# CDN 판(아티팩트에 올리는 파일)이 뜨는지: 정상 / 첫 주소 실패 / 모두 실패
from browser import *
def steps(pg):
    if os.environ.get('CDN') == 'failall': print('failall body:', pg.evaluate('document.body.innerText.slice(0, 60)')); return
    start(pg, 0); print(os.environ.get('CDN'), 'ok', pg.evaluate('[!!window.THREE, THREE.REVISION, dateStr(), R3.ready]'))
run(steps)
print('ERRORS', [e for e in errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'ERR_FAILED' not in e][:6])
