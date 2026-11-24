const $=i=>document.getElementById(i),f=$('give'),w=$('wait'),err=$('err'),go=$('go'),retry=$('retry'),again=$('again'),findlink=$('findlink'),toast=$('toast'),mine=$('mine'),custom=$('custom');
const calm=matchMedia('(prefers-reduced-motion:reduce)').matches;
const store={get(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}},del(k){try{localStorage.removeItem(k)}catch(e){}}};
const say=m=>{toast.textContent=m;toast.hidden=!m},show=m=>{err.textContent=m;err.hidden=!m};
const SEND='Give with M-Pesa';let timer;
function panel(title,msg,o){f.hidden=true;w.hidden=false;$('wt').textContent=title;$('wm').textContent=msg;$('spin').hidden=!o.spin;
  retry.hidden=!o.retry;again.hidden=!o.again;findlink.hidden=!o.find;if(o.again)again.onclick=()=>{panel('Checking again','Looking for your payment…',{spin:1});poll(o.again)};
  w.scrollIntoView({behavior:calm?'auto':'smooth',block:'center'})}
function reset(){clearTimeout(timer);w.hidden=true;f.hidden=false;go.disabled=false;go.textContent=SEND}
retry.onclick=()=>{store.del('pending');reset()};
findlink.onclick=()=>{$('find').open=true};
async function poll(ref,n=0,fails=0){
  clearTimeout(timer);
  if(n>34){panel('Still waiting','If you entered your PIN, it can take a little longer. Check again, or ask for a new prompt.',{again:ref,retry:1,find:1});return}
  try{const r=await fetch('/check/'+ref+'/');if(!r.ok)throw 0;const j=await r.json();fails=0;say('');
    if(j.status==='paid'){store.set('album_link',j.url);store.del('pending');panel('Asante sana!','Your gift is in. Opening your album…',{});navigator.vibrate&&navigator.vibrate(20);setTimeout(()=>location.href=j.url,900);return}
    if(j.status==='failed'){store.del('pending');panel('That didn’t go through',j.reason||'The payment was cancelled or didn’t complete.',{retry:1,find:1});return}
  }catch(e){if(++fails>=3)say('Having trouble reaching the server. Your payment is safe, and we’ll keep trying.')}
  timer=setTimeout(()=>poll(ref,n+1,fails),3000)}
// feedback when something breaks
addEventListener('offline',()=>say('You’re offline. We’ll carry on when you’re back.'));
addEventListener('online',()=>say(''));
addEventListener('unhandledrejection',()=>say('Something went wrong on our side. Please refresh and try again.'));
// inline phone check
const ph=f.phone,hint=document.createElement('p');hint.className='hint';hint.hidden=true;ph.after(hint);
const okPhone=v=>/^(?:\+?254|0)?[17]\d{8}$/.test(v.replace(/\s/g,''));
ph.addEventListener('blur',()=>{const bad=ph.value&&!okPhone(ph.value);ph.setAttribute('aria-invalid',bad);hint.hidden=!bad;hint.textContent=bad?'Use a Safaricom number like 0712 345 678.':''});
ph.addEventListener('input',()=>{if(okPhone(ph.value)){ph.removeAttribute('aria-invalid');hint.hidden=true}});
custom.addEventListener('focus',()=>{f.querySelector('input[value=custom]').checked=true});
$('listen').addEventListener('click',()=>setTimeout(()=>{const c=f.querySelector('input[name=amount]:checked');c&&c.focus({preventScroll:true})},500));
f.addEventListener('submit',async e=>{e.preventDefault();show('');
  const d=new FormData(f);let a=d.get('amount');if(a==='custom')a=custom.value;
  if(!okPhone(ph.value)){ph.focus();ph.dispatchEvent(new Event('blur'));return}
  go.disabled=true;go.textContent='Sending your prompt…';
  const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),20000);
  try{
    const r=await fetch('/pay/',{method:'POST',signal:ctl.signal,headers:{'X-CSRFToken':d.get('csrfmiddlewaretoken')},body:JSON.stringify({amount:a,phone:d.get('phone'),name:d.get('name'),email:d.get('email')})});
    const j=await r.json().catch(()=>({}));
    if(!r.ok){show(j.error||'Something went wrong on our side. Please try again in a moment.');go.disabled=false;go.textContent=SEND;return}
    store.set('pending',{ref:j.ref,t:Date.now()});panel('Check your phone','Enter your M-Pesa PIN to give KES '+a+'.',{spin:1});poll(j.ref);
  }catch(x){show('We couldn’t confirm that request. If an M-Pesa prompt reaches your phone, enter your PIN, then use “Find my album” below. Otherwise check your connection and try again.');go.disabled=false;go.textContent=SEND}
  finally{clearTimeout(to)}});
// come back later
const link=store.get('album_link'),p=store.get('pending');
if(link){mine.hidden=false;mine.querySelector('a').href=link}
else if(p&&Date.now()-p.t<20*60e3){panel('Welcome back','Checking on your payment…',{spin:1});poll(p.ref)}
else store.del('pending');
