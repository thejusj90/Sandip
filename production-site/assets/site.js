(()=> {
 const menu=document.querySelector('.mobile-menu'), nav=document.querySelector('#navigation');
 const show=(yes,focus=false)=>{nav.classList.toggle('open',yes);menu.setAttribute('aria-expanded',String(yes));if(focus)menu.focus()};
 menu.addEventListener('click',()=>show(!nav.classList.contains('open')));
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open'))show(false,true)});
 document.addEventListener('click',e=>{if(nav.classList.contains('open')&&!nav.contains(e.target)&&!menu.contains(e.target))show(false)});
 const form=document.querySelector('#project-enquiry');if(!form)return;
 const q=new URLSearchParams(location.search),sector=form.elements.sector,interest=form.elements.interest;
 const fill=(control,key)=>{const v=q.get(key);if(v&&Array.from(control.options).some(o=>o.value===v))control.value=v};
 fill(sector,'sector');fill(interest,'interest');
 const details=document.querySelector('#project-details');if(details&&(q.has('sector')||q.has('interest')))details.open=true;
 const hint=document.querySelector('#brief-hint'), update=()=>{hint.textContent=sector.value==='impact-advisory'||/^(impact-|decision-impact-)/.test(interest.value)?'What decision or outcome are you working towards? Who could be affected, what stage are you at and when do you need to act?':'Tell us who the project is for, your priorities and what you would like to achieve.'};
 update();sector.addEventListener('change',update);interest.addEventListener('change',update);
 const status=document.querySelector('#form-status'),button=form.querySelector('button[type="submit"]');
 form.addEventListener('submit',e=>{
  if(form.dataset.live!=='true'){
   e.preventDefault();status.textContent='This is a preview. Your enquiry has not been sent.';return;
  }
  if(form.elements._honey?.value){e.preventDefault();return;}
  // Keep the native POST so the provider can show verification, activation or errors.
  // Do not disable the button: a provider error or Back navigation must allow a retry.
  status.textContent='Opening the secure enquiry service. Complete any verification shown to send your message.';
 });
})();
