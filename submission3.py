# KAGGRICULTURE V8 - submission-ready heuristic agent
# Stdlib only. Built against the advanced Kaggriculture observation/action schema.
from collections import deque, defaultdict

N=10; DAY=24; TOTAL=720; MAX_ORDERS=10; SHED_CAP=100
TARGET_HANDS=11; TARGET_COWS=8; TARGET_SHEEP=6
SEED_COST={'WHEAT':10,'CARROT':15,'TOMATO':20,'STRAWBERRY':30,'MELON':50}
ANIMAL_COST={'GOOSE':300,'COW':500,'SHEEP':400}
BASE={'WHEAT':25,'CARROT':35,'TOMATO':60,'STRAWBERRY':120,'MELON':250,'EGG':50,'MILK':160,'WOOL':200,'FERTILIZER':100}
FIRST={'WHEAT':2,'CARROT':3,'TOMATO':3,'STRAWBERRY':2,'MELON':4}
MAXDAY={'WHEAT':4,'CARROT':6,'TOMATO':-1,'STRAWBERRY':-1,'MELON':7}
ONGOING={'TOMATO','STRAWBERRY'}
LAND_ORDER=['NE','SW','SE']; LAND_PRICE={'NE':1000,'SW':2000,'SE':4000}
STATE={'episode':None,'step':-1,'jobs':{},'roles':{}}


def tile(f,x,y):
    try:return f['tiles'][y][x]
    except:return None

def pos(x):
    return tuple(x) if isinstance(x,(list,tuple)) and len(x)>=2 else (4,4)

def dist(a,b):return abs(a[0]-b[0])+abs(a[1]-b[1])

def shed_adj(p): return p in ((4,4),(5,4),(4,5),(5,5))

def step_to(f,a,b):
    # Locked tiles are passable; only board edges matter for movement.
    x,y=a; gx,gy=b
    if (x,y)==(gx,gy): return ['PASS']
    dx=gx-x; dy=gy-y
    opts=[]
    if dx: opts.append(('EAST' if dx>0 else 'WEST',(x+(1 if dx>0 else -1),y)))
    if dy: opts.append(('SOUTH' if dy>0 else 'NORTH',(x,y+(1 if dy>0 else -1))))
    for op,p in opts:
        if 0<=p[0]<N and 0<=p[1]<N:return [op]
    return ['PASS']

def unlocked(f,p):
    t=tile(f,*p)
    return t!='LOCKED' and not (isinstance(t,dict) and t.get('locked',False))

def shed(f):
    # Shed is private; this function is replaced with private shed at call sites.
    return {}

def structures(f):
    out=[]
    for y,row in enumerate(f.get('tiles',[]) or []):
        for x,t in enumerate(row):
            if isinstance(t,dict) and t.get('kind') in ('COOP','PASTURE'):
                out.append((x,y,t))
    return out

def animals(f):
    c=defaultdict(int)
    for _,_,t in structures(f):
        a=t.get('animal')
        if a:c[a]+=1
    return c

def empty_tiles(f):
    return [(x,y) for y in range(N) for x in range(N)
            if not shed_adj((x,y)) and unlocked(f,(x,y)) and tile(f,x,y) is None]

def invs(private): return private.get('inventories',[]) or []
def inv(private,i):
    a=invs(private)
    return a[i] if i<len(a) and isinstance(a[i],dict) else {}
def iq(private,i,item): return int(inv(private,i).get(item,0) or 0)

def reset(obs):
    ep=obs.get('episodeId',obs.get('episode_id'))
    st=int(obs.get('step',0))
    if st==0 or st<STATE['step'] or ep!=STATE['episode']:
        STATE['jobs']={}; STATE['roles']={}; STATE['episode']=ep
    STATE['step']=st

def crop_counts(f):
    c=defaultdict(int)
    for row in f.get('tiles',[]) or []:
        for t in row:
            if isinstance(t,dict) and t.get('kind')=='PLANT':c[t.get('crop')]+=1
    return c

def market_price(obs,item): return float((obs.get('market',{}).get('prices',{}) or {}).get(item,BASE.get(item,0)))

def town_bonus(obs,item):
    s=' '.join((obs.get('town',{}) or {}).get('unlocked_shops',[]) or []).upper()
    keys={'WHEAT':('BAKERY',),'MILK':('DAIRY','BAKERY'),'EGG':('BAKERY',),'STRAWBERRY':('BAKERY',),'WOOL':('TEXTILE','')}
    return sum(k in s for k in keys.get(item,()))

