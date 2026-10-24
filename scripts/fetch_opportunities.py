"""Scheduled importer for public youth and academic opportunity feeds."""
import datetime as dt,email.utils,html,json,pathlib,re,urllib.parse,urllib.request,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=ROOT/'site/data/opportunities.json'; UA='WhereNext/1.0 (+https://sergosangreal-oss.github.io/where-next/)'
Y=re.compile(r'\b(youth|young people|student|scholarship|fellowship|exchange|internship|summer school|volunteer|erasmus|study abroad|training|mobility|graduate|doctoral|phd|postdoc|master)\b',re.I)
R=re.compile(r'\b(student|doctoral|doctorate|phd|postdoc|master|early-career|young scientist|graduate|undergraduate)\b',re.I)
EU='Austria Belgium Bulgaria Croatia Cyprus Czechia Denmark Estonia Finland France Germany Greece Hungary Ireland Italy Latvia Lithuania Luxembourg Malta Netherlands Poland Portugal Romania Slovakia Slovenia Spain Sweden'.split()
C=dict(zip('AT DE CH BE BG HR CY CZ DK EE FI FR GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE IS LI NO'.split(),'Austria Germany Switzerland Belgium Bulgaria Croatia Cyprus Czechia Denmark Estonia Finland France Greece Hungary Ireland Italy Latvia Lithuania Luxembourg Malta Netherlands Poland Portugal Romania Slovakia Slovenia Spain Sweden Iceland Liechtenstein Norway'.split()))
def get(u,b=None,t=None):
 h={'User-Agent':UA,'Accept':'application/json, application/rss+xml, application/xml, text/xml'}
 if t:h['Content-Type']=t
 with urllib.request.urlopen(urllib.request.Request(u,data=b,headers=h),timeout=25) as r:return r.read()
def base(i,t,k,o,u,s,src,upd=None,due=None,loc=None):return {'id':i,'title':t,'type':k,'organizer':o,'url':u,'summary':s,'location':loc,'minAge':None,'maxAge':None,'eligibleCountries':[],'budgetEur':None,'deadline':due,'source':src,'sourceType':'Public API/RSS','sourceUpdatedAt':upd}
def due(s):
 m=re.search(r'deadline\s*:?\s*([A-Z][a-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+)\d{4})',s,re.I)
 if not m:return None
 v=re.sub(r'(\d)(st|nd|rd|th)',r'\1',m.group(1),flags=re.I).replace(',','')
 for f in ('%B %d %Y','%b %d %Y'):
  try:return dt.datetime.strptime(v,f).date().isoformat()
  except ValueError:pass
 return None
def rss(u,src,research=False):
 x=ET.fromstring(get(u));out=[]
 for a in list(x.findall('.//item'))+list(x.findall('.//{http://www.w3.org/2005/Atom}entry')):
  title=(a.findtext('title') or a.findtext('{http://www.w3.org/2005/Atom}title') or '').strip(); ln=a.find('{http://www.w3.org/2005/Atom}link');url=(a.findtext('link') or (ln.get('href') if ln is not None else '') or '').strip(); desc=a.findtext('description') or a.findtext('{http://www.w3.org/2005/Atom}summary') or '';summary=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',desc))).strip()
  if not title or not url.startswith('https://') or not (R if research else Y).search(title+' '+summary):continue
  d=due(title+' '+summary)
  if d and d<dt.datetime.now(dt.timezone.utc).date().isoformat():continue
  pub=a.findtext('pubDate') or a.findtext('{http://www.w3.org/2005/Atom}published') or a.findtext('{http://www.w3.org/2005/Atom}updated')
  try:pub=email.utils.parsedate_to_datetime(pub).astimezone(dt.timezone.utc).isoformat()
  except Exception:
   try:pub=dt.datetime.fromisoformat(pub.replace('Z','+00:00')).astimezone(dt.timezone.utc).isoformat()
   except Exception:pub=None
  out.append(base(src.lower()+':'+url,title,'Academic opportunity' if research else 'Opportunity',src+' listing',url,summary[:600],src,pub,d))
 return out
def tech():
 out=[]
 for typ in ('internship','new-grad'):
  for page in (1,2):
   q=urllib.parse.urlencode({'type':typ,'page':page,'page-size':100});p=json.loads(get('https://techopportunities.eu/api/v1/opportunities?'+q));rows=p.get('data',[])
   for a in rows:
    title=a.get('title') or '';u=a.get('link') or ''
    if title and u.startswith('https://'):out.append(base('eto:'+str(a.get('linkedinJobId') or u),title,'Internship' if typ=='internship' else 'Graduate role',a.get('company') or 'Employer not listed',u,' · '.join(str(a[k]) for k in ('location','employmentType','startDate') if a.get(k)),'European Tech Opportunities',a.get('firstSeenAt'),loc=a.get('location')))
   if not rows or page >= (p.get('pagination',{}).get('totalPages') or 1):break
 return out
