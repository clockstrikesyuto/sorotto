from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from pathlib import Path
from io import BytesIO
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import secrets, random, time, qrcode, asyncio

BASE = Path(__file__).parent
HTML = '<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="theme-color" content="#0c0c0f">\n<title>SOROTTO｜価値観をそろえるゲーム</title>\n<style>\n:root{--bg:#0c0c0f;--card:#17171c;--card2:#222229;--line:#303039;--txt:#f8f8fa;--muted:#aaaab3;--ok:#78dfa0;--bad:#ff7c7c;--r:22px}\n*{box-sizing:border-box}html,body{margin:0;min-height:100%;background:radial-gradient(circle at 10% 0,#282834 0,transparent 30%),radial-gradient(circle at 100% 45%,#20202a 0,transparent 28%),var(--bg);color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Hiragino Sans","Yu Gothic",sans-serif}body{min-height:100svh}.app{max-width:760px;margin:auto;padding:18px 15px 42px}.brand{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}.brandMain{display:flex;gap:10px;align-items:center}.logo{width:45px;height:45px;background:#fff;color:#111;border-radius:14px;display:grid;place-items:center;font-weight:1000}.brand h1{font-size:19px;letter-spacing:.08em;margin:0}.brand small{color:var(--muted)}.pill{border:1px solid var(--line);border-radius:999px;padding:7px 10px;color:#d8d8df;font-size:12px;background:#17171c}.screen{display:none}.screen.on{display:block;animation:in .2s ease}@keyframes in{from{opacity:.25;transform:translateY(5px)}to{opacity:1;transform:none}}.card{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border-radius:var(--r);padding:18px;margin-bottom:12px;box-shadow:0 20px 55px rgba(0,0,0,.28)}.hero{padding:27px 21px}.eyebrow,.smallcaps{font-size:11px;letter-spacing:.14em;font-weight:900;color:var(--muted)}.hero h2,.topic{font-size:clamp(29px,7vw,48px);line-height:1.08;letter-spacing:-.04em;margin:10px 0 13px}.hero p,.hint{color:#d2d2d8;line-height:1.7}.hint{font-size:13px}.btn{width:100%;border:0;border-radius:15px;padding:14px 16px;background:#fff;color:#111;font-weight:900;margin-top:9px}.btn.secondary{background:var(--card2);color:#fff;border:1px solid var(--line)}.btn.ghost{background:transparent;color:#d7d7de;border:1px dashed var(--line)}.btn:disabled{opacity:.4;cursor:not-allowed}input,select{width:100%;background:#101014;color:#fff;border:1px solid var(--line);border-radius:14px;padding:13px 14px;font:inherit;outline:0}label{display:block;font-size:12px;color:var(--muted);margin:0 0 7px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}@media(max-width:520px){.grid{grid-template-columns:1fr}}.code{font-size:64px;font-weight:1000;letter-spacing:.08em;text-align:center;margin:10px 0}.qr{display:block;width:min(240px,70vw);aspect-ratio:1;margin:14px auto;background:#fff;padding:10px;border-radius:18px}.copyline{display:grid;grid-template-columns:1fr 110px;gap:8px}.players{display:grid;gap:8px;margin-top:11px}.player{display:flex;align-items:center;gap:10px;background:#111116;border:1px solid var(--line);padding:11px 12px;border-radius:14px}.dot{width:9px;height:9px;border-radius:50%;background:#7be39f}.axis{display:flex;justify-content:space-between;gap:8px;color:var(--muted);font-size:12px;margin-top:12px}.meter{height:9px;border-radius:999px;background:linear-gradient(90deg,#4b4b55,#fff);margin-top:7px}.number{font-size:100px;font-weight:1000;letter-spacing:-.08em;line-height:1;text-align:center;margin:17px 0}.secret{text-align:center;padding:20px 3px}.order{display:grid;gap:8px;margin-top:11px}.orderrow{display:grid;grid-template-columns:38px 1fr 40px;align-items:center;gap:8px;border:1px solid var(--line);background:#111116;border-radius:14px;padding:9px}.rank{width:32px;height:32px;border-radius:10px;background:#292930;display:grid;place-items:center;font-weight:900}.arrows{display:flex;flex-direction:column;gap:4px}.arrows button{height:22px;border:0;border-radius:6px;background:#2c2c35;color:#fff}.resultrow{display:flex;justify-content:space-between;padding:12px 2px;border-bottom:1px solid var(--line)}.resultrow:last-child{border:0}.actual{font-size:22px;font-weight:1000}.score{font-size:60px;font-weight:1000;text-align:center;letter-spacing:-.05em}.center{text-align:center}.ok{color:var(--ok)}.bad{color:var(--bad)}.status{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);background:#fff;color:#111;border-radius:999px;padding:9px 13px;font-size:12px;font-weight:900;opacity:0;pointer-events:none;transition:.2s}.status.show{opacity:1}.footer{text-align:center;color:#686872;font-size:11px;line-height:1.6;margin-top:18px}.row{display:flex;gap:8px}.row>*{flex:1}\n</style>\n</head>\n<body>\n<div class="app">\n  <div class="brand"><div class="brandMain"><div class="logo">SO</div><div><h1>SOROTTO</h1><small>価値観をそろえるゲーム</small></div></div><div class="pill" id="conn">OFFLINE</div></div>\n\n  <section id="home" class="screen on">\n    <div class="card hero"><div class="eyebrow">MULTIPLAYER PARTY GAME</div><h2>数字は秘密。<br>感覚だけ、そろえよう。</h2><p>各自のスマホに1〜100の数字が届きます。数字そのものは言わず、お題に合う“たとえ”で表現。みんなで小さい順に並べられたら成功。</p></div>\n    <div class="card"><div class="grid"><div><label>お題</label><select id="category"><option value="mix">ごちゃまぜ</option><option value="party">盛り上がり</option><option value="daily">日常</option><option value="love">恋愛・人間関係</option><option value="work">仕事・学校</option></select></div><div><label>ラウンド数</label><select id="rounds"><option>3</option><option selected>5</option><option>7</option><option>10</option></select></div></div><button class="btn" id="create">部屋をつくる</button></div>\n    <div class="card"><label>4桁の部屋コードで参加</label><div class="copyline"><input id="joinCode" inputmode="numeric" maxlength="4" placeholder="1234"><button class="btn secondary" style="margin:0" id="goJoin">参加</button></div></div>\n  </section>\n\n  <section id="join" class="screen">\n    <div class="card hero"><div class="eyebrow">JOIN ROOM</div><div class="code" id="joinCodeBig"></div><p>名前を入力して参加してください。</p></div>\n    <div class="card"><label>あなたの名前</label><input id="playerName" maxlength="18" placeholder="ゆうと"><button class="btn" id="joinBtn">この部屋に参加</button><button class="btn ghost" onclick="location.href=\'/\'">戻る</button></div>\n  </section>\n\n  <section id="host" class="screen">\n    <div id="hostLobby">\n      <div class="card center"><div class="smallcaps">ROOM CODE</div><div class="code" id="hostCode"></div><img class="qr" id="qr"><div class="copyline"><input id="joinUrl" readonly><button class="btn secondary" style="margin:0" id="copyUrl">コピー</button></div><p class="hint">QRコードを読み取るか、URLを送れば参加できます。</p></div>\n      <div class="card"><div class="smallcaps">PLAYERS</div><div class="players" id="hostPlayers"></div><button class="btn" id="start" disabled>2人以上でゲーム開始</button></div>\n    </div>\n    <div id="hostGame" style="display:none"></div>\n  </section>\n\n  <section id="player" class="screen"><div id="playerGame"></div></section>\n  <div class="footer">SOROTTO prototype — オリジナルUI・お題・得点ルールで制作したWebパーティーゲーム。</div>\n</div>\n<div class="status" id="toast"></div>\n<script>\nconst $=s=>document.querySelector(s);const path=location.pathname.split(\'/\').filter(Boolean);let ws=null,role=null,code=null,hostToken=null,playerId=null,playerToken=null,currentOrder=[];\nfunction screen(id){document.querySelectorAll(\'.screen\').forEach(x=>x.classList.remove(\'on\'));$(\'#\'+id).classList.add(\'on\');window.scrollTo(0,0)}\nfunction toast(t){const e=$(\'#toast\');e.textContent=t;e.classList.add(\'show\');setTimeout(()=>e.classList.remove(\'show\'),1500)}\nfunction esc(s){return String(s??\'\').replace(/[&<>"\']/g,m=>({\'&\':\'&amp;\',\'<\':\'&lt;\',\'>\':\'&gt;\',\'"\':\'&quot;\',"\'":\'&#39;\'}[m]))}\nfunction topicCard(t){return `<div class="card"><div class="smallcaps">TODAY\'S SCALE</div><div class="topic">${esc(t.text)}</div><div class="axis"><span>1：${esc(t.low)}</span><span>100：${esc(t.high)}</span></div><div class="meter"></div></div>`}\nasync function api(url,opt={}){const r=await fetch(url,{headers:{\'Content-Type\':\'application/json\'},...opt});if(!r.ok){let j={};try{j=await r.json()}catch{};throw new Error(j.detail||\'通信に失敗しました\')}return r.json()}\n$(\'#create\').onclick=async()=>{try{const d=await api(\'/api/rooms\',{method:\'POST\',body:JSON.stringify({category:$(\'#category\').value,rounds:+$(\'#rounds\').value})});location.href=d.host_url}catch(e){toast(e.message)}};\n$(\'#goJoin\').onclick=()=>{const c=$(\'#joinCode\').value.replace(/\\D/g,\'\');if(c.length!==4)return toast(\'4桁のコードを入力してね\');location.href=\'/join/\'+c};\nfunction parseHostToken(){const m=location.hash.match(/token=([^&]+)/);return m?decodeURIComponent(m[1]):localStorage.getItem(\'sorotto_host_\'+code)}\nasync function initJoin(){screen(\'join\');$(\'#joinCodeBig\').textContent=code;const saved=JSON.parse(localStorage.getItem(\'sorotto_player_\'+code)||\'null\');if(saved?.player_id&&saved?.player_token){playerId=saved.player_id;playerToken=saved.player_token;connectPlayer();return}$(\'#joinBtn\').onclick=async()=>{try{const d=await api(`/api/rooms/${code}/join`,{method:\'POST\',body:JSON.stringify({name:$(\'#playerName\').value})});playerId=d.player_id;playerToken=d.player_token;localStorage.setItem(\'sorotto_player_\'+code,JSON.stringify(d));connectPlayer()}catch(e){toast(e.message)}}}\nfunction initHost(){role=\'host\';hostToken=parseHostToken();if(!hostToken){screen(\'home\');return toast(\'ホスト情報がありません\')}localStorage.setItem(\'sorotto_host_\'+code,hostToken);history.replaceState(null,\'\',`/host/${code}`);screen(\'host\');$(\'#hostCode\').textContent=code;$(\'#qr\').src=`/room/${code}/qr?t=${Date.now()}`;$(\'#joinUrl\').value=location.origin+`/join/${code}`;$(\'#copyUrl\').onclick=async()=>{await navigator.clipboard.writeText($(\'#joinUrl\').value);toast(\'参加URLをコピーしました\')};connect(\'host\')}\nfunction connectPlayer(){role=\'player\';screen(\'player\');connect(\'player\')}\nfunction connect(r){if(ws)try{ws.close()}catch{};const proto=location.protocol===\'https:\'?\'wss\':\'ws\';let url=`${proto}://${location.host}/ws/${code}?role=${r}&token=${encodeURIComponent(r===\'host\'?hostToken:playerToken)}`;if(r===\'player\')url+=`&player_id=${encodeURIComponent(playerId)}`;ws=new WebSocket(url);ws.onopen=()=>{$(\'#conn\').textContent=\'LIVE\';$(\'#conn\').style.color=\'#78dfa0\'};ws.onclose=()=>{$(\'#conn\').textContent=\'RECONNECT\';$(\'#conn\').style.color=\'\';setTimeout(()=>connect(r),1800)};ws.onerror=()=>toast(\'接続を確認しています…\');ws.onmessage=e=>{const d=JSON.parse(e.data);if(d.type===\'error\')return toast(d.message);if(r===\'host\')renderHost(d);else renderPlayer(d)}}\nfunction send(action,extra={}){if(ws?.readyState===1)ws.send(JSON.stringify({action,...extra}))}\nfunction renderPlayers(list){return list.length?list.map(p=>`<div class="player"><span class="dot"></span><strong>${esc(p.name)}</strong></div>`).join(\'\'):`<p class="hint">参加者を待っています…</p>`}\nfunction renderHost(s){\n $(\'#hostPlayers\').innerHTML=renderPlayers(s.players);$(\'#start\').disabled=s.players.length<2;$(\'#start\').textContent=s.players.length<2?\'2人以上でゲーム開始\':`${s.players.length}人でゲーム開始`;$(\'#start\').onclick=()=>send(\'start\');\n if(s.stage===\'lobby\'){ $(\'#hostLobby\').style.display=\'\';$(\'#hostGame\').style.display=\'none\';return }\n $(\'#hostLobby\').style.display=\'none\';$(\'#hostGame\').style.display=\'\';const g=$(\'#hostGame\');\n if(s.stage===\'reveal\') {g.innerHTML=`<div class="card"><div class="smallcaps">ROUND ${s.round} / ${s.max_rounds}</div></div>${topicCard(s.topic)}<div class="card center"><div class="topic">各自の数字を確認中 👀</div><p class="hint">全員が自分のスマホで秘密の数字を確認したら、相談開始。</p><button class="btn" id="discuss">相談をはじめる</button></div>`;$(\'#discuss\').onclick=()=>send(\'discuss\');return}\n if(s.stage===\'discuss\') {currentOrder=(s.order?.length?s.order:s.players.map(p=>p.id)).slice();g.innerHTML=`<div class="card"><div class="smallcaps">ROUND ${s.round} / ${s.max_rounds}</div></div>${topicCard(s.topic)}<div class="card"><div class="smallcaps">小さいと思う順</div><p class="hint">みんなの“たとえ”を聞いて、ホストが順番を並べ替えてください。</p><div class="order" id="order"></div><button class="btn" id="judge">この順番で答え合わせ</button></div>`;renderOrder(s.players);$(\'#judge\').onclick=()=>send(\'judge\',{order:currentOrder});return}\n if(s.stage===\'result\'||s.stage===\'finished\'){const rows=(s.results||[]).map((x,i)=>`<div class="resultrow"><span>${i+1}. ${esc(x.name)}</span><span class="actual">${x.number}</span></div>`).join(\'\');g.innerHTML=`<div class="card"><div class="smallcaps">RESULT</div><div class="topic ${s.perfect?\'ok\':\'bad\'}">${s.perfect?\'PERFECT!\':\'惜しい！\'} +${s.last_gain}pt</div>${rows}</div><div class="card center"><div class="smallcaps">TOTAL SCORE</div><div class="score">${s.score}</div>${s.stage===\'finished\'?\'<p class="hint">全ラウンド終了！</p><button class="btn" id="reset">ロビーに戻る</button>\':`<button class="btn" id="next">${s.round>=s.max_rounds?\'最終結果へ\':\'次のラウンド\'}</button>`}</div>`;if($(\'#next\'))$(\'#next\').onclick=()=>send(\'next\');if($(\'#reset\'))$(\'#reset\').onclick=()=>send(\'reset\');return}\n}\nfunction renderOrder(players){const map=Object.fromEntries(players.map(p=>[p.id,p]));const wrap=$(\'#order\');wrap.innerHTML=currentOrder.map((id,i)=>`<div class="orderrow"><div class="rank">${i+1}</div><strong>${esc(map[id]?.name||\'?\')}</strong><div class="arrows"><button data-up="${i}">▲</button><button data-down="${i}">▼</button></div></div>`).join(\'\');wrap.querySelectorAll(\'[data-up]\').forEach(b=>b.onclick=()=>move(+b.dataset.up,-1,players));wrap.querySelectorAll(\'[data-down]\').forEach(b=>b.onclick=()=>move(+b.dataset.down,1,players))}\nfunction move(i,d,players){const n=i+d;if(n<0||n>=currentOrder.length)return;[currentOrder[i],currentOrder[n]]=[currentOrder[n],currentOrder[i]];renderOrder(players);send(\'order\',{order:currentOrder})}\nfunction renderPlayer(s){const g=$(\'#playerGame\');if(s.stage===\'lobby\'){g.innerHTML=`<div class="card hero center"><div class="eyebrow">ROOM ${s.code}</div><div class="topic">参加完了！</div><p>${esc(s.name)} さん</p><p class="hint">ホストがゲームを始めるまで、この画面で待ってください。</p></div><div class="card"><div class="smallcaps">PLAYERS</div><div class="players">${renderPlayers(s.players)}</div></div>`;return}\n if(s.stage===\'reveal\'||s.stage===\'discuss\'){g.innerHTML=`<div class="card"><div class="smallcaps">ROUND ${s.round} / ${s.max_rounds}</div></div>${topicCard(s.topic)}<div class="card secret"><div class="smallcaps">YOUR NUMBER</div><div class="number">${s.number}</div><p class="hint">この数字はあなただけの秘密。数字そのものは言わず、お題に合う“たとえ”で表現してください。</p>${s.stage===\'reveal\'?\'<div class="pill">みんなが確認中</div>\':\'<div class="pill">相談中</div>\'}</div>`;return}\n if(s.stage===\'result\'||s.stage===\'finished\'){const rows=(s.results||[]).map((x,i)=>`<div class="resultrow"><span>${i+1}. ${esc(x.name)}${x.id===s.player_id?\' ← YOU\':\'\'}</span><span class="actual">${x.number}</span></div>`).join(\'\');g.innerHTML=`<div class="card"><div class="smallcaps">RESULT</div><div class="topic ${s.perfect?\'ok\':\'bad\'}">${s.perfect?\'そろった！\':\'惜しい！\'}</div>${rows}</div><div class="card center"><div class="smallcaps">TEAM SCORE</div><div class="score">${s.score}</div><p class="hint">${s.stage===\'finished\'?\'ゲーム終了！おつかれさま！\':\'ホストが次のラウンドへ進めます。\'}</p></div>`;return}\n}\nif(path[0]===\'join\'&&/^\\d{4}$/.test(path[1]||\'\')){code=path[1];initJoin()}else if(path[0]===\'host\'&&/^\\d{4}$/.test(path[1]||\'\')){code=path[1];initHost()}else screen(\'home\');\n</script>\n</body></html>\n'
app = FastAPI(title="SOROTTO")

