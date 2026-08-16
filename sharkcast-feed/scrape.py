import json, os, re, hashlib
from datetime import datetime, timezone
from urllib.request import Request, urlopen

OUT = os.path.join(os.path.dirname(__file__), 'latest.json')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36'

STATIONS = {
'kingscliff':(-28.257,153.578),'clarkes':(-28.640,153.613),'lennox':(-28.800,153.599),'sharpes':(-28.841,153.604),'ballina':(-28.874,153.593),'evans head':(-29.118,153.438),'yamba':(-29.435,153.365),'coffs harbour':(-30.288,153.139),'mylestom':(-30.365,153.104),'nambucca':(-30.646,153.010),'south west rocks':(-30.885,153.042),'crescent head':(-31.191,152.978),'port macquarie':(-31.466,152.930),'old bar':(-31.970,152.590),'forster':(-32.180,152.513),'bennetts':(-32.665,152.178),'hawks nest':(-32.665,152.178),'birubi':(-32.778,152.085),'newcastle':(-32.929,151.790),'redhead':(-33.015,151.714),'soldiers':(-33.296,151.570),'avoca':(-33.468,151.438),'killcare':(-33.529,151.371),'palm beach':(-33.601,151.326),'north narrabeen':(-33.711,151.302),'north steyne':(-33.792,151.289),'manly':(-33.797,151.288),'queenscliff':(-33.782,151.286),'bondi':(-33.891,151.277),'maroubra':(-33.949,151.255),'cronulla':(-34.058,151.154),'stanwell park':(-34.226,150.986),'wollongong':(-34.420,150.902),'shellharbour':(-34.583,150.870),'kiama':(-34.672,150.859),'cudmirrah':(-35.157,150.599),'mollymook':(-35.340,150.475),'malua bay':(-35.793,150.229),'merimbula':(-36.889,149.915)
}

MONTHS={m.lower():i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}

def fetch(url):
    req=Request(url,headers={'User-Agent':UA,'Accept':'text/html,application/xhtml+xml'})
    with urlopen(req,timeout=30) as r:
        return r.status, r.read().decode('utf-8','replace')

def strip_html(s):
    s=re.sub(r'<script[\s\S]*?</script>',' ',s,flags=re.I)
    s=re.sub(r'<style[\s\S]*?</style>',' ',s,flags=re.I)
    s=re.sub(r'<[^>]+>',' ',s)
    s=s.replace('&amp;','&').replace('&quot;','"').replace('&#39;',"'").replace('&nbsp;',' ')
    return re.sub(r'\s+',' ',s).strip()

def parse_time(text):
    # acoustic: 09:48:29 AM (AEST) on 31-July-2026
    m=re.search(r'(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)\s*\((AEST|AEDT)\)\s*on\s*(\d{1,2})-([A-Za-z]+)-(20\d{2})',text,re.I)
    if m:
        h,mi,se=int(m.group(1)),int(m.group(2)),int(m.group(3)); ap=m.group(4).upper()
        if ap=='PM' and h!=12:h+=12
        if ap=='AM' and h==12:h=0
        month=MONTHS.get(m.group(7).lower()); offset=10 if m.group(5).upper()=='AEST' else 11
        if month:
            from datetime import timedelta
            local=datetime(int(m.group(8)),month,int(m.group(6)),h,mi,se,tzinfo=timezone(timedelta(hours=offset)))
            return local.astimezone(timezone.utc).isoformat().replace('+00:00','Z')
    # drone: at 03:29 pm, 23 Feb 2026
    m=re.search(r'at\s*(\d{1,2}):(\d{2})\s*(am|pm),\s*(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})',text,re.I)
    if m:
        h,mi=int(m.group(1)),int(m.group(2)); ap=m.group(3).lower()
        if ap=='pm' and h!=12:h+=12
        if ap=='am' and h==12:h=0
        month=MONTHS.get(m.group(5).lower())
        if month:
            from datetime import timedelta
            local=datetime(int(m.group(6)),month,int(m.group(4)),h,mi,tzinfo=timezone(timedelta(hours=11)))
            return local.astimezone(timezone.utc).isoformat().replace('+00:00','Z')
    return None

