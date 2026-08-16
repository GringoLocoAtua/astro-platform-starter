import json, os, re, hashlib, html as htmllib
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

OUT=os.path.join(os.path.dirname(__file__),'latest.json')
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36'
STATIONS={'kingscliff':(-28.257,153.578),'clarkes':(-28.640,153.613),'lennox':(-28.800,153.599),'sharpes':(-28.841,153.604),'ballina':(-28.874,153.593),'evans head':(-29.118,153.438),'yamba':(-29.435,153.365),'coffs harbour':(-30.288,153.139),'mylestom':(-30.365,153.104),'nambucca':(-30.646,153.010),'south west rocks':(-30.885,153.042),'crescent head':(-31.191,152.978),'port macquarie':(-31.466,152.930),'old bar':(-31.970,152.590),'forster':(-32.180,152.513),'bennetts':(-32.665,152.178),'hawks nest':(-32.665,152.178),'birubi':(-32.778,152.085),'newcastle':(-32.929,151.790),'redhead':(-33.015,151.714),'soldiers':(-33.296,151.570),'avoca':(-33.468,151.438),'killcare':(-33.529,151.371),'palm beach':(-33.601,151.326),'north narrabeen':(-33.711,151.302),'north steyne':(-33.792,151.289),'manly':(-33.797,151.288),'queenscliff':(-33.782,151.286),'bondi':(-33.891,151.277),'maroubra':(-33.949,151.255),'cronulla':(-34.058,151.154),'stanwell park':(-34.226,150.986),'wollongong':(-34.420,150.902),'shellharbour':(-34.583,150.870),'kiama':(-34.672,150.859),'cudmirrah':(-35.157,150.599),'mollymook':(-35.340,150.475),'malua bay':(-35.793,150.229),'merimbula':(-36.889,149.915)}
MONTHS={m.lower():i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}

def fetch(url,accept='text/html,*/*'):
    req=Request(url,headers={'User-Agent':UA,'Accept':accept})
    with urlopen(req,timeout=30) as r:return r.status,r.read().decode('utf-8','replace')

def clean(s):
    s=htmllib.unescape(s or '')
    s=re.sub(r'<[^>]+>',' ',s)
    return re.sub(r'\s+',' ',s).strip()

def parse_time(t):
    m=re.search(r'(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)\s*\((AEST|AEDT)\)\s*on\s*(\d{1,2})-([A-Za-z]+)-(20\d{2})',t,re.I)
    if m:
        hh,mi,se=int(m.group(1)),int(m.group(2)),int(m.group(3)); ap=m.group(4).upper(); off=10 if m.group(5).upper()=='AEST' else 11
        if ap=='PM' and hh!=12:hh+=12
        if ap=='AM' and hh==12:hh=0
        mon=MONTHS.get(m.group(7).lower())
        if mon:return datetime(int(m.group(8)),mon,int(m.group(6)),hh,mi,se,tzinfo=timezone(timedelta(hours=off))).astimezone(timezone.utc).isoformat().replace('+00:00','Z')
    m=re.search(r'at\s*(\d{1,2}):(\d{2})\s*(am|pm),\s*(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})',t,re.I)
    if m:
        hh,mi=int(m.group(1)),int(m.group(2)); ap=m.group(3).lower(); mon=MONTHS.get(m.group(5).lower())
        if ap=='pm' and hh!=12:hh+=12
        if ap=='am' and hh==12:hh=0
        if mon:return datetime(int(m.group(6)),mon,int(m.group(4)),hh,mi,tzinfo=timezone(timedelta(hours=10))).astimezone(timezone.utc).isoformat().replace('+00:00','Z')
    return None

def location(t):
    low=t.lower(); m=re.search(r'detected by\s+(.+?)\s+receiver',low,re.I); target=m.group(1).strip() if m else low
    for k,v in sorted(STATIONS.items(),key=lambda x:-len(x[0])):
        if k in target:return k,v[0],v[1]
    for k,v in sorted(STATIONS.items(),key=lambda x:-len(x[0])):
        if k in low:return k,v[0],v[1]
    return None,None,None