TOPICS = {
    "party": [
        ("テンションが上がる瞬間", "全然上がらない", "最高潮"),
        ("もらったら嬉しい差し入れ", "反応に困る", "めちゃ嬉しい"),
        ("休日にやりたいこと", "やりたくない", "最高にやりたい"),
        ("カラオケで盛り上がる曲", "しーん", "大合唱"),
        ("旅行先として行きたい場所", "今はいいかな", "今すぐ行きたい"),
        ("友達に誘われたら嬉しい遊び", "気が乗らない", "即OK"),
        ("宴会で起きたら面白いこと", "微妙", "伝説"),
        ("夏に食べたいもの", "そうでもない", "絶対食べたい"),
    ],
    "daily": [
        ("家にあると便利なもの", "なくても平気", "必需品"),
        ("朝にされたら嬉しいこと", "別に", "最高"),
        ("コンビニでつい買うもの", "ほぼ買わない", "毎回買う"),
        ("疲れた日にしたいこと", "したくない", "絶対したい"),
        ("部屋にほしい設備", "いらない", "絶対ほしい"),
        ("雨の日の過ごし方", "避けたい", "理想"),
        ("夜食として食べたいもの", "重い", "最高"),
        ("一人で行きやすい場所", "ハードル高い", "余裕"),
    ],
    "love": [
        ("デートで行きたい場所", "行きたくない", "めちゃ行きたい"),
        ("恋人にされたら嬉しいこと", "微妙", "キュン"),
        ("付き合う相手に求めること", "なくてもOK", "超重要"),
        ("初デートで話したい話題", "避けたい", "話したい"),
        ("理想の連絡頻度", "少なめ", "かなり多め"),
        ("恋人と一緒にやりたい趣味", "別々でいい", "絶対一緒に"),
        ("告白されるなら嬉しい場所", "ここは嫌", "理想"),
        ("記念日にしたいこと", "なくてもいい", "特別にしたい"),
    ],
    "work": [
        ("仕事ができる人の特徴", "なくてもいい", "超重要"),
        ("会議で言われたら嬉しい一言", "普通", "最高"),
        ("職場にほしい福利厚生", "いらない", "絶対ほしい"),
        ("上司に求める能力", "優先度低め", "最重要"),
        ("学校の授業で役立つもの", "役立ちにくい", "一生使う"),
        ("チームで大切なこと", "まあ大事", "絶対必要"),
        ("休憩時間にしたいこと", "しなくていい", "毎回したい"),
        ("働く場所として魅力的な環境", "避けたい", "理想"),
    ],
}
TOPICS["mix"] = sum(TOPICS.values(), [])

