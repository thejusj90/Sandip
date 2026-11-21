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
 form.addEventListener('submit',async e=>{
  e.preventDefault();
  if(form.dataset.live!=='true'){status.textContent='This is a preview. Your enquiry has not been sent.';return;}
  if(button.disabled||!form.reportValidity())return;
  if(form.elements._honey?.value)return;
  const originalLabel=button.textContent;
  button.disabled=true;button.textContent='Sending…';form.setAttribute('aria-busy','true');status.textContent='Sending your enquiry…';
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
  try{
   const endpoint=new URL(form.action);
   endpoint.pathname='/ajax'+endpoint.pathname;
   const payload=Object.fromEntries(new FormData(form));
   delete payload._next;
   const response=await fetch(endpoint.href,{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(payload),signal:controller.signal});
   const result=await response.json();
   if(!response.ok||!(result.success===true||result.success==='true'))throw new Error('Submission not confirmed');
   status.textContent='Thank you. The enquiry service has accepted your message. You can also contact hello@dipatmawellness.com directly.';
   form.reset();fill(sector,'sector');fill(interest,'interest');update();
  }catch(error){
   status.textContent='We could not confirm your submission. Your details are still here. Please email hello@dipatmawellness.com or try again.';
  }finally{
   clearTimeout(timer);button.disabled=false;button.textContent=originalLabel;form.removeAttribute('aria-busy');
  }
 });
})();
