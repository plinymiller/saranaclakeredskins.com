/* Sign-in desk for one class year. CLASS_YEAR is set by the page. */
(function(){
  var $=function(id){return document.getElementById(id)};
  var val=function(id){return $(id).value.trim()};
  function say(id,kind,text){var m=$(id);m.className='msg '+kind;m.textContent=text;m.hidden=false}
  function hush(id){$(id).hidden=true}
  function show(view){['viewOut','viewReset'].forEach(function(v){$(v).hidden=(v!==view)})}
  function tab(up){$('tabUp').setAttribute('aria-selected',up);$('tabIn').setAttribute('aria-selected',!up);$('formUp').hidden=!up;$('formIn').hidden=up}
  $('tabUp').addEventListener('click',function(){tab(true)});
  $('tabIn').addEventListener('click',function(){tab(false)});

  var ready = SUPABASE_URL && SUPABASE_ANON_KEY && window.supabase;
  if(!ready){
    $('offNote').hidden=false;
    ['upBtn','inBtn','forgot'].forEach(function(b){$(b).disabled=true});
    ['formUp','formIn'].forEach(function(f){$(f).addEventListener('submit',function(e){e.preventDefault()})});
    return;
  }
  var db = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  var here = location.origin + location.pathname;
  var home = new URL('welcome.html', location.href).href;
  var recovering = false;

  $('formUp').addEventListener('submit', async function(e){
    e.preventDefault(); hush('upMsg');
    var user=val('upUser'), pass=$('upPass').value, email=val('upEmail'), cell=val('upCell');
    if(!val('upFirst')||!val('upLast')) return say('upMsg','err','Enter your first and last name.');
    if(!/^[A-Za-z0-9_.\-]{3,24}$/.test(user)) return say('upMsg','err','Choose a username of 3 to 24 letters, numbers, dots, dashes or underscores.');
    if(pass.length<8) return say('upMsg','err','Choose a password of at least 8 characters.');
    if(!/^\S+@\S+\.\S+$/.test(email)) return say('upMsg','err','Enter a valid email address.');
    if(cell.replace(/\D/g,'').length<10) return say('upMsg','err','Enter your cell number with area code.');
    if(!$('upConsent').checked) return say('upMsg','err','Tick the box agreeing to be contacted about class news.');
    $('upBtn').disabled=true;
    try{
      var free = await db.rpc('username_available',{candidate:user});
      if(free.error) throw free.error;
      if(free.data===false){ say('upMsg','err','That username is taken. Try another.'); return; }
      var r = await db.auth.signUp({email:email,password:pass,options:{emailRedirectTo:home,data:{
        class_year:CLASS_YEAR, username:user, first_name:val('upFirst'), last_name:val('upLast'), grad_name:val('upGrad'), cell:cell,
        addr_street:val('upStreet'), addr_city:val('upCity'), addr_state:val('upState'), addr_zip:val('upZip'),
        listed:$('upListed').checked, show_email:$('upShowEmail').checked, show_cell:$('upShowCell').checked }}});
      if(r.error) throw r.error;
      if(!r.data.session) say('upMsg','ok','Almost done. We sent a confirmation link to '+email+'. Open it to finish creating your account.');
    }catch(err){ say('upMsg','err', err.message || 'Could not create the account. Try again.'); }
    finally{ $('upBtn').disabled=false; }
  });

  $('formIn').addEventListener('submit', async function(e){
    e.preventDefault(); hush('inMsg'); $('inBtn').disabled=true;
    var r = await db.auth.signInWithPassword({email:val('inEmail'),password:$('inPass').value});
    $('inBtn').disabled=false;
    if(r.error) say('inMsg','err', r.error.message==='Email not confirmed' ? 'Open the confirmation link we emailed you, then log in.' : 'That email and password do not match an account.');
  });

  $('forgot').addEventListener('click', async function(){
    var email=val('inEmail');
    if(!email) return say('inMsg','err','Enter your email above, then choose Forgot your password.');
    var r = await db.auth.resetPasswordForEmail(email,{redirectTo:here});
    if(r.error) say('inMsg','err', r.error.message); else say('inMsg','ok','If that email has an account, a reset link is on its way.');
  });

  $('formReset').addEventListener('submit', async function(e){
    e.preventDefault();
    if($('rsPass').value.length<8) return say('rsMsg','err','Choose a password of at least 8 characters.');
    var r = await db.auth.updateUser({password:$('rsPass').value});
    if(r.error) return say('rsMsg','err', r.error.message);
    recovering=false; var s=await db.auth.getSession(); render(s.data.session);
  });

  function render(session){
    if(recovering){ show('viewReset'); return; }
    if(session){
      var next=null; try{ next=localStorage.getItem('slr_next'); localStorage.removeItem('slr_next'); }catch(e){}
      location.replace(next && /^teachers\/index\.html(\?t=[a-z0-9-]{1,90})?$/.test(next) ? next : 'welcome.html'); return;
    }
    show('viewOut');
  }

  db.auth.onAuthStateChange(function(event, session){
    if(event==='PASSWORD_RECOVERY') recovering=true;
    setTimeout(function(){ render(session); },0);
  });
})();