@dataclass
class Player:
    id: str
    token: str
    name: str
    number: Optional[int] = None

@dataclass
class Room:
    code: str
    host_token: str
    category: str = "mix"
    max_rounds: int = 5
    players: Dict[str, Player] = field(default_factory=dict)
    stage: str = "lobby"
    round: int = 0
    topic: Optional[tuple] = None
    order: List[str] = field(default_factory=list)
    score: int = 0
    last_gain: int = 0
    perfect: bool = False
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)

rooms: Dict[str, Room] = {}
connections: Dict[str, List[dict]] = {}

class CreateRoom(BaseModel):
    category: str = "mix"
    rounds: int = 5

class JoinRoom(BaseModel):
    name: str
    player_token: Optional[str] = None


def public_origin(request: Request) -> str:
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    return f"{proto}://{host}".rstrip("/")


def make_code():
    for _ in range(100):
        code = f"{random.randint(0, 9999):04d}"
        if code not in rooms:
            return code
    raise RuntimeError("room code exhausted")


def public_room(room: Room):
    return {
        "code": room.code,
        "stage": room.stage,
        "round": room.round,
        "max_rounds": room.max_rounds,
        "player_count": len(room.players),
    }


def topic_json(room: Room):
    if not room.topic:
        return None
    return {"text": room.topic[0], "low": room.topic[1], "high": room.topic[2]}


