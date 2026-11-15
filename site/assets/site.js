(function(){
  var d=document, html=d.documentElement; html.classList.remove('no-js');

  /* header + mobile menu */
  var hdr=d.querySelector('.hdr'), burger=d.querySelector('.burger');
  addEventListener('scroll',function(){hdr&&hdr.classList.toggle('scrolled',scrollY>8)},{passive:true});
  if(burger) burger.addEventListener('click',function(){
    var o=!d.body.classList.contains('menu-open'); d.body.classList.toggle('menu-open',o); burger.setAttribute('aria-expanded',o);
  });

  /* reveal */
  var rv=d.querySelectorAll('.rv');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.1,rootMargin:'0px 0px -30px 0px'});
    rv.forEach(function(el){io.observe(el)});
    /* videos play only when visible */
    var vio=new IntersectionObserver(function(es){es.forEach(function(e){
      var v=e.target; if(e.isIntersecting){ if(v.preload==='none'){v.preload='auto'} var p=v.play(); if(p&&p.catch)p.catch(function(){}) } else v.pause();
    })},{threshold:.2});
    d.querySelectorAll('video[data-autoplay]').forEach(function(v){vio.observe(v)});
  } else { rv.forEach(function(el){el.classList.add('in')}) }

  /* tabs */
  d.querySelectorAll('[role=tablist]').forEach(function(list){
    var tabs=list.querySelectorAll('[role=tab]');
    tabs.forEach(function(t){t.addEventListener('click',function(){
      tabs.forEach(function(x){var on=x===t;x.setAttribute('aria-selected',on);x.tabIndex=on?0:-1;var p=d.getElementById(x.getAttribute('aria-controls'));if(p){p.hidden=!on;if(on)p.querySelectorAll('.rv').forEach(function(r){r.classList.add('in')})}});
    })});
  });

  /* filters */
  d.querySelectorAll('[data-filters]').forEach(function(g){
    var target=d.querySelector(g.dataset.filters), btns=g.querySelectorAll('button');
    btns.forEach(function(b){b.addEventListener('click',function(){
      btns.forEach(function(x){x.setAttribute('aria-pressed',x===b)});
      target.querySelectorAll('[data-cat]').forEach(function(c){c.hidden=b.dataset.f!=='all'&&c.dataset.cat.split(' ').indexOf(b.dataset.f)<0});
    })});
  });


  /* YouTube facade: load the player only when clicked */
  d.querySelectorAll('.yt-facade').forEach(function(f){f.addEventListener('click',function(){
    var i=d.createElement('iframe');
    i.src='https://www.youtube-nocookie.com/embed/'+f.dataset.yt+'?autoplay=1&playsinline=1&rel=0&modestbranding=1';
    i.title='Bella Oloha, founder of Bella Books: video testimonial';
    i.allow='autoplay; encrypted-media; picture-in-picture; fullscreen'; i.allowFullscreen=true;
    f.replaceWith(i);
  })});

  /* cookie consent + analytics events */
  var ck=d.getElementById('cookie');
  if(ck){var saved=null;try{saved=localStorage.getItem('artlify_consent')}catch(e){}
    if(!saved) ck.hidden=false;
    ck.querySelectorAll('[data-consent]').forEach(function(b){b.addEventListener('click',function(){
      var v=b.dataset.consent;try{localStorage.setItem('artlify_consent',v)}catch(e){}
      if(window.gtag) gtag('consent','update',{analytics_storage:v}); ck.hidden=true;})});}
  function ev(name,params){if(window.gtag) gtag('event',name,params||{});}
  d.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a');if(!a)return;var h=a.getAttribute('href')||'';
    if(h.indexOf('wa.me')>-1) ev('contact',{method:'whatsapp'});
    else if(h.indexOf('mailto:')===0) ev('contact',{method:'email'});
    else if(h.indexOf('tel:')===0) ev('contact',{method:'phone'});
    else if(h.indexOf('/work-with-us')>-1) ev('cta_click',{link_text:(a.textContent||'').trim().slice(0,40)});});
  window.addEventListener('message',function(m){try{var dt=typeof m.data==='string'?JSON.parse(m.data):m.data;
    if(dt&&dt.event==='Tally.FormSubmitted') ev('generate_lead',{form_id:(dt.payload&&dt.payload.formId)||'tally'});}catch(e){}});
  var tt=d.getElementById('toTop'); if(tt) tt.addEventListener('click',function(e){e.preventDefault();scrollTo({top:0,behavior:'smooth'})});

  /* ================= enquiry form ================= */
  var box=d.getElementById('fbox'); if(!box) return;
  var tallyId=(box.dataset.tally||'').trim();
  if(tallyId){
    var form0=d.getElementById('enq'); if(form0) form0.hidden=true;
    var w=d.getElementById('tallyWrap'); w.hidden=false;
    w.innerHTML='<iframe data-tally-src="https://tally.so/embed/'+encodeURIComponent(tallyId)+'?alignLeft=1&hideTitle=1&transparentBackground=1&dynamicHeight=1&formEventsForwarding=1" loading="lazy" width="100%" height="714" frameborder="0" marginheight="0" marginwidth="0" title="Work with Artlify — enquiry form"></iframe>';
    var s=d.createElement('script'); s.src='https://tally.so/widgets/embed.js'; s.async=true;
    s.onload=function(){ if(window.Tally) Tally.loadEmbeds(); else w.querySelectorAll('iframe').forEach(function(f){f.src=f.dataset.tallySrc}) };
    s.onerror=function(){ w.querySelectorAll('iframe').forEach(function(f){f.src=f.dataset.tallySrc}) };
    d.body.appendChild(s);
    return;
  }

  var form=d.getElementById('enq'), steps=[].slice.call(form.querySelectorAll('.step')), err=d.getElementById('err');
  var back=d.getElementById('back'), next=d.getElementById('next'), cur=0;
  function vals(n){return [].slice.call(form.querySelectorAll('input[name="'+n+'"]:checked')).map(function(i){return i.value})}
  function val(n){return vals(n)[0]||''}
  function has(list){var s=vals('services');return list.some(function(x){return s.indexOf(x)>-1})}
  var DETAIL=['Social Media Management','Paid Ads & Sponsored Ads','Funnel Building','Marketing Automation','Content Creation','Not sure yet'];
  function flow(){return steps.filter(function(st){return st.dataset.step!=='details'||has(DETAIL)})}
  function logic(){
    form.querySelectorAll('[data-if]').forEach(function(el){el.hidden=!has(el.dataset.if.split('|'))});
    var shown=form.querySelectorAll('[data-step=details] .sub:not([hidden])');
    form.querySelectorAll('[data-step=details] .sub').forEach(function(x){x.style.borderTop='';x.style.marginTop='';x.style.paddingTop=''});
    if(shown[0]){shown[0].style.borderTop='0';shown[0].style.marginTop='6px';shown[0].style.paddingTop='0'}
    var monthly=val('engagement')!=='One-off project';
    var b=d.getElementById('f-budget'), prev=b.value;
    var opts=monthly?['Under $500 / month','$500 – $1,500 / month','$1,500 – $3,000 / month','$3,000 – $5,000 / month','$5,000+ / month','Not sure yet']
                    :['Under $500','$500 – $1,500','$1,500 – $3,000','$3,000 – $5,000','$5,000+','Not sure yet'];
    var key=opts.join('|'); if(b.dataset.k!==key){b.dataset.k=key;b.innerHTML='<option value="">Select a range</option>'+opts.map(function(o){return '<option'+(o===prev?' selected':'')+'>'+o+'</option>'}).join('')}
  }
  function render(){
    logic(); var fl=flow(); if(cur>fl.length-1)cur=fl.length-1;
    steps.forEach(function(s){s.classList.remove('on')}); fl[cur].classList.add('on');
    d.getElementById('progBar').style.width=((cur+1)/fl.length*100)+'%';
    d.getElementById('progTxt').textContent='Step '+(cur+1)+' of '+fl.length;
    back.hidden=cur===0;
    next.innerHTML=cur===fl.length-1?'Send enquiry <span class="arr">→</span>':'Continue <span class="arr">→</span>';
    err.classList.remove('show');
  }
  function validate(st){
    var k=st.dataset.step,m='';
    if(k==='who'&&!val('business')) m='Please choose the option that best describes your business.';
    if(k==='services'&&!vals('services').length) m='Please choose at least one service — or “Not sure yet”.';
    if(k==='goals'&&!vals('goals').length) m='Please choose at least one goal.';
    if(k==='engagement'&&!val('engagement')) m='Please choose how you would like to work with us.';
    if(k==='contact'){
      var n=form.elements.name,e=form.elements.email; var badE=!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.value.trim());
      n.parentElement.classList.toggle('err',!n.value.trim()); e.parentElement.classList.toggle('err',badE);
      if(!n.value.trim()||badE) m='Please add your name and a valid email address so we can reply.';
    }
    if(m){err.textContent=m;err.classList.add('show');return false} return true;
  }
  function top(){var r=box.getBoundingClientRect(); if(r.top<90) scrollBy({top:r.top-110,behavior:'smooth'})}
  form.addEventListener('change',function(e){
    logic(); var fl=flow();
    d.getElementById('progTxt').textContent='Step '+(cur+1)+' of '+fl.length;
    d.getElementById('progBar').style.width=((cur+1)/fl.length*100)+'%';
    if(e.target.name==='business'){setTimeout(function(){if(validate(flow()[cur])){cur++;render();top()}},240)}
  });
  back.addEventListener('click',function(){cur=Math.max(0,cur-1);render();top()});
  form.addEventListener('submit',function(e){
    e.preventDefault(); var fl=flow();
    if(!validate(fl[cur])) return;
    if(cur<fl.length-1){cur++;render();top();return}
    var data={}; new FormData(form).forEach(function(v,k){if(!v)return; data[k]=data[k]?data[k]+', '+v:v});
    function finish(){form.hidden=true;d.getElementById('done').classList.add('on');top()}
    function fail(){next.disabled=false;render();err.textContent='Something went wrong sending your enquiry. Please try again in a moment.';err.classList.add('show')}
    if(data['bot-field']) return finish(); delete data['bot-field'];
    var hosted=/^https?:$/.test(location.protocol)&&location.hostname.indexOf('claude')===-1&&location.hostname!=='localhost';
    if(hosted){
      next.disabled=true; next.textContent='Sending…'; data['form-name']='enquiry';
      fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(data).toString()})
        .then(function(r){if(!r.ok)throw 0;if(window.gtag)gtag('event','generate_lead',{form_id:'enquiry'});finish()}).catch(fail);
    } else finish();
  });
  /* preselect a service from ?service= */
  try{var q=new URLSearchParams(location.search).get('service'); if(q){var c=form.querySelector('input[name=services][value="'+q.replace(/"/g,'')+'"]'); if(c)c.checked=true}}catch(_){}
  render();
})();

/* ===== Free-audit popup (Tally form 2ja0NA) =====
   First-time visitors only. Desktop: exit intent or after 15s. Mobile: 50% scroll (or 25s).
   Never shown again after signing up; hidden for 7 days after closing. Not shown on Work With Us. */
(function(){
  var ID='2ja0NA', KEY='artlify_audit_popup', DAY=864e5;
  function get(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){return {}}}
  function set(o){try{localStorage.setItem(KEY,JSON.stringify(o))}catch(e){}}
  var st=get(); if(st.done) return; if(st.closed && Date.now()-st.closed<7*DAY) return;
  function onWWU(){return /work-with-us/.test(location.pathname+location.hash)}
  var fired=false, loading=false, timer;
  function load(cb){
    if(window.Tally) return cb();
    if(loading) return; loading=true;
    var s=document.createElement('script'); s.src='https://tally.so/widgets/embed.js'; s.async=true; s.onload=cb; document.head.appendChild(s);
  }
  function cleanup(){clearTimeout(timer);document.removeEventListener('mouseout',exit);removeEventListener('scroll',onScroll)}
  function open(){
    if(fired) return;
    if(onWWU()) return;
    fired=true; cleanup();
    load(function(){
      if(!window.Tally) return;
      Tally.openPopup(ID,{
        layout:'modal', width:520, overlay:true,
        emoji:{text:'👋',animation:'wave'},
        hiddenFields:{source:location.pathname+location.hash},
        onSubmit:function(){set({done:Date.now()})},
        onClose:function(){var x=get(); if(!x.done){x.closed=Date.now(); set(x)}}
      });
    });
  }
  function exit(e){ if(!e.relatedTarget && e.clientY<=0) open() }
  function onScroll(){ var h=document.documentElement; if(h.scrollHeight>innerHeight*1.3 && (scrollY+innerHeight)/h.scrollHeight>=0.5) open() }
  var mobile=window.matchMedia&&matchMedia('(hover: none), (max-width: 820px)').matches;
  if(mobile){ addEventListener('scroll',onScroll,{passive:true}); timer=setTimeout(open,25000) }
  else { document.addEventListener('mouseout',exit); timer=setTimeout(open,15000) }
  window.ArtlifyOpenAudit=function(){fired=false;open()};
})();