def match_coord(text):
    low=text.lower()
    # Prefer explicit receiver station
    m=re.search(r'detected by\s+(.+?)\s+receiver',low,re.I)
    if m:
        name=m.group(1).strip()
        for k,v in sorted(STATIONS.items(),key=lambda kv:-len(kv[0])):
            if k in name:return k,v
    for k,v in sorted(STATIONS.items(),key=lambda kv:-len(kv[0])):
        if k in low:return k,v
    return None,(None,None)

def parse(html):
    plain=strip_html(html)
    patterns=[
      r'DPI Fisheries advise:\s*tagged\s+(?:White|Bull|Tiger)\s+Shark\s+#?\d+[\s\S]{0,650}?Tagged and released[\s\S]{0,260}?\.',
      r'SLSNSW advise[\s\S]{0,520}?(?:Beach Closed\.|Beach Reopened\.|has been reopened[^.]*\.|Please be #SharkSmart\.)',
      r'SLSNSW advise[^.]{0,360}?(?:By Drone|By Lifeguard)[^.]{0,220}?\d{1,2}\s+[A-Za-z]+\s+20\d{2}\.',
      r'DPI advise\s+\d+(?:\.\d+)?m\s+(?:White|Bull|Tiger)\s+Shark\s+tagged and released from SMART drumline[\s\S]{0,300}?\.'
    ]
    texts=[]
    for p in patterns:
        for m in re.finditer(p,plain,re.I):
            t=re.sub(r'\s+',' ',m.group(0)).strip()
            if t not in texts:texts.append(t)
    events=[]
    for text in texts:
        when=parse_time(text)
        if not when: continue
        station,(lat,lon)=match_coord(text)
        species=(re.search(r'(White|Bull|Tiger)\s+Shark',text,re.I) or [None,'Unknown'])[1].title()+' Shark'
        tag=(re.search(r'Shark\s+#?(\d+)',text,re.I) or [None,None])[1]
        category='acoustic'
        if re.search(r'By Drone',text,re.I):category='drone'
        elif re.search(r'By Lifeguard',text,re.I):category='sighting'
        elif re.search(r'SMART drumline',text,re.I):category='drumline'
        eid=hashlib.sha1(text.encode()).hexdigest()[:20]
        events.append({'id':eid,'event_time':when,'category':category,'species':species,'tag_id':tag,'station':station,'lat':lat,'lon':lon,'text':text,'source':'NSW SharkSmart public alert mirror','source_url':'https://x.com/NSWSharkSmart'})
    events.sort(key=lambda x:x['event_time'],reverse=True)
    return events

def main():
    old={}
    try:
        with open(OUT,'r',encoding='utf-8') as f:old=json.load(f)
    except Exception:pass
    checked=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    errors=[]; events=[]; status=None
    for url in ['https://twstalker.com/NSWSharkSmart','https://www.twstalker.com/NSWSharkSmart']:
        try:
            status,html=fetch(url)
            events=parse(html)
            if events:break
            errors.append(f'{url}: HTTP {status}, parsed 0 events')
        except Exception as e:errors.append(f'{url}: {type(e).__name__}: {e}')
    if not events and old.get('events'):
        events=old['events']
    out={'checked_at':checked,'ok':bool(events),'source_http':status,'events':events[:120],'event_count':len(events),'latest_event_time':events[0]['event_time'] if events else None,'errors':errors,'relay_version':'1.0'}
    with open(OUT,'w',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps({'ok':out['ok'],'event_count':out['event_count'],'latest_event_time':out['latest_event_time'],'errors':errors},indent=2))

if __name__=='__main__':main()
