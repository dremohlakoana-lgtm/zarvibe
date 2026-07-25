#!/usr/bin/env python3
"""Build the MZN Social frontend HTML file."""
import os

OUT = "/data/.openclaw/workspace/mznsocial/backend/frontend/index.html"

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0e1a;--bg2:#111827;--bg3:#1a2235;--border:#1e2d45;
  --purple:#6c63ff;--purple2:#8b85ff;--accent:#00d4aa;
  --red:#ff4757;--gold:#ffd700;--text:#e8eaf6;--muted:#8892a4;
  --card:#141d2e;--radius:14px;--sidebar:240px;
}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;overflow-x:hidden}
a{color:inherit;text-decoration:none}
button{cursor:pointer;border:none;outline:none;background:none;color:var(--text);font-family:inherit}
input,textarea{font-family:inherit;background:var(--bg3);color:var(--text);border:1px solid var(--border);border-radius:10px;padding:10px 14px;font-size:.9rem;outline:none;transition:border .2s}
input:focus,textarea:focus{border-color:var(--purple)}
textarea{resize:vertical}
img{max-width:100%;border-radius:10px;display:block}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:var(--bg)}::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
#app{display:flex;min-height:100vh}
#sidebar{width:var(--sidebar);min-width:var(--sidebar);background:var(--bg2);border-right:1px solid var(--border);display:flex;flex-direction:column;padding:20px 0;position:fixed;top:0;left:0;height:100vh;z-index:100;transition:transform .3s}
.logo{display:flex;align-items:center;gap:10px;padding:0 20px 24px;font-size:1.3rem;font-weight:800}
.logo-text{background:linear-gradient(135deg,var(--purple),var(--accent));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
#nav-items{flex:1}
.nav-item{display:flex;align-items:center;gap:14px;padding:14px 20px;font-size:.95rem;font-weight:500;cursor:pointer;border-radius:var(--radius);margin:2px 10px;transition:background .2s,color .2s}
.nav-item:hover{background:var(--bg3);color:var(--purple2)}
.nav-item.active{background:linear-gradient(135deg,rgba(108,99,255,.25),rgba(0,212,170,.1));color:var(--purple)}
.nav-icon{font-size:1.2rem;width:24px;text-align:center}
#ticker{margin:10px;padding:12px 16px;background:linear-gradient(135deg,var(--bg3),#0d1a2e);border:1px solid var(--border);border-radius:var(--radius);font-size:.85rem;color:var(--muted)}
#ticker .amount{font-size:1.1rem;font-weight:700;color:var(--accent)}
#main{margin-left:var(--sidebar);flex:1;max-width:calc(100vw - var(--sidebar));min-height:100vh}
.page{display:none;min-height:100vh;padding-bottom:60px}
.page.active{display:block}
.topbar{position:sticky;top:0;z-index:50;background:rgba(10,14,26,.9);backdrop-filter:blur(16px);border-bottom:1px solid var(--border);padding:14px 20px;display:flex;align-items:center;gap:12px}
.topbar h2{font-size:1.1rem;font-weight:700}
#bottom-tabs{display:none;position:fixed;bottom:0;left:0;right:0;background:var(--bg2);border-top:1px solid var(--border);z-index:200;padding:6px 0;flex-direction:row}
.btab{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;font-size:.6rem;color:var(--muted);cursor:pointer;padding:4px}
.btab .bicon{font-size:1.3rem}
.btab.active{color:var(--purple)}
#auth-overlay{position:fixed;inset:0;background:var(--bg);z-index:1000;display:flex;align-items:center;justify-content:center}
.auth-box{background:var(--bg2);border:1px solid var(--border);border-radius:20px;padding:40px;width:100%;max-width:420px}
.auth-tab-btns{display:flex;gap:8px;margin-bottom:20px}
.auth-tab-btn{padding:8px 20px;border-radius:20px;font-weight:600;font-size:.9rem;border:1px solid var(--border);color:var(--muted);transition:.2s}
.auth-tab-btn.active{background:var(--purple);color:#fff;border-color:var(--purple)}
.field{margin-bottom:14px}
.field label{display:block;margin-bottom:6px;font-size:.85rem;color:var(--muted)}
.field input,.field textarea{width:100%}
.btn-primary{width:100%;padding:13px;border-radius:12px;font-size:1rem;font-weight:700;background:linear-gradient(135deg,var(--purple),var(--purple2));color:#fff;margin-top:8px;transition:opacity .2s}
.btn-primary:hover{opacity:.9}
.feed-container{max-width:600px;margin:0 auto;padding:0 10px}
.composer{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin:16px 0}
.composer-row{display:flex;gap:12px;align-items:flex-start}
.av{width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,var(--purple),var(--accent));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1rem;flex-shrink:0;overflow:hidden}
.av img{width:100%;height:100%;object-fit:cover;border-radius:50%}
.composer textarea{flex:1;min-height:80px;background:none;border:none;font-size:1rem;line-height:1.5;color:var(--text);width:100%}
.composer textarea::placeholder{color:var(--muted)}
.composer-footer{display:flex;align-items:center;gap:10px;margin-top:10px;padding-top:10px;border-top:1px solid var(--border);flex-wrap:wrap}
.composer-footer input{flex:1;min-width:120px;height:36px;font-size:.85rem}
select.msel{background:var(--bg3);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:6px 10px;font-size:.85rem}
.post-btn{padding:8px 20px;border-radius:20px;font-weight:700;font-size:.9rem;background:linear-gradient(135deg,var(--purple),var(--purple2));color:#fff}
.post-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin:10px 0;transition:border-color .2s}
.post-card:hover{border-color:var(--purple)}
.post-header{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}
.post-meta{flex:1}
.post-name{font-weight:700;font-size:.95rem}
.post-username{color:var(--muted);font-size:.82rem}
.post-time{color:var(--muted);font-size:.78rem;margin-top:2px}
.viral-badge{background:linear-gradient(135deg,#ff6b35,#ff4757);color:#fff;font-size:.7rem;font-weight:800;padding:3px 10px;border-radius:20px;animation:pulse 1.5s infinite}
.ai-badge{background:linear-gradient(135deg,var(--bg3),#1a2535);border:1px solid var(--purple);color:var(--purple2);font-size:.7rem;font-weight:700;padding:3px 8px;border-radius:20px}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.7}}
.post-content{font-size:.95rem;line-height:1.6;margin-bottom:12px;word-break:break-word}
.post-media{margin-bottom:12px;border-radius:12px;overflow:hidden;max-height:380px}
.post-media img,.post-media video{width:100%;border-radius:12px;display:block;max-height:380px;object-fit:cover}
.post-actions{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.action-btn{display:flex;align-items:center;gap:5px;color:var(--muted);font-size:.85rem;padding:6px 10px;border-radius:20px;transition:all .2s}
.action-btn:hover{background:rgba(108,99,255,.12);color:var(--purple)}
.action-btn.liked{color:var(--red)}
@keyframes likeAnim{0%{transform:scale(1)}40%{transform:scale(1.5)}70%{transform:scale(.9)}100%{transform:scale(1)}}
.like-pop{animation:likeAnim .4s ease}
#page-videos{background:#000;padding:0;padding-bottom:0!important}
.video-feed{height:100vh;overflow-y:scroll;scroll-snap-type:y mandatory;-webkit-overflow-scrolling:touch}
.video-item{height:100vh;scroll-snap-align:start;position:relative;background:#000;display:flex;align-items:center;justify-content:center;overflow:hidden}
.video-item video{width:100%;height:100%;object-fit:cover;position:absolute;inset:0}
.video-placeholder{width:100%;height:100%;background:linear-gradient(135deg,#0a0e1a,#1a2235);display:flex;align-items:center;justify-content:center;font-size:4rem;position:absolute;inset:0}
.video-overlay{position:absolute;bottom:0;left:0;right:60px;padding:20px;background:linear-gradient(transparent,rgba(0,0,0,.85));z-index:2}
.video-overlay .vname{font-weight:700;font-size:1rem}
.video-overlay .vcontent{font-size:.9rem;color:rgba(255,255,255,.8);margin-top:4px}
.video-side-actions{position:absolute;right:0;bottom:80px;display:flex;flex-direction:column;align-items:center;gap:20px;padding:0 10px;z-index:2}
.vid-action{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:.7rem;color:#fff}
.vid-action button{font-size:1.8rem;background:rgba(0,0,0,.4);border-radius:50%;width:46px;height:46px;display:flex;align-items:center;justify-content:center}
.w2e-coin{position:absolute;top:20px;right:20px;z-index:10;background:rgba(255,215,0,.15);border:2px solid var(--gold);border-radius:50%;width:44px;height:44px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;opacity:0;transition:opacity .4s}
.w2e-coin.show{opacity:1;animation:coinSpin 1s ease}
@keyframes coinSpin{0%{transform:rotateY(0) scale(.5)}50%{transform:rotateY(180deg) scale(1.2)}100%{transform:rotateY(360deg) scale(1)}}
.chat-layout{display:flex;height:calc(100vh - 58px)}
.chat-list{width:280px;min-width:280px;border-right:1px solid var(--border);overflow-y:auto}
.chat-item{padding:14px 16px;border-bottom:1px solid var(--border);cursor:pointer;transition:background .2s;display:flex;align-items:center;gap:12px}
.chat-item:hover,.chat-item.active{background:var(--bg3)}
.chat-meta{flex:1;min-width:0}
.chat-name{font-weight:600;font-size:.9rem}
.chat-preview{font-size:.8rem;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}
.chat-window{flex:1;display:flex;flex-direction:column;min-width:0}
.chat-header{padding:14px 16px;border-bottom:1px solid var(--border);font-weight:700}
.messages-area{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:8px}
.msg{max-width:70%;padding:10px 14px;border-radius:18px;font-size:.9rem;line-height:1.4}
.msg.sent{align-self:flex-end;background:var(--purple);color:#fff;border-bottom-right-radius:4px}
.msg.recv{align-self:flex-start;background:var(--bg3);color:var(--text);border-bottom-left-radius:4px}
.chat-input-bar{padding:12px 16px;border-top:1px solid var(--border);display:flex;gap:10px}
.chat-input-bar input{flex:1}
.send-btn{padding:8px 18px;border-radius:20px;background:var(--purple);color:#fff;font-weight:700}
.chat-empty{flex:1;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:1rem;flex-direction:column;gap:10px}
.memories-stories{display:flex;gap:12px;padding:16px;overflow-x:auto;border-bottom:1px solid var(--border)}
.story-circle{display:flex;flex-direction:column;align-items:center;gap:6px;cursor:pointer;flex-shrink:0}
.story-ring{width:64px;height:64px;border-radius:50%;padding:3px;background:linear-gradient(135deg,var(--purple),var(--accent));display:flex;align-items:center;justify-content:center;transition:transform .2s}
.story-ring:hover{transform:scale(1.08)}
.story-ring.boosted{background:linear-gradient(135deg,var(--gold),#ff6b35);box-shadow:0 0 16px rgba(255,215,0,.5);animation:glow 2s infinite}
@keyframes glow{0%,100%{box-shadow:0 0 12px rgba(255,215,0,.4)}50%{box-shadow:0 0 24px rgba(255,215,0,.8)}}
.story-av{width:58px;height:58px;border-radius:50%;background:var(--bg2);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.2rem;overflow:hidden}
.story-name{font-size:.72rem;color:var(--muted);text-align:center;max-width:64px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.story-viewer{position:fixed;inset:0;background:rgba(0,0,0,.95);z-index:500;display:none;align-items:center;justify-content:center}
.story-viewer.open{display:flex}
.story-content-box{max-width:400px;width:90%;background:var(--bg2);border-radius:20px;padding:24px;position:relative}
.story-close{position:absolute;top:16px;right:16px;font-size:1.4rem;cursor:pointer;color:var(--muted)}
.memories-feed{padding:16px;max-width:600px;margin:0 auto}
.memory-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin:10px 0}
.earnings-container{max-width:600px;margin:0 auto;padding:16px}
.earnings-hero{background:linear-gradient(135deg,#0d1a2e,#1a2640);border:1px solid var(--accent);border-radius:20px;padding:30px;text-align:center;margin-bottom:20px}
.earnings-hero .big-amount{font-size:3.5rem;font-weight:900;color:var(--accent);line-height:1}
.withdraw-btn{display:inline-block;margin-top:20px;padding:12px 32px;border-radius:25px;font-weight:800;font-size:1rem;background:linear-gradient(135deg,var(--accent),#00a884);color:#0a0e1a}
.stats-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px}
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;text-align:center}
.stat-card .sv{font-size:1.6rem;font-weight:800;color:var(--purple)}
.stat-card .sl{font-size:.8rem;color:var(--muted);margin-top:4px}
.log-item{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:var(--card);border:1px solid var(--border);border-radius:10px;margin-bottom:6px}
.log-item .reason{font-size:.85rem;color:var(--muted)}
.log-item .amount-pos{color:var(--accent);font-weight:700}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:600;display:none;align-items:center;justify-content:center}
.modal-overlay.open{display:flex}
.modal-box{background:var(--bg2);border:1px solid var(--border);border-radius:20px;padding:32px;width:100%;max-width:380px}
.modal-box h3{font-size:1.2rem;font-weight:700;margin-bottom:20px}
.profile-container{max-width:600px;margin:0 auto}
.cover-photo{height:180px;background:linear-gradient(135deg,var(--purple),var(--accent));overflow:hidden;position:relative}
.cover-photo img{width:100%;height:100%;object-fit:cover}
.profile-av-wrap{padding:0 20px;margin-top:-36px;display:flex;justify-content:space-between;align-items:flex-end}
.profile-av{width:80px;height:80px;border-radius:50%;border:4px solid var(--bg);background:linear-gradient(135deg,var(--purple),var(--accent));display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:700;overflow:hidden}
.profile-av img{width:100%;height:100%;object-fit:cover}
.edit-profile-btn{padding:8px 20px;border-radius:20px;border:1px solid var(--border);font-weight:600;font-size:.85rem;background:none;color:var(--text);transition:.2s;cursor:pointer}
.edit-profile-btn:hover{background:var(--bg3)}
.profile-info{padding:16px 20px}
.profile-name{font-size:1.2rem;font-weight:800}
.profile-handle{color:var(--muted);font-size:.88rem;margin-top:2px}
.profile-bio{margin-top:10px;font-size:.9rem;line-height:1.5}
.profile-stats{display:flex;gap:24px;margin-top:14px;flex-wrap:wrap}
.pstat{font-size:.9rem}
.pstat strong{font-weight:800}
.pstat span{color:var(--muted);margin-left:4px}
.profile-posts-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2px;margin-top:16px}
.grid-post{aspect-ratio:1;background:var(--bg3);overflow:hidden;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:1.4rem;position:relative}
.grid-post img{width:100%;height:100%;object-fit:cover}
.grid-overlay{position:absolute;inset:0;background:rgba(0,0,0,.5);display:none;align-items:center;justify-content:center;font-size:.8rem;color:#fff;gap:8px}
.grid-post:hover .grid-overlay{display:flex}
#toast-container{position:fixed;bottom:80px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px}
.toast{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:12px 16px;font-size:.88rem;min-width:200px;animation:slideIn .3s ease}
.toast.earn{border-color:var(--accent);color:var(--accent)}
.toast.info{border-color:var(--purple);color:var(--purple2)}
.toast.error{border-color:var(--red);color:var(--red)}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
#confetti-canvas{position:fixed;inset:0;pointer-events:none;z-index:9000;display:none}
@media(max-width:768px){
  #sidebar{transform:translateX(-100%)}
  #sidebar.mobile-open{transform:translateX(0)}
  #main{margin-left:0;max-width:100vw}
  #bottom-tabs{display:flex}
  .chat-list{width:100%}
  .profile-posts-grid{grid-template-columns:1fr 1fr}
  .video-feed,.video-item{height:calc(100vh - 56px)}
}
"""

HTML_BODY = """
<canvas id="confetti-canvas"></canvas>
<div id="toast-container"></div>

<div id="auth-overlay">
  <div class="auth-box">
    <h1 style="font-size:1.8rem;font-weight:800;margin-bottom:6px">&#x1F31F; <span style="background:linear-gradient(135deg,#6c63ff,#00d4aa);-webkit-background-clip:text;-webkit-text-fill-color:transparent">MZN Social</span></h1>
    <p style="color:var(--muted);margin-bottom:24px;font-size:.9rem">Create, share &amp; earn real money from your content.</p>
    <div class="auth-tab-btns">
      <button class="auth-tab-btn active" id="btn-login-tab" onclick="switchAuthTab('login')">Sign In</button>
      <button class="auth-tab-btn" id="btn-register-tab" onclick="switchAuthTab('register')">Sign Up</button>
    </div>
    <div id="login-form">
      <div class="field"><label>Email</label><input id="l-email" type="email" placeholder="you@email.com"/></div>
      <div class="field"><label>Password</label><input id="l-pass" type="password"/></div>
      <button class="btn-primary" onclick="doLogin()">Sign In</button>
    </div>
    <div id="register-form" style="display:none">
      <div class="field"><label>Username</label><input id="r-user" placeholder="@username"/></div>
      <div class="field"><label>Display Name</label><input id="r-name" placeholder="Your Name"/></div>
      <div class="field"><label>Email</label><input id="r-email" type="email" placeholder="you@email.com"/></div>
      <div class="field"><label>Password</label><input id="r-pass" type="password"/></div>
      <button class="btn-primary" onclick="doRegister()">Create Account &#x2013; Start Earning!</button>
    </div>
  </div>
</div>

<div class="story-viewer" id="story-viewer">
  <div class="story-content-box">
    <span class="story-close" onclick="closeStory()">&#x2715;</span>
    <div class="post-header" style="margin-bottom:14px">
      <div class="av" id="sv-av"></div>
      <div class="post-meta"><div class="post-name" id="sv-name"></div><div class="post-username" id="sv-user"></div></div>
    </div>
    <div id="sv-content" style="line-height:1.6;margin-bottom:16px"></div>
    <div id="sv-media"></div>
    <button onclick="boostCurrentStory()" style="margin-top:16px;width:100%;padding:10px;border-radius:12px;background:linear-gradient(135deg,#ffd700,#ff6b35);color:#0a0e1a;font-weight:700">&#x26A1; Boost Memory</button>
  </div>
</div>

<div class="modal-overlay" id="withdraw-modal">
  <div class="modal-box">
    <h3>&#x1F4B8; Withdraw to Moizzen</h3>
    <div class="field"><label>Amount (ZAR)</label><input id="w-amount" type="number" min="1" step="0.01" placeholder="10.00"/></div>
    <div class="field"><label>Moizzen Email</label><input id="w-email" type="email" placeholder="your@moizzen.com"/></div>
    <div style="display:flex;gap:10px;margin-top:6px">
      <button class="btn-primary" onclick="submitWithdraw()" style="flex:1">Withdraw</button>
      <button onclick="closeWithdraw()" style="flex:1;padding:13px;border-radius:12px;border:1px solid var(--border);font-weight:600">Cancel</button>
    </div>
  </div>
</div>

<div id="app">
  <div id="sidebar">
    <div class="logo"><span style="font-size:1.5rem">&#x1F31F;</span><span class="logo-text">MZN Social</span></div>
    <div id="nav-items">
      <div class="nav-item active" onclick="showPage('home')"><span class="nav-icon">&#x1F3E0;</span>Home Feed</div>
      <div class="nav-item" onclick="showPage('videos')"><span class="nav-icon">&#x1F3A5;</span>Videos</div>
      <div class="nav-item" onclick="showPage('chat')"><span class="nav-icon">&#x1F4AC;</span>Chat</div>
      <div class="nav-item" onclick="showPage('memories')"><span class="nav-icon">&#x1F9E0;</span>Memories</div>
      <div class="nav-item" onclick="showPage('earnings')"><span class="nav-icon">&#x1F4B0;</span>Earnings</div>
      <div class="nav-item" onclick="showPage('profile')"><span class="nav-icon">&#x1F464;</span>Profile</div>
    </div>
    <div id="ticker">
      <div style="margin-bottom:4px">&#x1F4B0; Your Balance</div>
      <div class="amount" id="ticker-balance">R 0.00</div>
    </div>
  </div>
  <div id="main">

    <div class="page active" id="page-home">
      <div class="topbar"><h2>&#x1F3E0; Home Feed</h2></div>
      <div class="feed-container">
        <div class="composer">
          <div class="composer-row">
            <div class="av" id="composer-av">?</div>
            <textarea id="post-text" placeholder="What's on your mind? Share and earn!"></textarea>
          </div>
          <div class="composer-footer">
            <input id="post-media-url" placeholder="Media URL (optional)"/>
            <select class="msel" id="post-media-type">
              <option value="none">No media</option>
              <option value="image">Image</option>
              <option value="video">Video</option>
            </select>
            <button class="post-btn" onclick="createPost()">Post &#x2192;</button>
          </div>
        </div>
        <div id="feed-list"></div>
        <button onclick="loadFeed(feedPage+1)" id="load-more-btn" style="display:none;width:100%;padding:12px;border-radius:var(--radius);background:var(--bg3);border:1px solid var(--border);margin:10px 0;font-weight:600">Load More</button>
      </div>
    </div>

    <div class="page" id="page-videos">
      <div class="video-feed" id="video-feed"></div>
    </div>

    <div class="page" id="page-chat">
      <div class="topbar"><h2>&#x1F4AC; Chat</h2></div>
      <div class="chat-layout">
        <div class="chat-list" id="chat-list-el">
          <div style="padding:16px">
            <div class="field" style="margin-bottom:10px"><label>Start a chat (enter username)</label><input id="new-chat-user" placeholder="username"/></div>
            <button onclick="openC