def host_state(room: Room):
    results = None
    if room.stage in ("result", "finished"):
        results = [
            {"id": pid, "name": room.players[pid].name, "number": room.players[pid].number}
            for pid in room.order if pid in room.players
        ]
    return {
        "type": "state",
        "role": "host",
        "code": room.code,
        "stage": room.stage,
        "round": room.round,
        "max_rounds": room.max_rounds,
        "score": room.score,
        "last_gain": room.last_gain,
        "perfect": room.perfect,
        "topic": topic_json(room),
        "players": [{"id": p.id, "name": p.name} for p in room.players.values()],
        "order": room.order,
        "results": results,
    }


def player_state(room: Room, pid: str):
    p = room.players.get(pid)
    if not p:
        return {"type": "error", "message": "プレイヤー情報が見つかりません"}
    reveal_number = p.number if room.stage in ("reveal", "discuss") else None
    results = None
    if room.stage in ("result", "finished"):
        results = [
            {"id": oid, "name": room.players[oid].name, "number": room.players[oid].number}
            for oid in room.order if oid in room.players
        ]
    return {
        "type": "state",
        "role": "player",
        "player_id": p.id,
        "name": p.name,
        "code": room.code,
        "stage": room.stage,
        "round": room.round,
        "max_rounds": room.max_rounds,
        "score": room.score,
        "last_gain": room.last_gain,
        "perfect": room.perfect,
        "topic": topic_json(room),
        "number": reveal_number,
        "players": [{"id": x.id, "name": x.name} for x in room.players.values()],
        "results": results,
    }


