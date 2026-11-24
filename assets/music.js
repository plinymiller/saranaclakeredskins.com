(function(){
  var list=document.getElementById("clips"); if(!list) return;
  var MAIL="plinymiller@gmail.com";
  function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
  function mm(s){s=Math.round(s);return Math.floor(s/60)+":"+("0"+s%60).slice(-2)}
  function fmtDate(d){if(!d)return "";if(d.length===4)return d;var m=["Jan.","Feb.","March","April","May","June","July","Aug.","Sept.","Oct.","Nov.","Dec."];var p=d.split("-");return m[+p[1]-1]+" "+(+p[2])+", "+p[0]}
  function mail(c){var sub="Band names: "+(c.song||"song")+" / "+c.event+" "+c.date+" ["+c.id+"]";
    var body="Clip: "+c.id+"\nI was in this band / I can name:\n\nDirector:\nDrum major:\nSoloists:\nPlayers (name, instrument, class year):\n\nMy name and class year:\n";
    return "mailto:"+MAIL+"?subject="+encodeURIComponent(sub)+"&body="+encodeURIComponent(body)}
  function director(c){
    if(c.director) return /fred baker/i.test(c.director)?'<a href="music/fred-baker.html">'+esc(c.director)+'</a>':esc(c.director);
    if(c.director_suggested) return '<a href="music/fred-baker.html">Fred Baker</a>? <span class="need">likely, not yet confirmed</span>';
    return '<span class="need">Not yet named</span>'}
  function card(c){
    var named=0,secs=Object.keys(c.roster||{}),rows=secs.map(function(s){var n=c.roster[s]||[];named+=n.length;
      return "<li><b>"+esc(s)+"</b>"+(n.length?esc(n.join(", ")):'<span class="need">Names needed</span>')+"</li>"}).join("");
    var title=c.song?esc(c.song):'<span class="tbc">Song not yet named</span>';
    var media=c.youtube_id
      ? '<button class="play" type="button" data-yt="'+esc(c.youtube_id)+'" aria-label="Play '+esc(c.song||"clip")+'"><i></i></button>'
      : '<span class="soon">Coming to YouTube</span>';
    return '<li class="clip" id="'+esc(c.id)+'"><div class="player"><img src="'+esc(c.thumb)+'" alt="Still from the clip: '+esc(c.event)+', '+esc(c.date)+'" loading="lazy" width="640" height="360">'+media+'<span class="dur">'+mm(c.duration)+'</span></div>'+
      '<div class="clip-meta"><p class="kicker">'+esc(c.event)+' &middot; '+esc(fmtDate(c.date))+'</p><h3 class="clip-title">'+title+'</h3>'+
      (c.composer?'<p>'+esc(c.composer)+'</p>':'')+
      '<dl class="credits"><dt>Band</dt><dd>'+esc(c.band)+'</dd><dt>Director</dt><dd>'+director(c)+'</dd>'+
      '<dt>Drum major</dt><dd>'+(c.drum_major?esc(c.drum_major):'<span class="need">Not yet named</span>')+'</dd>'+
      '<dt>Soloists</dt><dd>'+(c.soloists?esc(c.soloists):'<span class="need">Not yet named</span>')+'</dd></dl>'+
      '<details class="roster"><summary>Who played ('+named+' named)</summary><ul>'+rows+'</ul></details>'+
      '<a class="addnames" href="'+mail(c)+'">Add names to this clip &rarr;</a></div></li>'}
  fetch("data/music.json",{cache:"no-store"}).then(function(r){return r.json()}).then(function(d){
    var cs=d.clips||[]; document.getElementById("clip-count").textContent=cs.length+(cs.length===1?" clip":" clips");
    list.innerHTML=cs.length?cs.map(card).join(""):'<li class="need">The first clips are being cut now.</li>';
  }).catch(function(){list.innerHTML='<li class="need">Clips could not load. Try again in a moment.</li>'});
  list.addEventListener("click",function(e){var b=e.target.closest(".play");if(!b)return;
    var f=document.createElement("iframe");f.src="https://www.youtube-nocookie.com/embed/"+encodeURIComponent(b.dataset.yt)+"?autoplay=1&rel=0";
    f.allow="autoplay; encrypted-media; picture-in-picture";f.allowFullscreen=true;f.title="YouTube video";b.parentNode.appendChild(f);b.remove()});
})();
