/* Member home: class board + all-classes board, directory, news, photos, your details. */
(function(){
  var $=function(id){return document.getElementById(id)};
  var val=function(id){return $(id).value.trim()};
  function say(id,kind,text){var m=$(id);m.className='msg '+kind;m.textContent=text;m.hidden=false}
  function hush(id){$(id).hidden=true}
  var firstYear = (typeof FIRST_YEAR==='number') ? FIRST_YEAR : 1890;
  var lastYear = (typeof LAST_YEAR==='number') ? LAST_YEAR : 2000;
  function yearFile(y){
    y = Number(y);
    if (y === 2000) return '00.html';
    if (y >= 1960 && y <= 1999) return ('0'+(y%100)).slice(-2)+'.html';
    return y + '.html';
  }
  function yy(y){
    y = Number(y);
    if (y >= 1960 && y <= 2000) return ('0'+(y%100)).slice(-2);
    return String(y);
  }
  function yearMark(y){
    y = Number(y);
    if (y >= 1960 && y <= 2000) return '\u2019'+yy(y);
    return String(y);
  }

  if(!(SUPABASE_URL && SUPABASE_ANON_KEY && window.supabase)){ location.replace('classes.html'); return; }
  var db = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  var uid=null, myYear=null, boardAll=false, dirAll=false, people=[];

  $('signOut').addEventListener('click', function(){ db.auth.signOut(); });
  $('copyLink').addEventListener('click', function(){
    var b=$('copyLink'), done=function(){b.textContent='Link copied';setTimeout(function(){b.textContent='Copy the link'},2200)};
    try{navigator.clipboard.writeText('https://'+$('shareLink').textContent).then(done,function(){b.textContent='Select the link above'})}catch(e){b.textContent='Select the link above'}
  });

  /* ---------- Bulletin board ---------- */
  function setBoard(all){
    boardAll=all;
    $('bdClass').setAttribute('aria-pressed', String(!all)); $('bdAll').setAttribute('aria-pressed', String(all));
    $('postingTo').textContent='';
    var t=document.createTextNode('Posting to: '), b=document.createElement('b');
    b.textContent = all ? 'All classes, '+firstYear+' to '+lastYear : 'Class of '+myYear+' only';
    $('postingTo').appendChild(t); $('postingTo').appendChild(b);
    $('postLabel').textContent = all ? 'Leave a message for every class' : 'Leave a message for the Class of '+myYear;
    hush('postMsg'); loadPosts();
  }
  $('bdClass').addEventListener('click', function(){ setBoard(false); });
  $('bdAll').addEventListener('click', function(){ setBoard(true); });
  $('postBody').addEventListener('input', function(){ $('postLeft').textContent=(1000-$('postBody').value.length)+' characters left'; });
  $('formPost').addEventListener('submit', async function(e){
    e.preventDefault(); hush('postMsg');
    var body=val('postBody');
    if(!body) return say('postMsg','err','Write a message first.');
    if(body.length>1000) return say('postMsg','err','Keep it to 1,000 characters.');
    $('postBtn').disabled=true;
    var r = await db.from('class_posts').insert({body:body, class_year: boardAll ? null : myYear});
    $('postBtn').disabled=false;
    if(r.error) return say('postMsg','err', r.error.message || 'Could not post. Try again.');
    $('postBody').value=''; $('postLeft').textContent='1000 characters left'; loadPosts();
  });
  function when(ts){ try{ return new Date(ts).toLocaleString([], {year:'numeric',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}); }catch(e){ return ''; } }
  async function loadPosts(){
    var want=boardAll;
    var r = await db.rpc('board_posts',{p_all:want});
    if(want!==boardAll) return;
    var rows=(r.error||!r.data)?[]:r.data; var box=$('postList'); box.textContent='';
    $('postEmpty').hidden=!!rows.length;
    $('postEmpty').textContent = want ? 'No messages on the all-classes board yet. Be the first to say hello.' : 'No messages from the Class of '+myYear+' yet. Be the first to say hello.';
    $('postCount').textContent = rows.length ? rows.length+(rows.length===1?' message':' messages') : '';
    rows.forEach(function(p){
      var a=document.createElement('article'); a.className='post';
      var h=document.createElement('header');
      var by=document.createElement('span'); by.className='by'; by.textContent=((p.first_name||'')+' '+(p.last_name||'')).trim()||'A classmate';
      if(want && p.author_year){ var tg=document.createElement('span'); tg.className='tag'; tg.textContent=yearMark(p.author_year); by.appendChild(tg); }
      var w=document.createElement('span'); w.className='when'; w.textContent=when(p.created_at);
      h.appendChild(by); h.appendChild(w); a.appendChild(h);
      var t=document.createElement('p'); t.textContent=p.body||''; a.appendChild(t);
      if(p.mine){ var d=document.createElement('button'); d.type='button'; d.className='link'; d.textContent='Remove my message';
        d.addEventListener('click', async function(){ d.disabled=true; var x=await db.from('class_posts').delete().eq('id',p.id); if(x.error){ d.disabled=false; say('postMsg','err',x.error.message); } else loadPosts(); });
        a.appendChild(d); }
      box.appendChild(a);
    });
  }

  /* ---------- Directory ---------- */
  function cell(text){ var td=document.createElement('td'); td.textContent=text||''; return td; }
  function personName(p){ return (p.first_name+' '+p.last_name+(p.grad_name?' ('+p.grad_name+')':'')).trim(); }
  function personCity(p){ return [p.addr_city,p.addr_state].filter(Boolean).join(', '); }
  function addRow(dl, label, value){
    if(!value) return;
    var dt=document.createElement('dt'); dt.textContent=label;
    var dd=document.createElement('dd'); dd.textContent=value;
    dl.appendChild(dt); dl.appendChild(dd);
  }
  function drawDirectory(){
    var q=val('dirSearch').toLowerCase();
    var tb=$('dirTable').querySelector('tbody'); tb.textContent='';
    var cards=$('dirCards'); if(cards) cards.textContent='';
    var rows=people.filter(function(p){ return !q || [p.first_name,p.last_name,p.grad_name,p.addr_city,p.addr_state,p.class_year].join(' ').toLowerCase().indexOf(q)>-1; });
    $('dirTable').hidden=!rows.length; $('dirEmpty').hidden=!!rows.length;
    $('dirEmpty').textContent = people.length ? 'No one matches that search.' : (dirAll ? 'No one listed yet.' : 'No one from the Class of '+myYear+' is listed yet.');
    $('dirCount').textContent = people.length ? (q ? rows.length+' of '+people.length+' listed' : people.length+' listed') : '';
    rows.forEach(function(p){
      var tr=document.createElement('tr');
      tr.appendChild(cell(personName(p)));
      tr.appendChild(cell(p.class_year ? String(p.class_year) : ''));
      tr.appendChild(cell(personCity(p)));
      tr.appendChild(cell(p.email)); tr.appendChild(cell(p.cell)); tb.appendChild(tr);
      if(cards){
        var art=document.createElement('article'); art.className='person';
        var h=document.createElement('h3'); h.textContent=personName(p); art.appendChild(h);
        var dl=document.createElement('dl');
        addRow(dl,'Class', p.class_year ? String(p.class_year) : '');
        addRow(dl,'City', personCity(p));
        addRow(dl,'Email', p.email||'');
        addRow(dl,'Cell', p.cell||'');
        art.appendChild(dl); cards.appendChild(art);
      }
    });
  }
  $('dirSearch').addEventListener('input', drawDirectory);
  async function loadDirectory(){
    var want=dirAll; var r = await db.rpc('class_directory',{p_all:want});
    if(want!==dirAll) return;
    people=(r.error||!r.data)?[]:r.data; drawDirectory();
  }
  function setDir(all){
    dirAll=all; $('drClass').setAttribute('aria-pressed', String(!all)); $('drAll').setAttribute('aria-pressed', String(all)); loadDirectory();
  }
  $('drClass').addEventListener('click', function(){ setDir(false); });
  $('drAll').addEventListener('click', function(){ setDir(true); });

  /* ---------- News and photos ---------- */
  async function loadNews(){
    var r = await db.from('class_news').select('posted_on,title,body,class_year').order('posted_on',{ascending:false});
    var box=$('newsList'); if(r.error||!r.data||!r.data.length) return;
    box.textContent='';
    r.data.forEach(function(n){ var a=document.createElement('article');
      var d=document.createElement('span'); d.className='label'; d.textContent=(n.posted_on||'')+(n.class_year?'  \u00b7  Class of '+n.class_year:'  \u00b7  All classes');
      var h=document.createElement('h3'); h.textContent=n.title||'';
      var p=document.createElement('p'); p.textContent=n.body||'';
      a.appendChild(d); a.appendChild(h); a.appendChild(p); box.appendChild(a); });
  }
  async function loadPhotos(){
    var r = await db.from('class_photos').select('image_url,caption').order('sort_order',{ascending:true});
    var g=$('photoGrid'); g.textContent=''; var rows=(r.error||!r.data)?[]:r.data; $('photoEmpty').hidden=!!rows.length;
    rows.forEach(function(ph){ if(!/^https:\/\//.test(ph.image_url||'')) return;
      var f=document.createElement('figure'); var i=document.createElement('img'); i.src=ph.image_url; i.alt=ph.caption||'Class photo'; i.loading='lazy';
      var c=document.createElement('figcaption'); c.textContent=ph.caption||''; f.appendChild(i); f.appendChild(c); g.appendChild(f); });
  }

  /* ---------- Your details ---------- */
  $('formMe').addEventListener('submit', async function(e){
    e.preventDefault(); hush('meMsg');
    if(!val('meFirst')||!val('meLast')) return say('meMsg','err','Enter your first and last name.');
    if(val('meCell').replace(/\D/g,'').length<10) return say('meMsg','err','Enter your cell number with area code.');
    if(!uid) return;
    var r = await db.from('profiles').update({ first_name:val('meFirst'), last_name:val('meLast'), grad_name:val('meGrad'), cell:val('meCell'),
      addr_street:val('meStreet'), addr_city:val('meCity'), addr_state:val('meState'), addr_zip:val('meZip'),
      listed:$('meListed').checked, show_email:$('meShowEmail').checked, show_cell:$('meShowCell').checked }).eq('id', uid);
    if(r.error) say('meMsg','err', r.error.message); else { say('meMsg','ok','Saved.'); loadDirectory(); loadPosts(); }
  });

  async function render(session){
    if(!session){ location.replace('classes.html'); return; }
    uid=session.user.id;
    var r = await db.from('profiles').select('*').eq('id',uid).maybeSingle();
    var me = r.data || {};
    myYear = me.class_year || 1988;
    document.title = 'Class of '+myYear+' Home';
    $('yrTitle').textContent = myYear;
    $('shareLink').textContent = 'saranaclakeredskins.com/'+yearFile(myYear);
    $('bdClass').textContent = 'Class of '+myYear; $('drClass').textContent = 'Class of '+myYear;
    $('photoLabel').textContent = 'Class of '+myYear;
    $('whoName').textContent = (me.first_name ? me.first_name+' '+(me.last_name||'') : session.user.email)+'  \u00b7  '+yearMark(myYear);
    $('meUser').textContent = (me.username ? 'Username: '+me.username+'  \u00b7  ' : '')+'Class of '+myYear;
    [['meFirst','first_name'],['meLast','last_name'],['meGrad','grad_name'],['meCell','cell'],['meStreet','addr_street'],['meCity','addr_city'],['meState','addr_state'],['meZip','addr_zip']]
      .forEach(function(p){ $(p[0]).value = me[p[1]] || ''; });
    $('meListed').checked=!!me.listed; $('meShowEmail').checked=!!me.show_email; $('meShowCell').checked=!!me.show_cell;
    var ok=!!me.approved; $('pending').hidden=ok; $('roomPhotos').hidden=!ok;
    $('page').hidden=false; $('who').hidden=false;
    setBoard(false); setDir(false); loadNews(); if(ok) loadPhotos();
  }
  var drawn=false;
  db.auth.onAuthStateChange(function(event, session){
    if(session && drawn && event!=='SIGNED_OUT') return;
    drawn=!!session; setTimeout(function(){ render(session); },0);
  });
})();