async def broadcast(code: str):
    room = rooms.get(code)
    if not room:
        return
    room.last_active = time.time()
    alive = []
    for conn in connections.get(code, []):
        ws = conn["ws"]
        try:
            if conn["role"] == "host":
                await ws.send_json(host_state(room))
            else:
                await ws.send_json(player_state(room, conn["player_id"]))
            alive.append(conn)
        except Exception:
            pass
    connections[code] = alive


@app.get("/healthz")
async def healthz():
    return {"ok": True, "rooms": len(rooms)}


@app.get("/")
@app.get("/join/{code}")
@app.get("/host/{code}")
async def site(code: str = ""):
    return HTMLResponse(HTML)


@app.post("/api/rooms")
async def create_room(data: CreateRoom, request: Request):
    category = data.category if data.category in TOPICS else "mix"
    rounds = min(10, max(1, data.rounds))
    code = make_code()
    token = secrets.token_urlsafe(24)
    room = Room(code=code, host_token=token, category=category, max_rounds=rounds)
    rooms[code] = room
    base = public_origin(request)
    return {
        "code": code,
        "host_token": token,
        "host_url": f"{base}/host/{code}#token={token}",
        "join_url": f"{base}/join/{code}",
    }


@app.get("/api/rooms/{code}")
async def room_info(code: str):
    room = rooms.get(code)
    if not room:
        raise HTTPException(404, "部屋が見つかりません")
    return public_room(room)