def radar():
 p=json.loads(get('https://researchradar.at/api/v1/grants?status=open,rolling'));out=[]
 for a in p.get('data',[]):
  title=(a.get('name_en') or a.get('name') or '').strip();txt=title+' '+(a.get('target_group_en') or '')+' '+(a.get('description_en') or '');u=a.get('application_url') or a.get('website') or ''
  if not title or not R.search(txt) or not u.startswith('https://'):continue
  c=[]
  for x in a.get('eligibility_countries') or []:c.extend(EU if x=='EU' else [C.get(x,x)])
  dates=a.get('deadline_dates') or [];d=next((x for x in dates if isinstance(x,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',x) and x>=dt.date.today().isoformat()),None)
  z=base('rr:'+str(a.get('id') or u),title,'Research funding / award',a.get('institution') or 'ResearchRadar listed funder',u,(a.get('description_en') or '')[:900],'ResearchRadar.at',a.get('source_checked'),d);z['eligibleResidenceCountries']=c;out.append(z)
 return out
def grants():
 out=[]
 for kw in ('scholarship','fellowship','student internship','youth exchange'):
  for start in (0,100,200):
   b=json.dumps({'keyword':kw,'oppStatuses':'posted','eligibilities':'21','rows':100,'startRecordNum':start}).encode();p=json.loads(get('https://api.grants.gov/v1/api/search2',b,'application/json'))
   if p.get('errorcode')!=0:raise ValueError('Grants.gov error')
   d=p.get('data') or {};rows=d.get('oppHits') or []
   for a in rows:
    title=a.get('title') or '';n=a.get('id')
    if not title or not n or not Y.search(title):continue
    end=None
    try:end=dt.datetime.strptime(a.get('closeDate',''),'%m/%d/%Y').date().isoformat()
    except ValueError:pass
    if not end or end>=dt.date.today().isoformat():out.append(base('grants:'+str(n),title,'US individual opportunity',a.get('agencyName') or 'U.S. federal agency','https://www.grants.gov/search-results-detail/'+str(n),'Listed as open to individual applicants. Verify nationality, age and award terms.','Grants.gov',a.get('openDate'),end,'United States'))
   if start+len(rows)>=(d.get('hitCount') or 0) or not rows:break
 return out
FEEDS=[('European Tech Opportunities','https://techopportunities.eu/api/v1/opportunities',tech),('Opportunity Desk','https://opportunitydesk.org/feed/',lambda:rss('https://opportunitydesk.org/feed/','Opportunity Desk')),('ScholarshipHunter','https://scholarshiphunter.app/feed.xml',lambda:rss('https://scholarshiphunter.app/feed.xml','ScholarshipHunter',True)),('Grants.gov RSS','https://www.grants.gov/rss/GG_NewOppByCategory.xml',lambda:rss('https://www.grants.gov/rss/GG_NewOppByCategory.xml','Grants.gov')),('Grants.gov','https://api.grants.gov/v1/api/search2',grants),('ResearchRadar.at','https://researchradar.at/api/v1/grants',radar)]
def main():
 now=dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat();rows=[];status=[]
 for name,url,fn in FEEDS:
  try:
   got=fn()
   for a in got:a['sourceConnector']=name
   rows+=got;status.append({'name':name,'url':url,'ok':True,'count':len(got),'checkedAt':now});print(name,len(got))
  except Exception as e:status.append({'name':name,'url':url,'ok':False,'count':0,'checkedAt':now,'error':type(e).__name__});print(name,'unavailable',type(e).__name__)
 failed={x['name'] for x in status if not x['ok']}
 if failed and OUT.exists():
  try:
   for a in json.loads(OUT.read_text(encoding='utf-8')).get('opportunities',[]):
    src=a.get('sourceConnector') or (a.get('source') if a.get('source') in ('European Tech Opportunities','Opportunity Desk','ResearchRadar.at','ScholarshipHunter') else ('Grants.gov' if a.get('source')=='Grants.gov' else None))
    if src in failed:a['stale']=True;rows.append(a)
  except Exception:pass
 unique={}
 for a in rows:
  if a['id'] not in unique or unique[a['id']].get('stale') and not a.get('stale'):unique[a['id']]=a
 if not any(x['ok'] for x in status):raise SystemExit('All sources failed; catalog not replaced.')
 data={'updatedAt':now,'listingCount':len(unique),'sources':status,'opportunities':sorted(unique.values(),key=lambda a:(a.get('sourceUpdatedAt') or '',a['title']),reverse=True)}
 OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Wrote',len(unique),'listings from',sum(x['ok'] for x in status),'/',len(status),'feeds')
if __name__=='__main__':main()
