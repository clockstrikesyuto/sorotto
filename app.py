from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from io import BytesIO
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import asyncio
import random
import secrets
import time
import unicodedata
import qrcode

app = FastAPI(title="SOROTTO")

HTML = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0c0c0f">
<title>SOROTTO｜価値観をそろえるゲーム</title>
<style>
:root{--bg:#0c0c0f;--card:#17171c;--card2:#222229;--line:#303039;--txt:#f8f8fa;--muted:#aaaab3;--ok:#78dfa0;--bad:#ff7c7c;--warn:#ffd36c;--r:22px}
*{box-sizing:border-box}html,body{margin:0;min-height:100%;background:radial-gradient(circle at 10% 0,#282834 0,transparent 30%),radial-gradient(circle at 100% 45%,#20202a 0,transparent 28%),var(--bg);color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Hiragino Sans","Yu Gothic",sans-serif}body{min-height:100svh}.app{max-width:760px;margin:auto;padding:18px 15px 42px}.brand{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}.brandMain{display:flex;gap:10px;align-items:center}.logo{width:45px;height:45px;background:#fff;color:#111;border-radius:14px;display:grid;place-items:center;font-weight:1000}.brand h1{font-size:19px;letter-spacing:.08em;margin:0}.brand small{color:var(--muted)}.pill{border:1px solid var(--line);border-radius:999px;padding:7px 10px;color:#d8d8df;font-size:12px;background:#17171c}.screen{display:none}.screen.on{display:block;animation:in .2s ease}@keyframes in{from{opacity:.25;transform:translateY(5px)}to{opacity:1;transform:none}}.card{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border-radius:var(--r);padding:18px;margin-bottom:12px;box-shadow:0 20px 55px rgba(0,0,0,.28)}.hero{padding:27px 21px}.eyebrow,.smallcaps{font-size:11px;letter-spacing:.14em;font-weight:900;color:var(--muted)}.hero h2,.topic{font-size:clamp(29px,7vw,48px);line-height:1.08;letter-spacing:-.04em;margin:10px 0 13px}.hero p,.hint{color:#d2d2d8;line-height:1.7}.hint{font-size:13px}.btn{width:100%;border:0;border-radius:15px;padding:14px 16px;background:#fff;color:#111;font-weight:900;margin-top:9px}.btn.secondary{background:var(--card2);color:#fff;border:1px solid var(--line)}.btn.ghost{background:transparent;color:#d7d7de;border:1px dashed var(--line)}.btn.danger{background:#2b1719;color:#ffb9b9;border:1px solid #5e2a30}.btn:disabled{opacity:.4;cursor:not-allowed}input,select{width:100%;background:#101014;color:#fff;border:1px solid var(--line);border-radius:14px;padding:13px 14px;font:inherit;outline:0}label{display:block;font-size:12px;color:var(--muted);margin:0 0 7px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}@media(max-width:520px){.grid{grid-template-columns:1fr}}.code{font-size:64px;font-weight:1000;letter-spacing:.08em;text-align:center;margin:10px 0}.qr{display:block;width:min(240px,70vw);aspect-ratio:1;margin:14px auto;background:#fff;padding:10px;border-radius:18px}.copyline{display:grid;grid-template-columns:1fr 110px;gap:8px}.players{display:grid;gap:8px;margin-top:11px}.player{display:flex;align-items:center;gap:10px;background:#111116;border:1px solid var(--line);padding:11px 12px;border-radius:14px}.dot{width:9px;height:9px;border-radius:50%;background:#7be39f}.hostBadge{margin-left:auto;font-size:10px;padding:4px 7px;border:1px solid var(--line);border-radius:999px;color:var(--muted)}.axis{display:flex;justify-content:space-between;gap:8px;color:var(--muted);font-size:12px;margin-top:12px}.meter{height:9px;border-radius:999px;background:linear-gradient(90deg,#4b4b55,#fff);margin-top:7px}.number{font-size:100px;font-weight:1000;letter-spacing:-.08em;line-height:1;text-align:center;margin:17px 0}.secret{text-align:center;padding:20px 3px}.order{display:grid;gap:8px;margin-top:11px}.orderrow{display:grid;grid-template-columns:38px 1fr 40px;align-items:center;gap:8px;border:1px solid var(--line);background:#111116;border-radius:14px;padding:9px}.rank{width:32px;height:32px;border-radius:10px;background:#292930;display:grid;place-items:center;font-weight:900}.arrows{display:flex;flex-direction:column;gap:4px}.arrows button{height:22px;border:0;border-radius:6px;background:#2c2c35;color:#fff}.resultrow{display:flex;justify-content:space-between;padding:12px 2px;border-bottom:1px solid var(--line)}.resultrow:last-child{border:0}.actual{font-size:22px;font-weight:1000}.score{font-size:60px;font-weight:1000;text-align:center;letter-spacing:-.05em}.center{text-align:center}.ok{color:var(--ok)}.bad{color:var(--bad)}.warn{color:var(--warn)}.status{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);background:#fff;color:#111;border-radius:999px;padding:9px 13px;font-size:12px;font-weight:900;opacity:0;pointer-events:none;transition:.2s;z-index:99}.status.show{opacity:1}.footer{text-align:center;color:#686872;font-size:11px;line-height:1.6;margin-top:18px}.row{display:flex;gap:8px}.row>*{flex:1}
.chatBox{max-height:290px;overflow:auto;display:flex;flex-direction:column;gap:8px;padding:4px 2px 10px}.chatMsg{background:#111116;border:1px solid var(--line);border-radius:14px;padding:10px 11px}.chatMsg.system{background:transparent;border-style:dashed;color:var(--muted);text-align:center;font-size:12px}.chatHead{font-size:11px;color:var(--muted);margin-bottom:4px}.chatText{font-size:15px;line-height:1.45;overflow-wrap:anywhere}.chatComposer{display:grid;grid-template-columns:1fr 80px;gap:8px;margin-top:8px}.chatComposer .btn{margin:0}.reactions{display:flex;flex-wrap:wrap;gap:7px;margin-top:9px}.react{border:1px solid var(--line);background:#222229;color:#fff;border-radius:999px;padding:8px 12px;font-size:17px}.noDigits{font-size:11px;color:var(--warn);margin:8px 0 0}.hostJoinState{display:flex;align-items:center;justify-content:space-between;gap:10px;background:#111116;border:1px solid var(--line);border-radius:14px;padding:12px;margin-top:10px}.mini{font-size:12px;color:var(--muted)}
/* v3: current position + card reveal */
.positionList{display:grid;gap:9px;margin-top:12px}.positionCard{display:grid;grid-template-columns:44px 1fr auto;align-items:center;gap:10px;background:#111116;border:1px solid var(--line);border-radius:15px;padding:10px 12px;transition:.2s}.positionCard.mine{border-color:#f5f5f7;box-shadow:0 0 0 2px rgba(255,255,255,.09);background:#1d1d23}.positionRank{width:34px;height:34px;border-radius:10px;background:#292930;display:grid;place-items:center;font-weight:1000}.youBadge{font-size:10px;font-weight:1000;letter-spacing:.08em;border-radius:999px;background:#fff;color:#111;padding:5px 8px}.positionSummary{text-align:center;font-weight:900;margin:12px 0 2px}.positionSummary strong{font-size:28px}
.flipResults{display:grid;gap:10px;margin-top:13px;perspective:1000px}.resultCard{height:78px;position:relative;transition:transform .35s ease}.flipInner{position:absolute;inset:0;transform-style:preserve-3d;animation:flipReveal .72s cubic-bezier(.2,.75,.2,1) forwards;animation-delay:calc(var(--i)*.55s)}.flipFace{position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;border:1px solid var(--line);border-radius:16px;padding:12px 14px;display:flex;align-items:center;justify-content:space-between;background:#111116}.flipFront{background:linear-gradient(145deg,#22222a,#121217)}.flipBack{transform:rotateY(180deg);background:#18181e}.flipName{display:flex;align-items:center;gap:10px;font-weight:900}.flipRank{width:35px;height:35px;border-radius:10px;background:#292930;display:grid;place-items:center;font-weight:1000}.flipQ{font-size:28px;color:var(--muted);font-weight:1000}.resultCard.mismatch.shiftRight{animation:wrongShiftRight .35s ease forwards;animation-delay:calc(var(--i)*.55s + .78s)}.resultCard.mismatch.shiftLeft{animation:wrongShiftLeft .35s ease forwards;animation-delay:calc(var(--i)*.55s + .78s)}.resultCard.mismatch .flipBack{border-color:#6d3a3e}.resultCard.mismatch .flipBack:after{content:"ズレ";font-size:10px;font-weight:1000;color:#ffb2b2;border:1px solid #6d3a3e;border-radius:999px;padding:4px 7px;margin-left:8px}.resultCard.correct .flipBack{border-color:#315b40}@keyframes flipReveal{0%{transform:rotateY(0)}100%{transform:rotateY(180deg)}}@keyframes wrongShiftRight{to{transform:translateX(12px)}}@keyframes wrongShiftLeft{to{transform:translateX(-12px)}}
@media(max-width:520px){.resultCard.mismatch.shiftRight{--shift:8px}.resultCard.mismatch.shiftLeft{--shift:-8px}}
</style>
</head>
<body>
<div class="app">
  <div class="brand"><div class="brandMain"><div class="logo">SO</div><div><h1>SOROTTO</h1><small>価値観をそろえるゲーム</small></div></div><div class="pill" id="conn">OFFLINE</div></div>

  <section id="home" class="screen on">
    <div class="card hero"><div class="eyebrow">MULTIPLAYER PARTY GAME</div><h2>数字は秘密。<br>感覚だけ、そろえよう。</h2><p>各自のスマホに秘密の数字が届きます。数字そのものは言わず、お題に合う“たとえ”で表現。みんなで小さい順に並べられたら成功。</p></div>
    <div class="card"><div class="grid"><div><label>お題</label><select id="category"><option value="mix">ごちゃまぜ</option><option value="party">盛り上がり</option><option value="daily">日常</option><option value="love">恋愛・人間関係</option><option value="work">仕事・学校</option></select></div><div><label>ラウンド数</label><select id="rounds"><option>3</option><option selected>5</option><option>7</option><option>10</option></select></div></div><button class="btn" id="create">部屋をつくる</button></div>
    <div class="card"><label>4桁の部屋コードで参加</label><div class="copyline"><input id="joinCode" inputmode="numeric" maxlength="4" placeholder="1234"><button class="btn secondary" style="margin:0" id="goJoin">参加</button></div></div>
  </section>

  <section id="join" class="screen">
    <div class="card hero"><div class="eyebrow">JOIN ROOM</div><div class="code" id="joinCodeBig"></div><p>名前を入力して参加してください。</p></div>
    <div class="card"><label>あなたの名前</label><input id="playerName" maxlength="18" placeholder="ゆうと"><button class="btn" id="joinBtn">この部屋に参加</button><button class="btn ghost" onclick="location.href='/'">戻る</button></div>
  </section>

  <section id="host" class="screen">
    <div id="hostLobby"></div>
    <div id="hostGame" style="display:none"></div>
  </section>

  <section id="player" class="screen"><div id="playerGame"></div></section>
  <div class="footer">SOROTTO prototype — オリジナルUI・お題・得点ルールで制作したWebパーティーゲーム。</div>
</div>
<div class="status" id="toast"></div>
<script>
const $=s=>document.querySelector(s);
const path=location.pathname.split('/').filter(Boolean);
let ws=null,role=null,code=null,hostToken=null,playerId=null,playerToken=null,currentOrder=[],chatDraft='';
function screen(id){document.querySelectorAll('.screen').forEach(x=>x.classList.remove('on'));$('#'+id).classList.add('on');window.scrollTo(0,0)}
function toast(t){const e=$('#toast');e.textContent=t;e.classList.add('show');setTimeout(()=>e.classList.remove('show'),1800)}
function esc(s){return String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
function topicCard(t){return `<div class="card"><div class="smallcaps">TODAY'S SCALE</div><div class="topic">${esc(t.text)}</div><div class="axis"><span>1：${esc(t.low)}</span><span>100：${esc(t.high)}</span></div><div class="meter"></div></div>`}
async function api(url,opt={}){const r=await fetch(url,{headers:{'Content-Type':'application/json'},...opt});if(!r.ok){let j={};try{j=await r.json()}catch{};throw new Error(j.detail||'通信に失敗しました')}return r.json()}
$('#create').onclick=async()=>{try{const d=await api('/api/rooms',{method:'POST',body:JSON.stringify({category:$('#category').value,rounds:+$('#rounds').value})});location.href=d.host_url}catch(e){toast(e.message)}};
$('#goJoin').onclick=()=>{const c=$('#joinCode').value.replace(/\D/g,'');if(c.length!==4)return toast('4桁のコードを入力してね');location.href='/join/'+c};
function parseHostToken(){const m=location.hash.match(/token=([^&]+)/);return m?decodeURIComponent(m[1]):localStorage.getItem('sorotto_host_'+code)}
async function initJoin(){screen('join');$('#joinCodeBig').textContent=code;const saved=JSON.parse(localStorage.getItem('sorotto_player_'+code)||'null');if(saved?.player_id&&saved?.player_token){playerId=saved.player_id;playerToken=saved.player_token;connectPlayer();return}$('#joinBtn').onclick=async()=>{try{const d=await api(`/api/rooms/${code}/join`,{method:'POST',body:JSON.stringify({name:$('#playerName').value})});playerId=d.player_id;playerToken=d.player_token;localStorage.setItem('sorotto_player_'+code,JSON.stringify(d));connectPlayer()}catch(e){toast(e.message)}}}
function initHost(){role='host';hostToken=parseHostToken();if(!hostToken){screen('home');return toast('ホスト情報がありません')}localStorage.setItem('sorotto_host_'+code,hostToken);history.replaceState(null,'',`/host/${code}`);screen('host');connect('host')}
function connectPlayer(){role='player';screen('player');connect('player')}
function connect(r){if(ws)try{ws.close()}catch{};const proto=location.protocol==='https:'?'wss':'ws';let url=`${proto}://${location.host}/ws/${code}?role=${r}&token=${encodeURIComponent(r==='host'?hostToken:playerToken)}`;if(r==='player')url+=`&player_id=${encodeURIComponent(playerId)}`;ws=new WebSocket(url);ws.onopen=()=>{$('#conn').textContent='LIVE';$('#conn').style.color='#78dfa0'};ws.onclose=()=>{$('#conn').textContent='RECONNECT';$('#conn').style.color='';setTimeout(()=>connect(r),1800)};ws.onerror=()=>toast('接続を確認しています…');ws.onmessage=e=>{const d=JSON.parse(e.data);if(d.type==='error')return toast(d.message);if(r==='host')renderHost(d);else renderPlayer(d)}}
function send(action,extra={}){if(ws?.readyState===1)ws.send(JSON.stringify({action,...extra}))}
function renderPlayers(list){return list.length?list.map(p=>`<div class="player"><span class="dot"></span><strong>${esc(p.name)}</strong>${p.is_host?'<span class="hostBadge">HOST</span>':''}</div>`).join(''):`<p class="hint">参加者を待っています…</p>`}
function chatHtml(s){const msgs=(s.chat||[]).map(m=>m.kind==='system'?`<div class="chatMsg system">${esc(m.text)}</div>`:`<div class="chatMsg"><div class="chatHead">${esc(m.sender)}</div><div class="chatText">${esc(m.text)}</div></div>`).join('');return `<div class="card"><div class="smallcaps">ROOM CHAT</div><div class="chatBox" id="chatBox">${msgs||'<div class="chatMsg system">まだメッセージはありません</div>'}<div id="chatEnd" aria-hidden="true"></div></div><div class="chatComposer"><input id="chatInput" maxlength="120" inputmode="text" enterkeyhint="send" autocomplete="off" autocapitalize="sentences" placeholder="たとえを送る…" value="${esc(chatDraft)}"><button class="btn secondary" id="chatSend">送信</button></div><div class="reactions"><button class="react" data-react="👍">👍</button><button class="react" data-react="🤔">🤔</button><button class="react" data-react="😂">😂</button><button class="react" data-react="👀">👀</button><button class="react" data-react="⬆️">⬆️</button><button class="react" data-react="⬇️">⬇️</button></div><p class="noDigits">チャットでは数字を含むメッセージは送信できません。</p></div>`}
function scrollChatToLatest(){const box=$('#chatBox'),end=$('#chatEnd');if(!box)return;const go=()=>{box.scrollTop=box.scrollHeight;if(end)end.scrollIntoView({block:'end',inline:'nearest'})};requestAnimationFrame(()=>requestAnimationFrame(go));setTimeout(go,60);setTimeout(go,180)}
function bindChat(){const inp=$('#chatInput'),btn=$('#chatSend');if(!inp||!btn)return;let composing=false;inp.addEventListener('compositionstart',()=>{composing=true});inp.addEventListener('compositionend',()=>{composing=false;chatDraft=inp.value});inp.oninput=()=>chatDraft=inp.value;const submit=()=>{const text=inp.value.trim();if(!text){toast('メッセージを入力してね');return}if(/[0-9０-９]/.test(text)){toast('数字はチャットで使えません');return}send('chat',{text});chatDraft='';inp.value='';scrollChatToLatest()};btn.type='button';btn.onclick=e=>{e.preventDefault();submit()};inp.onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing&&!composing){e.preventDefault();submit()}};document.querySelectorAll('[data-react]').forEach(b=>{b.type='button';b.onclick=e=>{e.preventDefault();send('react',{emoji:b.dataset.react});scrollChatToLatest()}});scrollChatToLatest()}
function currentPositionHtml(s,myId,interactive=false){const players=s.players||[];const map=Object.fromEntries(players.map(p=>[p.id,p]));const order=(s.order?.length?s.order:players.map(p=>p.id));const mine=order.indexOf(myId);const summary=myId&&mine>=0?`<div class="positionSummary">あなたは今 <strong>${mine+1}</strong> 番目</div>`:'';const rows=order.map((id,i)=>{const p=map[id]||{};const isMine=id===myId;return `<div class="positionCard ${isMine?'mine':''}"><div class="positionRank">${i+1}</div><strong>${esc(p.name||'?')}</strong>${isMine?'<span class="youBadge">YOU</span>':''}</div>`}).join('');return `<div class="card"><div class="smallcaps">CURRENT ORDER</div>${summary}<div class="positionList">${rows}</div>${interactive?'':'<p class="hint">並び替えはホストが操作します。変更はリアルタイムで反映されます。</p>'}</div>`}
function resultCardsHtml(s,myId){const rows=(s.results||[]).map((x,i)=>{const correct=x.position_correct!==false;const dir=correct?'':(x.correct_position>(i+1)?'shiftRight':'shiftLeft');return `<div class="resultCard ${correct?'correct':'mismatch'} ${dir}" style="--i:${i}"><div class="flipInner"><div class="flipFace flipFront"><div class="flipName"><div class="flipRank">${i+1}</div><span>${esc(x.name)}${x.id===myId?' <span class="youBadge">YOU</span>':''}</span></div><div class="flipQ">?</div></div><div class="flipFace flipBack"><div class="flipName"><div class="flipRank">${i+1}</div><span>${esc(x.name)}${x.id===myId?' <span class="youBadge">YOU</span>':''}</span></div><span class="actual">${x.number}</span></div></div></div>`}).join('');return `<div class="flipResults">${rows}</div>${s.perfect?'':`<p class="hint center">順番が違ったカードだけ、少し横にズレて表示されます。</p>`}`}
function renderHost(s){
 const lobby=$('#hostLobby'),g=$('#hostGame');
 if(s.stage==='lobby'){
   g.style.display='none';lobby.style.display='';
   const hostPlay=s.host_player_id?`<div class="hostJoinState"><div><strong>${esc(s.host_player_name)}</strong><div class="mini">ホスト兼プレイヤーとして参加中</div></div><button class="btn danger" style="width:auto;margin:0" id="hostLeave">参加をやめる</button></div>`:`<label style="margin-top:12px">ホストもプレイヤーとして参加</label><div class="copyline"><input id="hostName" maxlength="18" placeholder="あなたの名前"><button class="btn secondary" style="margin:0" id="hostJoin">参加する</button></div>`;
   lobby.innerHTML=`<div class="card center"><div class="smallcaps">ROOM CODE</div><div class="code">${esc(s.code)}</div><img class="qr" src="/room/${esc(s.code)}/qr?t=${Date.now()}"><div class="copyline"><input id="joinUrl" readonly value="${location.origin}/join/${esc(s.code)}"><button class="btn secondary" style="margin:0" id="copyUrl">コピー</button></div><p class="hint">QRコードを読み取るか、URLを送れば参加できます。</p></div><div class="card"><div class="smallcaps">HOST PLAYER</div>${hostPlay}</div><div class="card"><div class="smallcaps">PLAYERS</div><div class="players">${renderPlayers(s.players)}</div><button class="btn" id="start" ${s.players.length<2?'disabled':''}>${s.players.length<2?'あと'+(2-s.players.length)+'人で開始':s.players.length+'人でゲーム開始'}</button></div>${chatHtml(s)}`;
   $('#copyUrl').onclick=async()=>{try{await navigator.clipboard.writeText($('#joinUrl').value);toast('参加URLをコピーしました')}catch{toast('コピーできませんでした')}};
   if($('#hostJoin'))$('#hostJoin').onclick=()=>{const name=$('#hostName').value.trim();if(!name)return toast('名前を入力してね');send('host_join',{name})};
   if($('#hostLeave'))$('#hostLeave').onclick=()=>send('host_leave');
   $('#start').onclick=()=>send('start');bindChat();return;
 }
 lobby.style.display='none';g.style.display='';
 const mine=s.host_player_id&&s.number!=null?`<div class="card secret"><div class="smallcaps">YOUR NUMBER</div><div class="number">${s.number}</div><p class="hint">ホストのあなたもプレイヤーです。この数字は秘密。</p></div>`:'';
 if(s.stage==='reveal') {g.innerHTML=`<div class="card"><div class="smallcaps">ROUND ${s.round} / ${s.max_rounds}</div></div>${topicCard(s.topic)}${mine}<div class="card center"><div class="topic">各自の数字を確認中 👀</div><p class="hint">全員が自分のスマホで秘密の数字を確認したら、相談開始。</p><button class="btn" id="discuss">相談をはじめる</button></div>${chatHtml(s)}`;$('#discuss').onclick=()=>send('discuss');bindChat();return}
 if(s.stage==='discuss') {currentOrder=(s.order?.length?s.order:s.players.map(p=>p.id)).slice();g.innerHTML=`<div class="card"><div class="smallcaps">ROUND ${s.round} / ${s.max_rounds}</div></div>${topicCard(s.topic)}${mine}<div class="card"><div class="smallcaps">小さいと思う順</div>${s.host_player_id&&currentOrder.indexOf(s.host_player_id)>=0?`<div class="positionSummary">あなたは今 <strong>${currentOrder.indexOf(s.host_player_id)+1}</strong> 番目</div>`:''}<p class="hint">チャットや会話の“たとえ”を見て、ホストが順番を並べ替えてください。</p><div class="order" id="order"></div><button class="btn" id="judge">この順番で答え合わせ</button></div>${chatHtml(s)}`;renderOrder(s.players,s.host_player_id);$('#judge').onclick=()=>send('judge',{order:currentOrder});bindChat();return}
 if(s.stage==='result'||s.stage==='finished'){g.innerHTML=`<div class="card"><div class="smallcaps">RESULT</div><div class="topic ${s.perfect?'ok':'bad'}">${s.perfect?'PERFECT!':'惜しい！'} +${s.last_gain}pt</div>${resultCardsHtml(s,s.host_player_id)}</div><div class="card center"><div class="smallcaps">TOTAL SCORE</div><div class="score">${s.score}</div>${s.stage==='finished'?'<p class="hint">全ラウンド終了！</p><button class="btn" id="reset">ロビーに戻る</button>':`<button class="btn" id="next">${s.round>=s.max_rounds?'最終結果へ':'次のラウンド'}</button>`}</div>${chatHtml(s)}`;if($('#next'))$('#next').onclick=()=>send('next');if($('#reset'))$('#reset').onclick=()=>send('reset');bindChat();return}
}
function renderOrder(players,myId=null){const map=Object.fromEntries(players.map(p=>[p.id,p]));const wrap=$('#order');wrap.innerHTML=currentOrder.map((id,i)=>`<div class="orderrow ${id===myId?'positionCard mine':''}"><div class="rank">${i+1}</div><strong>${esc(map[id]?.name||'?')}${id===myId?' <span class="youBadge">YOU</span>':''}</strong><div class="arrows"><button data-up="${i}">▲</button><button data-down="${i}">▼</button></div></div>`).join('');wrap.querySelectorAll('[data-up]').forEach(b=>b.onclick=()=>move(+b.dataset.up,-1,players,myId));wrap.querySelectorAll('[data-down]').forEach(b=>b.onclick=()=>move(+b.dataset.down,1,players,myId))}
function move(i,d,players,myId=null){const n=i+d;if(n<0||n>=currentOrder.length)return;[currentOrder[i],currentOrder[n]]=[currentOrder[n],currentOrder[i]];renderOrder(players,myId);send('order',{order:currentOrder})}
function renderPlayer(s){const g=$('#playerGame');if(s.stage==='lobby'){g.innerHTML=`<div class="card hero center"><div class="eyebrow">ROOM ${s.code}</div><div class="topic">参加完了！</div><p>${esc(s.name)} さん</p><p class="hint">ホストがゲームを始めるまで、この画面で待ってください。</p></div><div class="card"><div class="smallcaps">PLAYERS</div><div class="players">${renderPlayers(s.players)}</div></div>${chatHtml(s)}`;bindChat();return}
 if(s.stage==='reveal'){g.innerHTML=`<div class="card"><div class="smallcaps">ROUND ${s.round} / ${s.max_rounds}</div></div>${topicCard(s.topic)}<div class="card secret"><div class="smallcaps">YOUR NUMBER</div><div class="number">${s.number}</div><p class="hint">この数字はあなただけの秘密。数字そのものは言わず、お題に合う“たとえ”で表現してください。</p><div class="pill">みんなが確認中</div></div>${chatHtml(s)}`;bindChat();return}
 if(s.stage==='discuss'){g.innerHTML=`<div class="card"><div class="smallcaps">ROUND ${s.round} / ${s.max_rounds}</div></div>${topicCard(s.topic)}<div class="card secret"><div class="smallcaps">YOUR NUMBER</div><div class="number">${s.number}</div><p class="hint">この数字はあなただけの秘密。数字そのものは言わず、お題に合う“たとえ”で表現してください。</p><div class="pill">相談中</div></div>${currentPositionHtml(s,s.player_id)}${chatHtml(s)}`;bindChat();return}
 if(s.stage==='result'||s.stage==='finished'){g.innerHTML=`<div class="card"><div class="smallcaps">RESULT</div><div class="topic ${s.perfect?'ok':'bad'}">${s.perfect?'そろった！':'惜しい！'}</div>${resultCardsHtml(s,s.player_id)}</div><div class="card center"><div class="smallcaps">TEAM SCORE</div><div class="score">${s.score}</div><p class="hint">${s.stage==='finished'?'ゲーム終了！おつかれさま！':'ホストが次のラウンドへ進めます。'}</p></div>${chatHtml(s)}`;bindChat();return}
}
if(path[0]==='join'&&/^\d{4}$/.test(path[1]||'')){code=path[1];initJoin()}else if(path[0]==='host'&&/^\d{4}$/.test(path[1]||'')){code=path[1];initHost()}else screen('home');
</script>
</body></html>'''

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

REACTIONS = {"👍", "🤔", "😂", "👀", "⬆️", "⬇️"}

@dataclass
class Player:
    id: str
    token: str
    name: str
    number: Optional[int] = None
    is_host: bool = False

@dataclass
class Room:
    code: str
    host_token: str
    category: str = "mix"
    max_rounds: int = 5
    players: Dict[str, Player] = field(default_factory=dict)
    host_player_id: Optional[str] = None
    stage: str = "lobby"
    round: int = 0
    topic: Optional[tuple] = None
    order: List[str] = field(default_factory=list)
    score: int = 0
    last_gain: int = 0
    perfect: bool = False
    chat: List[dict] = field(default_factory=list)
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
    return {"code": room.code, "stage": room.stage, "round": room.round, "max_rounds": room.max_rounds, "player_count": len(room.players)}


def topic_json(room: Room):
    if not room.topic:
        return None
    return {"text": room.topic[0], "low": room.topic[1], "high": room.topic[2]}


def player_list(room: Room):
    return [{"id": p.id, "name": p.name, "is_host": p.is_host} for p in room.players.values()]


def result_list(room: Room):
    if room.stage not in ("result", "finished"):
        return None
    guessed = [pid for pid in room.order if pid in room.players]
    correct = sorted(guessed, key=lambda pid: room.players[pid].number)
    correct_pos = {pid: i + 1 for i, pid in enumerate(correct)}
    return [
        {
            "id": pid,
            "name": room.players[pid].name,
            "number": room.players[pid].number,
            "guessed_position": i + 1,
            "correct_position": correct_pos[pid],
            "position_correct": correct_pos[pid] == i + 1,
        }
        for i, pid in enumerate(guessed)
    ]


def host_state(room: Room):
    hp = room.players.get(room.host_player_id) if room.host_player_id else None
    reveal_number = hp.number if hp and room.stage in ("reveal", "discuss") else None
    return {
        "type": "state", "role": "host", "code": room.code, "stage": room.stage,
        "round": room.round, "max_rounds": room.max_rounds, "score": room.score,
        "last_gain": room.last_gain, "perfect": room.perfect, "topic": topic_json(room),
        "players": player_list(room), "order": room.order, "results": result_list(room),
        "host_player_id": room.host_player_id, "host_player_name": hp.name if hp else None,
        "number": reveal_number, "chat": room.chat,
    }


def player_state(room: Room, pid: str):
    p = room.players.get(pid)
    if not p:
        return {"type": "error", "message": "プレイヤー情報が見つかりません"}
    reveal_number = p.number if room.stage in ("reveal", "discuss") else None
    return {
        "type": "state", "role": "player", "player_id": p.id, "name": p.name,
        "code": room.code, "stage": room.stage, "round": room.round,
        "max_rounds": room.max_rounds, "score": room.score, "last_gain": room.last_gain,
        "perfect": room.perfect, "topic": topic_json(room), "number": reveal_number,
        "players": player_list(room), "order": room.order, "results": result_list(room), "chat": room.chat,
    }


def add_chat(room: Room, sender: str, text: str, kind: str = "chat"):
    room.chat.append({"id": secrets.token_hex(4), "sender": sender, "text": text, "kind": kind, "at": int(time.time())})
    if len(room.chat) > 100:
        room.chat = room.chat[-100:]


def contains_digit(text: str) -> bool:
    normalized = unicodedata.normalize("NFKC", text)
    return any(ch.isdigit() for ch in normalized)


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
    add_chat(room, "", "部屋ができました。参加者を待っています。", "system")
    rooms[code] = room
    base = public_origin(request)
    return {"code": code, "host_token": token, "host_url": f"{base}/host/{code}#token={token}", "join_url": f"{base}/join/{code}"}


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
            if p.token and secrets.compare_digest(p.token, data.player_token):
                p.name = name
                await broadcast(code)
                return {"player_id": p.id, "player_token": p.token, "name": p.name}
    if len(room.players) >= 12:
        raise HTTPException(409, "この部屋は満員です")
    pid = secrets.token_hex(5)
    token = secrets.token_urlsafe(18)
    room.players[pid] = Player(id=pid, token=token, name=name)
    room.order.append(pid)
    add_chat(room, "", f"{name} さんが参加しました。", "system")
    await broadcast(code)
    return {"player_id": pid, "player_token": token, "name": name}


@app.get("/room/{code}/qr")
async def room_qr(code: str, request: Request):
    if code not in rooms:
        raise HTTPException(404, "部屋が見つかりません")
    url = f"{public_origin(request)}/join/{code}"
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png", headers={"Cache-Control": "no-store"})


def check_host(room: Room, token: str):
    return bool(token and secrets.compare_digest(token, room.host_token))


def check_player(room: Room, pid: str, token: str):
    p = room.players.get(pid)
    return bool(p and token and p.token and secrets.compare_digest(token, p.token))


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
    add_chat(room, "", "新しいラウンドが始まりました。数字はチャットに書かないでください。", "system")


def judge(room: Room):
    vals = [room.players[pid].number for pid in room.order]
    correct_pairs = sum(1 for i in range(1, len(vals)) if vals[i - 1] < vals[i])
    room.perfect = correct_pairs == max(0, len(vals) - 1)
    room.last_gain = (100 + max(0, len(vals) - 2) * 20) if room.perfect else correct_pairs * 10
    room.score += room.last_gain
    room.stage = "result"
    add_chat(room, "", "答え合わせになりました。", "system")


def sender_name(room: Room, role: str, pid: str) -> str:
    if role == "host":
        hp = room.players.get(room.host_player_id) if room.host_player_id else None
        return hp.name if hp else "ホスト"
    p = room.players.get(pid)
    return p.name if p else "参加者"


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
            action = msg.get("action")
            try:
                if action == "chat":
                    text = str(msg.get("text") or "").strip()[:120]
                    if not text:
                        raise ValueError("メッセージを入力してください")
                    if contains_digit(text):
                        raise ValueError("数字を含むメッセージは送れません")
                    add_chat(room, sender_name(room, role, pid), text)
                    await broadcast(code)
                    continue
                if action == "react":
                    emoji = str(msg.get("emoji") or "")
                    if emoji not in REACTIONS:
                        raise ValueError("そのリアクションは使えません")
                    add_chat(room, sender_name(room, role, pid), emoji)
                    await broadcast(code)
                    continue
                if role != "host":
                    raise ValueError("ホストだけが操作できます")
                if action == "host_join":
                    if room.stage != "lobby":
                        raise ValueError("ロビーでのみ参加できます")
                    name = str(msg.get("name") or "").strip()[:18]
                    if not name:
                        raise ValueError("名前を入力してください")
                    if room.host_player_id and room.host_player_id in room.players:
                        room.players[room.host_player_id].name = name
                    else:
                        if len(room.players) >= 12:
                            raise ValueError("この部屋は満員です")
                        hpid = secrets.token_hex(5)
                        room.players[hpid] = Player(id=hpid, token="", name=name, is_host=True)
                        room.host_player_id = hpid
                        room.order.append(hpid)
                        add_chat(room, "", f"{name} さんがホスト兼プレイヤーで参加しました。", "system")
                elif action == "host_leave":
                    if room.stage != "lobby":
                        raise ValueError("ロビーでのみ参加解除できます")
                    hpid = room.host_player_id
                    if hpid and hpid in room.players:
                        name = room.players[hpid].name
                        room.players.pop(hpid, None)
                        room.order = [x for x in room.order if x != hpid]
                        room.host_player_id = None
                        add_chat(room, "", f"{name} さんは司会専任になりました。", "system")
                elif action == "start":
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
                    add_chat(room, "", "相談タイムです。たとえをチャットでも送れます。", "system")
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
                    room.chat = []
                    add_chat(room, "", "ロビーに戻りました。", "system")
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