def event_from_text(text,url):
    text=clean(text)
    if not re.search(r'(tagged\s+(?:White|Bull|Tiger)\s+Shark|By Drone|By Lifeguard|SMART drumline)',text,re.I):return None
    when=parse_time(text)
    if not when:return None
    station,lat,lon=location(text)
    sm=re.search(r'(White|Bull|Tiger)\s+Shark',text,re.I); species=(sm.group(1).title()+' Shark') if sm else 'Unknown Shark'
    tm=re.search(r'Shark\s+#?(\d+)',text,re.I); tag=tm.group(1) if tm else None
    cat='acoustic'
    if re.search(r'By Drone',text,re.I):cat='drone'
    elif re.search(r'By Lifeguard',text,re.I):cat='sighting'
    elif re.search(r'SMART drumline',text,re.I):cat='drumline'
    return {'id':hashlib.sha1((text+url).encode()).hexdigest()[:20],'event_time':when,'category':cat,'species':species,'tag_id':tag,'station':station,'lat':lat,'lon':lon,'text':text,'source':'NSW SharkSmart public index','source_url':url}

def bing_rss():
    queries=['site:x.com/NSWSharkSmart/status "DPI Fisheries advise" tagged Shark','site:x.com/NSWSharkSmart/status "By Drone" shark','site:x.com/NSWSharkSmart/status "SMART drumline" shark','"SharkSmart @NSWSharkSmart" "DPI Fisheries advise"']
    found=[]; errors=[]
    for q in queries:
        url='https://www.bing.com/search?format=rss&count=50&q='+quote_plus(q)
        try:
            status,xml=fetch(url,'application/rss+xml,text/xml,*/*')
            root=ET.fromstring(xml)
            for item in root.findall('.//item'):
                title=clean(item.findtext('title')); desc=clean(item.findtext('description')); link=clean(item.findtext('link'))
                ev=event_from_text(title+' '+desc,link)
                if ev:found.append(ev)
        except Exception as e:errors.append('bing '+q+': '+type(e).__name__+': '+str(e))
    return found,errors

def twstalker():
    found=[]; errors=[]
    for url in ['https://twstalker.com/NSWSharkSmart','https://www.twstalker.com/NSWSharkSmart']:
        try:
            status,body=fetch(url)
            plain=clean(body)
            chunks=re.split(r'View Details|SharkSmart @NSWSharkSmart',plain,flags=re.I)
            for c in chunks:
                ev=event_from_text(c,'https://x.com/NSWSharkSmart')
                if ev:found.append(ev)
            if found:break
        except Exception as e:errors.append(url+': '+type(e).__name__+': '+str(e))
    return found,errors

def dedupe(events):
    d={}
    for e in events:
        key=(e.get('tag_id'),e.get('station'),e.get('event_time'),e.get('category'))
        d[key]=e
    return sorted(d.values(),key=lambda e:e['event_time'],reverse=True)

def main():
    try:
        old=json.load(open(OUT,encoding='utf-8'))
    except Exception:old={}
    events=[]; errors=[]
    a,er=bing_rss();events+=a;errors+=er
    b,er=twstalker();events+=b;errors+=er
    events=dedupe(events)
    if not events and old.get('events'):
        events=old['events'];errors.append('using last-good relay cache')
    out={'checked_at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'ok':bool(events),'events':events[:150],'event_count':len(events),'latest_event_time':events[0]['event_time'] if events else None,'errors':errors[-12:],'relay_version':'1.1'}
    json.dump(out,open(OUT,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print(json.dumps({'ok':out['ok'],'event_count':out['event_count'],'latest':out['latest_event_time'],'errors':out['errors']},indent=2))
if __name__=='__main__':main()