def opponent_count(obs,item):
    fs=obs.get('farms',[]); me=int(obs.get('player',0))
    if len(fs)<2:return 0
    f=fs[1-me]; n=0
    for row in f.get('tiles',[]) or []:
        for t in row:
            if isinstance(t,dict) and t.get('kind')=='PLANT' and t.get('crop')==item:n+=1
            if isinstance(t,dict) and t.get('animal')==item:n+=1
    return n

def sellable(private):
    return {k:int(v) for k,v in (private.get('shed',{}) or {}).items() if isinstance(v,(int,float)) and v>0 and k not in SEED_COST}

def market_orders(obs,f,pv):
    day=int(obs.get('day',0)); step=int(obs.get('step',0)); money=float(f.get('money',0)); orders=[]
    sh=sellable(pv); terminal=step>=672
    # Meter premium sales. Dump hard only in liquidation.
    ranked=[]
    for item,q in sh.items():
        p=market_price(obs,item); b=BASE.get(item,p)
        score=p/b + .08*town_bonus(obs,item) - .01*opponent_count(obs,item)
        if item=='FERTILIZER':score-=.4
        ranked.append((score,item,q,p,b))
    for _,item,q,p,b in sorted(ranked,reverse=True):
        if len(orders)>=MAX_ORDERS:break
        if terminal:n=min(q,12)
        elif item=='WHEAT':n=min(q,10)
        elif item in ('MILK','WOOL','EGG','STRAWBERRY'):n=min(q,3 if p<b*1.05 else 4)
        elif item=='MELON':n=min(q,2) if p>=300 else 0
        elif item=='FERTILIZER':n=min(q,2) if p>=140 else 0
        else:n=min(q,4) if p>=b*.85 else 0
        if n:orders.append(['SELL',item,n])
    if terminal:return orders[:MAX_ORDERS]
    # Rehire each day. Hands disappear at end of day.
    hands=len(f.get('hands',[]) or [])
    if hands<TARGET_HANDS and money>500:
        for _ in range(min(TARGET_HANDS-hands,MAX_ORDERS-len(orders))):orders.append(['HIRE',1])
    # Expand to NE when there is enough working capital; SW only after strong cash.
    quads=f.get('unlocked_quadrants',['NW']) or ['NW']
    if 'NE' not in quads and money>1700 and day>=2 and len(orders)<MAX_ORDERS:
        orders.append(['BUY_LAND','NE'])
    elif 'SW' not in quads and money>3300 and day>=9 and len(orders)<MAX_ORDERS:
        orders.append(['BUY_LAND','SW'])
    # Build herd, but never consume the cash needed for the next land/operation cycle.
    ac=animals(f); cows=ac['COW']; sheep=ac['SHEEP']
    if day<=16 and money>700:
        for a,target in (('COW',TARGET_COWS),('SHEEP',TARGET_SHEEP)):
            need=target-ac[a]
            if need<=0 or len(orders)>=MAX_ORDERS:continue
            reserve=350 if 'NE' in quads else 500
            affordable=max(0,int((money-reserve)//ANIMAL_COST[a]))
            n=min(need,affordable,3)
            if n:orders.append(['BUY_ANIMAL',a,n])
    # Seeds: default 10 wheat / 16 strawberry, but only buy as space and cash justify it.
    cc=crop_counts(f); seeds=pv.get('seeds',{}) or {}
    for crop,target in (('WHEAT',10),('STRAWBERRY',16)):
        if len(orders)>=MAX_ORDERS:break
        d=max(0,target-cc[crop]-int(seeds.get(crop,0) or 0))
        affordable=max(0,int((money-250)//SEED_COST[crop]))
        n=min(d,affordable,8)
        if n:orders.append(['BUY_SEED',crop,n])
    return orders[:MAX_ORDERS]

def role_map(f):
    # Keep a compact livestock block near the shed, then wheat, then strawberry.
    key=(tuple(f.get('unlocked_quadrants',[]) or []),)
    if STATE['roles'].get('key')==key:return STATE['roles']
    cells=empty_tiles(f)
    # Include currently occupied cells as role anchors so planting doesn't move around.
    usable=[]
    for y in range(N):
        for x in range(N):
            p=(x,y)
            if shed_adj(p) or not unlocked(f,p):continue
            usable.append(p)
    usable.sort(key=lambda p:(dist(p,(4,4)),p[1],p[0]))
    animal_slots=usable[:14]
    rest=usable[14:]
    rest.sort(key=lambda p:(p[1],p[0]))
    roles={'key':key,'animals':animal_slots,'wheat':rest[:10],'straw':rest[10:26]}
    STATE['roles']=roles
    return roles

def job_valid(f,j):
    if not j:return False
    p=j.get('p'); k=j.get('k')
    if p is None:return False
    t=tile(f,*p)
    if k in ('WATER','HARVEST','FERTILIZE'):return isinstance(t,dict) and t.get('kind')=='PLANT'
    if k=='PLANT':return t is None and unlocked(f,p)
    if k=='BUILD':return t is None and unlocked(f,p)
    if k in ('FEED','CARE','COLLECT','PLACE'):return isinstance(t,dict) and t.get('kind') in ('PASTURE','COOP')
    if k=='WEED':return isinstance(t,dict) and t.get('kind')=='WEED'
    return True

def make_jobs(obs,f,pv):
    day=int(obs.get('day',0)); step=int(obs.get('step',0)); terminal=step>=672
    roles=role_map(f); jobs=[]
    # Critical plant work.
    for y,row in enumerate(f.get('tiles',[]) or []):
        for x,t in enumerate(row):
            if not isinstance(t,dict):continue
            if t.get('kind')=='WEED':jobs.append({'k':'WEED','p':(x,y),'v':130})
            if t.get('kind')!='PLANT':continue
            c=t.get('crop'); age=day-int(t.get('planted_day',day)); watered=t.get('watered_today',False)
            if not watered:
                urgent=90 if c in ONGOING else (70 if age>=FIRST.get(c,2)-1 else 25)
                if terminal:urgent=100
                jobs.append({'k':'WATER','p':(x,y),'v':urgent})
            held=int(t.get('yield_units',0) or 0)
            if c in ONGOING:
                if held>=3 or terminal:jobs.append({'k':'HARVEST','p':(x,y),'v':120+10*held})
                elif c=='STRAWBERRY' and not terminal and int((t.get('fertilized_until_day',-1) or -1))<day and (pv.get('shed',{}) or {}).get('FERTILIZER',0)>0:
                    jobs.append({'k':'FERTILIZE','p':(x,y),'v':75})
            elif age>=FIRST.get(c,2):
                # Harvest near max yield; terminal forces liquidation.
                if terminal or age>=MAXDAY.get(c,age):jobs.append({'k':'HARVEST','p':(x,y),'v':115})
    ac=animals(f); held_animals=ac['COW']+ac['SHEEP']+ac['GOOSE']
    target=min(14,held_animals+sum(int((pv.get('shed',{}) or {}).get(a,0)) for a in ('COW','SHEEP')))
    # Build pasture slots before planting them.
    built=sum(1 for _,_,t in structures(f))
    for p in roles['animals'][:max(4,target)]:
        t=tile(f,*p)
        if t is None and built<max(4,target):
            jobs.append({'k':'BUILD','p':p,'v':100});built+=1
    # Place purchased animals on empty matching structures.
    shedv=pv.get('shed',{}) or {}
    for x,y,t in structures(f):
        if t.get('animal') is None:
            if shedv.get('COW',0)>0:jobs.append({'k':'PLACE','p':(x,y),'v':110,'need':'COW'})
            elif shedv.get('SHEEP',0)>0:jobs.append({'k':'PLACE','p':(x,y),'v':108,'need':'SHEEP'})
    # Crop planting zones.
    seeds=pv.get('seeds',{}) or {}
    cc=crop_counts(f)
    for p in roles['wheat']:
        if tile(f,*p) is None and seeds.get('WHEAT',0)>0:jobs.append({'k':'PLANT','p':p,'v':60,'crop':'WHEAT'})
    for p in roles['straw']:
        if tile(f,*p) is None and seeds.get('STRAWBERRY',0)>0:jobs.append({'k':'PLANT','p':p,'v':68,'crop':'STRAWBERRY'})
    # Animals: feed is absolute priority; care next; collect fertilizer daily.
    for x,y,t in structures(f):
        a=t.get('animal')
        if not a:continue
        if not t.get('fed_today',False):jobs.append({'k':'FEED','p':(x,y),'v':180,'need':'WHEAT'})
        elif not terminal and not t.get('cared_today',False):jobs.append({'k':'CARE','p':(x,y),'v':110 if a=='COW' else 95})
        if t.get('fertilizer_available',False):jobs.append({'k':'COLLECT','p':(x,y),'v':55})
        if int(t.get('yield_units',0) or 0)>=3 or terminal:jobs.append({'k':'HARVEST','p':(x,y),'v':105})
    jobs.sort(key=lambda j:j['v'],reverse=True)
    return jobs

def nearest_job(unit_p,jobs,used,pv,uid):
    best=None
    for i,j in enumerate(jobs):
        if i in used or not job_valid(CURRENT_FARM,j):continue
        need=j.get('need')
        # If need is present in inventory, prefer it; otherwise logistics is allowed.
        d=dist(unit_p,j['p']); s=j['v']-2.2*d
        if need and iq(pv,uid,need)>0:s+=35
        if j['k']=='FEED':s+=50
        if j['k']=='HARVEST':s+=20
        if best is None or s>best[0]:best=(s,i,j)
    return (best[1],best[2]) if best else (None,None)

def unit_action(obs,f,pv,uid,p,job,jobs,used):
    global CURRENT_FARM
    CURRENT_FARM=f
    ip=inv(pv,uid); shed_item=pv.get('shed',{}) or {}
    # Persist a job for the current day, but discard it if the target is no longer valid.
    old=STATE['jobs'].get(uid)
    if old and job_valid(f,old):job=old
    else:
        _,job=nearest_job(p,jobs,used,pv,uid)
        if job:STATE['jobs'][uid]=job
    if not job:
        # Carrying goods: get them to shed before taking another task.
        if any(isinstance(v,(int,float)) and v>0 for v in ip.values()):
            if shed_adj(p):
                item=max(ip,key=lambda k:ip.get(k,0))
                return ['DROP',item,int(ip[item])]
            return step_to(f,p,(4 if p[0]<5 else 5,4 if p[1]<5 else 5))
        return ['PASS']
    need=job.get('need')
    if need and iq(pv,uid,need)<=0:
        if shed_item.get(need,0)>0:
            if shed_adj(p):return ['PICKUP',need, min(4 if need=='WHEAT' else 1,int(shed_item[need]))]
            return step_to(f,p,(4 if p[0]<5 else 5,4 if p[1]<5 else 5))
        # No stock: release job so another job can be selected.
        STATE['jobs'].pop(uid,None);return ['PASS']
    target=job['p']
    if p!=target:return step_to(f,p,target)
    k=job['k']
    if k=='WATER':return ['WATER']
    if k=='HARVEST':return ['HARVEST']
    if k=='FERTILIZE':return ['FERTILIZE']
    if k=='PLANT':return ['PLANT',job['crop']]
    if k=='BUILD':return ['BUILD_PASTURE']
    if k=='FEED':return ['FEED']
    if k=='CARE':return ['CARE']
    if k=='COLLECT':return ['COLLECT_FERTILIZER']
    if k=='WEED':return ['DIG']
    if k=='PLACE':return ['PLACE',need,1]
    return ['PASS']

def agent(obs,config=None):
    global CURRENT_FARM
    try:
        reset(obs)
        player=int(obs.get('player',0)); farms=obs.get('farms',[]) or []
        if player>=len(farms):return {'farmer':['PASS'],'hands':[],'market':[]}
        f=farms[player]; pv=obs.get('private',{}) or {}
        orders=market_orders(obs,f,pv)
        jobs=make_jobs(obs,f,pv)
        hands=f.get('hands',[]) or []
        positions=[pos(f.get('farmer',[4,4]))]+[pos(x) for x in hands]
        actions=[]; used=set()
        for uid,p in enumerate(positions):
            actions.append(unit_action(obs,f,pv,uid,p,None,jobs,used))
        return {'farmer':actions[0],'hands':actions[1:],'market':orders[:MAX_ORDERS]}
    except Exception:
        f=(obs.get('farms',[]) or [{}])[int(obs.get('player',0))]
        return {'farmer':['PASS'],'hands':[['PASS'] for _ in (f.get('hands',[]) or [])],'market':[]}
