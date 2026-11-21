# v0.12.1 (1/1): Claude 앱 안(아티팩트)에서 세이브 파일 내보내기  (data.js · ui_panels.js)
#  v0.12 를 올릴 때 게시 쪽이 알려 준 것: 아티팩트 화면에서는 페이지가 시작하는 내려받기(<a download> · blob)와 공유 창(Web Share)이 막혀 있다.
#  그래서 그 안에서는 [파일로 저장]을 눌러도 아무 일이 없는데 "파일로 내보냈습니다"라고 떴다(틀린 알림).
#   - 아티팩트 안인지(window.claude.use 가 있는지)를 보고, 그 안에서는 파일을 downloads 기능으로 내보낸다:
#       claude.use('downloads') → save({ filename, data }). 보는 사람이 확인하면 저장된다(Claude iOS 앱에서는 공유 창이 열린다고 문서에 적혀 있다).
#       기능이 없으면(null) [파일로 내보내기] 단추를 내지 않고 그렇다고 적는다. 준비되는 동안은 '준비하는 중…'.
#   - 아티팩트 안에서는 공유 창(Web Share) 단추를 내지 않는다(주소 [보내기] · 세이브 [보내기]) — 막혀 있는 길이다.
#   - 밖(앱 주소 · 브라우저)에서는 v0.12 와 같다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var GAME_VERSION = 'v0.12';", "var GAME_VERSION = 'v0.12.1';")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "function saveFileObj(p) {",
           "/* Claude 아티팩트 안인가(v0.12.1). 그곳에서는 공유 창과 페이지가 시작하는 내려받기가 막혀 있고, 파일은 downloads 기능으로만 내보낼 수 있다.\n"
           "   DLCAP: undefined = 아직 묻지 않음 · 0 = 묻는 중 · null = 쓸 수 없음 · 객체 = downloads(그 save 를 부른다) */\n"
           "var DLCAP;\n"
           "function inClaude() { try { return !!(window.claude && typeof window.claude.use === 'function'); } catch (e) { return false; } }\n"
           "function dlCapAsk(cb) {\n"
           "  if (DLCAP !== undefined) return;\n"
           "  if (!inClaude()) { DLCAP = null; return; }\n"
           "  DLCAP = 0;\n"
           "  var done = function (ns) { DLCAP = ns && typeof ns.save === 'function' ? ns : null; if (cb) cb(); };\n"
           "  try { window.claude.use('downloads').then(done, function () { done(null); }); } catch (e) { done(null); }\n"
           "}\n"
           "function saveFileObj(p) {")
s = rep(s, "  var st = { id: '' }, game = inGame();\n  showDialog({\n    render: function () {\n      var h = dlgHead('세이브 파일 보내기')",
           "  var st = { id: '' }, game = inGame(), dlg;\n  dlCapAsk(function () { if (MODAL === dlg) refreshDialog(); });\n  showDialog(dlg = {\n    render: function () {\n      var h = dlgHead('세이브 파일 보내기')")
s = rep(s, "        var kb = Math.max(1, Math.round(p.text.length / 1024)), can = canShareFile(saveFileObj(p));\n",
           "        var kb = Math.max(1, Math.round(p.text.length / 1024)), inC = inClaude(), can = !inC && canShareFile(saveFileObj(p)), fileBtn;\n"
           "        if (!inC) fileBtn = '<button class=\"cmd' + (can ? '' : ' pri') + '\" type=\"button\" data-a=\"sdown\"><b>파일로 저장</b><small>' + p.name + ' · 약 ' + kb + 'KB</small></button>';\n"
           "        else if (DLCAP) fileBtn = '<button class=\"cmd pri\" type=\"button\" data-a=\"sdown\"><b>파일로 내보내기</b><small>저장하거나 다른 앱으로 보냅니다 · 약 ' + kb + 'KB</small></button>';\n"
           "        else fileBtn = DLCAP === 0 ? '<button class=\"cmd\" type=\"button\" disabled><b>파일로 내보내기</b><small>준비하는 중…</small></button>' : '';\n")
s = rep(s, "          '<button class=\"cmd' + (can ? '' : ' pri') + '\" type=\"button\" data-a=\"sdown\"><b>파일로 저장</b><small>' + p.name + ' · 약 ' + kb + 'KB</small></button>' +\n",
           "          fileBtn +\n")
s = rep(s, "(can ? '' : ' 이 화면에서는 공유 창에 파일을 실을 수 없어 저장 · 복사만 됩니다.') + '</p>';",
           "(inC ? (DLCAP === null ? ' <b class=\"bad\">이 화면에서는 파일로 내보낼 수 없습니다</b> — [글자로 복사]를 쓰거나 앱 주소(' + SHARE_URL + ')에서 여세요.' : '') : (can ? '' : ' 이 화면에서는 공유 창에 파일을 실을 수 없어 저장 · 복사만 됩니다.')) + '</p>';")
s = rep(s, "      sdown: function () { var p = saveFileText(st.id); if (p && saveDownload(p)) toast('파일로 내보냈습니다 — 내려받은 파일을 보내면 됩니다', 2800); else toast('이 화면에서는 파일을 내보낼 수 없습니다 — [글자로 복사]를 쓰세요', 3200); },",
           "      sdown: function () {\n"
           "        var p = saveFileText(st.id); if (!p) return;\n"
           "        if (inClaude()) {                                           // 아티팩트 안: downloads 기능으로(보는 사람이 확인해야 저장된다)\n"
           "          var no = function () { toast('파일을 내보내지 못했습니다 — [글자로 복사]를 쓰세요', 3200); };\n"
           "          if (!DLCAP) return no();\n"
           "          try { DLCAP.save({ filename: p.name, data: p.text }).then(function () { toast('파일을 내보냈습니다', 2400); }, function (e) { var c = e && e.code; if (c === 'declined') return; if (c === 'rate_limited') toast('잠시 뒤에 다시 눌러 주세요', 2400); else no(); }); } catch (e) { no(); }\n"
           "          return;\n"
           "        }\n"
           "        if (saveDownload(p)) toast('파일로 내보냈습니다 — 내려받은 파일을 보내면 됩니다', 2800); else toast('이 화면에서는 파일을 내보낼 수 없습니다 — [글자로 복사]를 쓰세요', 3200);\n"
           "      },")
# 주소 공유 창: 아티팩트 안에서는 [보내기](Web Share)를 내지 않는다
s = rep(s, "        '<div class=\"cmds ' + (navigator.share ? 'c2' : 'c1') + '\"><button class=\"cmd pri\" type=\"button\" data-a=\"copy\"><b>주소 복사</b></button>' + (navigator.share ? '<button class=\"cmd\" type=\"button\" data-a=\"send\"><b>보내기</b><small>앱 고르기</small></button>' : '') + '</div>' +",
           "        '<div class=\"cmds ' + (navigator.share && !inClaude() ? 'c2' : 'c1') + '\"><button class=\"cmd pri\" type=\"button\" data-a=\"copy\"><b>주소 복사</b></button>' + (navigator.share && !inClaude() ? '<button class=\"cmd\" type=\"button\" data-a=\"send\"><b>보내기</b><small>앱 고르기</small></button>' : '') + '</div>' +")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