@app.post("/api/rooms/{code}/join")
async def join_room(code: str, data: JoinRoom):
    room = rooms.get(code)
    if not room:
        raise HTTPException(404, "部屋が見つかりません")
    if room.stage not in ("lobby", "result"):
        raise HTTPException(409, "ラウンド進行中のため、新規参加は次のラウンドまで待ってください")
    name = data.name.strip()[:18]
    if not name:
        raise HTTPException(400, "名前を入力してください")
    if data.player_token:
        for p in room.players.values():
            if secrets.compare_digest(p.token, data.player_token):
                p.name = name
                await broadcast(code)
                return {"player_id": p.id, "player_token": p.token, "name": p.name}
    if len(room.players) >= 12:
        raise HTTPException(409, "この部屋は満員です")
    pid = secrets.token_hex(5)
    token = secrets.token_urlsafe(18)
    room.players[pid] = Player(id=pid, token=token, name=name)
    room.order.append(pid)
    await broadcast(code)
    return {"player_id": pid, "player_token": token, "name": name}


@app.get("/room/{code}/qr")
async def room_qr(code: str, request: Request):
    if code not in rooms:
        raise HTTPException(404, "部屋が見つかりません")
    base = public_origin(request)
    url = f"{base}/join/{code}"
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png", headers={"Cache-Control": "no-store"})


