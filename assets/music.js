(function(){
  var list=document.getElementById("clips"); if(!list) return;
  var MAIL="plinymiller@gmail.com", all=[], onlyLikely=false;
  function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
  function mm(s){s=Math.round(s);return Math.floor(s/60)+":"+("0"+s%60).slice(-2)}
  function tapeTime(t){return (t||"").replace(/^00:/,"").replace(/^0/,"")}
  function mail(c){var sub="Band names: "+(c.song||"clip")+" / "+c.tape+" at "+c.tape_time+" ["+c.id+"]";
    var body="Clip: "+c.id+" ("+c.tape+", starts "+c.tape_time+")\nSong title (if you know it):\nWhich band is this:\nDirector:\nDrum major:\nSoloists:\nPlayers (name, instrument, class year):\n\nMy name and class year:\n";
    return "mailto:"+MAIL+"?subject="+encodeURIComponent(sub)+"&body="+encodeURIComponent(body)}
  function director(c){
    if(c.director) return /fred baker/i.test(c.director)?'<a href="music/fred-baker.html">'+esc(c.director)+'</a>':esc(c.director);
    if(c.director_suggested) return 'If this is the Saranac Lake band: <a href="music/fred-baker.html">Fred Baker</a>? <span class="need">likely, not yet confirmed</span>';
    return '<span class="need">Not yet named</span>'}
  function card(c){
    var named=0,rows=Object.keys(c.roster||{}).map(function(s){var n=c.roster[s]||[];named+=n.length;
      return "<li><b>"+esc(s)+"</b>"+(n.length?esc(n.join(", ")):'<span class="need">Names needed</span>')+"</li>"}).join("");
    var media=c.youtube_id?'<button class="play" type="button" data-yt="'+esc(c.youtube_id)+'" aria-label="Play clip"><i></i></button>':'';
    var badge=c.tier==="likely"?'<span class="soon">Band playing</span>':'<span class="soon chk">Music &middot; check</span>';
    return '<li class="cc" id="'+esc(c.id)+'"><div class="player"><img src="'+esc(c.thumb)+'" alt="Still from '+esc(c.date+' '+(c.tape_label||c.tape))+' at '+esc(c.tape_time)+'" loading="lazy" width="640" height="480">'+badge+media+'<span class="dur">'+mm(c.duration)+'</span></div>'+
      '<h4 class="cc-t">'+(c.song?esc(c.song):esc(c.display_title||'Band selection')+' <span class="tbc">&middot; song not yet named</span>')+'</h4>'+
      '<p class="cc-m">Starts '+esc(tapeTime(c.tape_time))+' into the tape'+(c.youtube_id?'':' &middot; YouTube soon')+'</p>'+
      '<details class="roster"><summary>Credits ('+named+' named)</summary><dl class="credits"><dt>Band</dt><dd>'+(c.band?esc(c.band):'<span class="need">Which band? Tell us</span>')+'</dd><dt>Director</dt><dd>'+director(c)+'</dd>'+
      '<dt>Drum major</dt><dd>'+(c.drum_major?esc(c.drum_major):'<span class="need">Not yet named</span>')+'</dd><dt>Soloists</dt><dd>'+(c.soloists?esc(c.soloists):'<span class="need">Not yet named</span>')+'</dd></dl><ul>'+rows+'</ul></details>'+
      '<a class="addnames" href="'+mail(c)+'">Add names or the song &rarr;</a></li>'}
  function render(){
    var cs=all.filter(function(c){return !onlyLikely||c.tier==="likely"}), groups=[], by={};
    cs.forEach(function(c){if(!by[c.tape]){by[c.tape]={tape:c.tape,label:c.tape_label||c.tape.replace(/^\d{4}\s*/,""),date:c.date,clips:[]};groups.push(by[c.tape])}by[c.tape].clips.push(c)});
    document.getElementById("clip-count").textContent=cs.length+(cs.length===1?" clip":" clips")+" from "+groups.length+(groups.length===1?" tape":" tapes");
    var jump=document.getElementById("tape-jump"); if(jump) jump.innerHTML=groups.map(function(g,i){return '<li><a href="#tape-'+i+'">'+esc(g.date+' \u00b7 '+g.label)+' <span>'+g.clips.length+'</span></a></li>'}).join("");
    list.innerHTML=groups.length?groups.map(function(g,i){var lk=g.clips.filter(function(c){return c.tier==="likely"}).length;
      return '<li class="tape" id="tape-'+i+'"><div class="tape-h"><p class="kicker">'+esc(g.date)+'</p><h3>'+esc(g.label)+'</h3><p class="mu-count">'+g.clips.length+(g.clips.length===1?' clip':' clips')+' &middot; '+lk+' with the band clearly playing</p></div><ul class="cc-grid">'+g.clips.map(card).join("")+'</ul></li>'}).join(""):'<li class="need">The first clips are being cut now.</li>';
  }
  fetch("data/music.json",{cache:"no-store"}).then(function(r){return r.json()}).then(function(d){all=d.clips||[];render()})
    .catch(function(){list.innerHTML='<li class="need">Clips could not load. Try again in a moment.</li>'});
  var f=document.getElementById("only-likely"); if(f) f.addEventListener("change",function(){onlyLikely=f.checked;render()});
  list.addEventListener("click",function(e){var b=e.target.closest(".play");if(!b)return;
    var fr=document.createElement("iframe");fr.src="https://www.youtube-nocookie.com/embed/"+encodeURIComponent(b.dataset.yt)+"?autoplay=1&rel=0";
    fr.allow="autoplay; encrypted-media; picture-in-picture";fr.allowFullscreen=true;fr.title="YouTube video";b.parentNode.appendChild(fr);b.remove()});
})();
