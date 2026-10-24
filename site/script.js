const form=document.getElementById('finderForm');
form.addEventListener('submit',async event=>{event.preventDefault();const profile={age:Number(document.getElementById('age').value),residence:document.getElementById('residence').value,citizenship:document.getElementById('citizenship').value,budget:Number(document.getElementById('budget').value)};const area=document.getElementById('resultsArea');area.innerHTML='<div class="no-results"><span>↻</span><h3>Checking the catalog…</h3><p>We’re looking for opportunities that match your profile.</p></div>';try{const response=await fetch('./data/opportunities.json',{headers:{Accept:'application/json'}});if(!response.ok){showCatalogState(area,'catalog_unavailable');return}const payload=await response.json();const opportunities=Array.isArray(payload.opportunities)?payload.opportunities:[];const matches=opportunities.filter(item=>matchesProfile(item,profile));render(matches,profile,payload.updatedAt)}catch{showCatalogState(area,'catalog_unavailable')}});
function matchesProfile(item,profile){if(item.minAge!==null&&item.minAge!==undefined&&profile.age<item.minAge)return false;if(item.maxAge!==null&&item.maxAge!==undefined&&profile.age>item.maxAge)return false;if(item.budgetEur!==null&&item.budgetEur!==undefined&&item.budgetEur>profile.budget)return false;const eligible=Array.isArray(item.eligibleCountries)?item.eligibleCountries:[];if(eligible.length){const profileCountries=[profile.residence,profile.citizenship].map(normalizeCountry);const allowed=eligible.map(normalizeCountry);if(!profileCountries.some(country=>allowed.includes('worldwide')||allowed.includes('allcountries')||allowed.includes('allworld')||allowed.includes('world')||allowed.includes(country)))return false}return true}
function render(items,profile,updatedAt){const area=document.getElementById('resultsArea');if(!items.length){area.innerHTML=`<div class="no-results"><span>✳</span><h3>No close matches in this catalog yet.</h3><p>The catalog is being connected to public opportunity sources. You can search official directories directly while it grows.</p>${sourceLinks()}</div>`;return}area.innerHTML=`<div class="results-head"><div><span class="tiny-label">CATALOG LISTINGS</span><h3>Opportunities for you</h3></div><span class="result-count">${items.length} ${items.length===1?'match':'matches'}</span></div><div class="result-list">${items.map(card).join('')}</div><p class="result-disclaimer">Matched to your age, residence, citizenship and budget where the listing provides these details. Confirm all eligibility and cost information with the organizer before applying.${updatedAt?` Catalog checked ${new Date(updatedAt).toLocaleString('en',{dateStyle:'medium',timeStyle:'short'})}.`:''}</p>`}
function card(item){const uncertain=[];if(item.minAge===null||item.minAge===undefined)uncertain.push('age');if(!Array.isArray(item.eligibleCountries)||!item.eligibleCountries.length)uncertain.push('country eligibility');if(item.budgetEur===null||item.budgetEur===undefined)uncertain.push('cost');const cost=item.budgetEur===null||item.budgetEur===undefined?'Check listing':`€${Number(item.budgetEur).toLocaleString('en')}`;const deadline=item.deadline?` · Deadline ${escapeHtml(formatDate(item.deadline))}`:'';return `<article class="result-card"><div class="result-icon green">✳</div><div><span class="result-tag">${escapeHtml(item.type||'OPPORTUNITY')}</span><h4>${escapeHtml(item.title)}</h4><p>${escapeHtml(item.organizer||'Where Next catalog')} · ${cost}${deadline}</p></div><a class="result-match result-link" href="${safeUrl(item.url)}" target="_blank" rel="noreferrer">VIEW ↗</a><p class="result-details">${escapeHtml(item.summary||'Open the original listing for full details.')}${uncertain.length?`<br><b>Please verify:</b> ${escapeHtml(uncertain.join(', '))} details are not provided in this listing.`:''}</p></article>`}
function showCatalogState(area){area.innerHTML=`<div class="no-results"><span>↻</span><h3>We couldn’t load the catalog.</h3><p>Please try again in a little while. You can also search official opportunity directories directly.</p>${sourceLinks()}</div>`}
function sourceLinks(){return `<div class="source-links"><a href="https://youth.europa.eu/solidarity_en" target="_blank" rel="noreferrer">European Solidarity Corps ↗</a><a href="https://erasmus-plus.ec.europa.eu/opportunities/opportunities-for-individuals/young-people" target="_blank" rel="noreferrer">Erasmus+ for young people ↗</a><a href="https://www.daad.de/en/study-and-research-in-germany/scholarships/" target="_blank" rel="noreferrer">DAAD scholarships ↗</a></div>`}
function normalizeCountry(value){return String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]/g,'')}
function formatDate(value){const date=new Date(value);return Number.isNaN(date.getTime())?String(value):date.toLocaleDateString('en',{dateStyle:'medium'})}
function safeUrl(value){try{const url=new URL(value);return url.protocol==='https:'?escapeHtml(url.href):'#'}catch{return '#'}}
function escapeHtml(value){return String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}

async function loadSourceDirectory(){
  const grid=document.getElementById('sourceGrid');
  const count=document.getElementById('sourcesCount');
  const health=document.getElementById('sourceHealth');
  try{
    const [sourceResponse,healthResponse]=await Promise.all([
      fetch('./data/sources.json',{headers:{Accept:'application/json'}}),
      fetch('./data/source-health.json',{headers:{Accept:'application/json'}}).catch(()=>null)
    ]);
    if(!sourceResponse.ok)throw new Error('Source directory unavailable');
    const payload=await sourceResponse.json();
    const sources=Array.isArray(payload.sources)?payload.sources:[];
    count.textContent=`${sources.length} OFFICIAL SOURCES`;
    let healthMap={}; let checkedAt=null;
    if(healthResponse&&healthResponse.ok){const h=await healthResponse.json();healthMap=h.sources||{};checkedAt=h.checkedAt||null}
    const reachable=Object.values(healthMap).filter(x=>x.ok).length;
    if(checkedAt){health.textContent=`Website check: ${reachable} of ${sources.length} sources reachable · ${new Date(checkedAt).toLocaleString('en',{dateStyle:'medium',timeStyle:'short'})}`}
    else{health.textContent='Daily website availability checks are being set up.'}
    grid.innerHTML=sources.map((item,index)=>`<a class="source-card" href="${safeUrl(item.url)}" target="_blank" rel="noreferrer"><span class="source-number">${String(index+1).padStart(2,'0')}</span><span class="source-card-main"><b>${escapeHtml(item.name)}</b><small>${escapeHtml(item.region)} · ${escapeHtml(item.type)}</small></span><span class="source-access">${escapeHtml(item.access)}</span><span class="source-open">↗</span></a>`).join('');
  }catch{
    count.textContent='OFFICIAL SOURCES';
    health.textContent='The source directory could not be loaded right now.';
    grid.innerHTML='<p>Please refresh the page to try again.</p>';
  }
}
loadSourceDirectory();