def check_host(room: Room, token: str):
    return token and secrets.compare_digest(token, room.host_token)


def check_player(room: Room, pid: str, token: str):
    p = room.players.get(pid)
    return bool(p and token and secrets.compare_digest(token, p.token))


def start_round(room: Room):
    if len(room.players) < 2:
        raise ValueError("2人以上参加してから開始してください")
    room.round += 1
    room.topic = random.choice(TOPICS[room.category])
    nums = random.sample(range(1, 101), len(room.players))
    for p, num in zip(room.players.values(), nums):
        p.number = num
    room.order = list(room.players.keys())
    room.stage = "reveal"
    room.last_gain = 0
    room.perfect = False


def judge(room: Room):
    vals = [room.players[pid].number for pid in room.order]
    correct_pairs = sum(1 for i in range(1, len(vals)) if vals[i-1] < vals[i])
    room.perfect = correct_pairs == max(0, len(vals)-1)
    room.last_gain = (100 + max(0, len(vals)-2)*20) if room.perfect else correct_pairs*10
    room.score += room.last_gain
    room.stage = "result"


@app.websocket("/ws/{code}")
async def websocket_endpoint(websocket: WebSocket, code: str):
    room = rooms.get(code)
    if not room:
        await websocket.close(code=4404)
        return
    role = websocket.query_params.get("role", "player")
    token = websocket.query_params.get("token", "")
    pid = websocket.query_params.get("player_id", "")
    if role == "host":
        if not check_host(room, token):
            await websocket.close(code=4403)
            return
        conn = {"ws": websocket, "role": "host"}
    else:
        if not check_player(room, pid, token):
            await websocket.close(code=4403)
            return
        conn = {"ws": websocket, "role": "player", "player_id": pid}
    await websocket.accept()
    connections.setdefault(code, []).append(conn)
    await broadcast(code)
    try:
        while True:
            msg = await websocket.receive_json()
            room.last_active = time.time()
            if role != "host":
                continue
            action = msg.get("action")
            try:
                if action == "start":
                    if room.stage not in ("lobby", "result"):
                        raise ValueError("今は開始できません")
                    if room.round >= room.max_rounds:
                        room.round = 0
                        room.score = 0
                    start_round(room)
                elif action == "discuss":
                    if room.stage != "reveal":
                        raise ValueError("今は相談フェーズへ進めません")
                    room.stage = "discuss"
                elif action == "order":
                    order = msg.get("order") or []
                    if sorted(order) != sorted(room.players.keys()):
                        raise ValueError("並び順が不正です")
                    room.order = order
                elif action == "judge":
                    if room.stage not in ("reveal", "discuss"):
                        raise ValueError("今は答え合わせできません")
                    order = msg.get("order") or room.order
                    if sorted(order) != sorted(room.players.keys()):
                        raise ValueError("並び順が不正です")
                    room.order = order
                    judge(room)
                elif action == "next":
                    if room.stage != "result":
                        raise ValueError("今は次へ進めません")
                    if room.round >= room.max_rounds:
                        room.stage = "finished"
                    else:
                        start_round(room)
                elif action == "reset":
                    room.stage = "lobby"
                    room.round = 0
                    room.score = 0
                    room.topic = None
                    room.last_gain = 0
                    room.perfect = False
                    for p in room.players.values():
                        p.number = None
                else:
                    raise ValueError("不明な操作です")
                await broadcast(code)
            except ValueError as e:
                await websocket.send_json({"type": "error", "message": str(e)})
    except WebSocketDisconnect:
        pass
    finally:
        if code in connections:
            connections[code] = [x for x in connections[code] if x["ws"] is not websocket]


@app.on_event("startup")
async def cleanup_task():
    async def loop():
        while True:
            await asyncio.sleep(1800)
            now = time.time()
            expired = [c for c, r in rooms.items() if now - r.last_active > 12 * 3600]
            for c in expired:
                rooms.pop(c, None)
                connections.pop(c, None)
    asyncio.create_task(loop())
