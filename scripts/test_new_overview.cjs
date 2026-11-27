// Deterministic offline checks for the combined concerts/festivals overview.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync('index.html','utf8');
const script=html.split('<script>')[1].split('</script>')[0];
const first=script.indexOf('function isFestivalEvent(e){');
const last=script.indexOf('function ratingOf(e)',first);
assert(first>0&&last>first,'Overview helpers found');
const ctx={
 catalog:[],discovery:[],status:{},
 seed:[],nationalSeed:[],liveEvents:[],
 state:{newOrder:'found',newKind:'all',newDecision:'all'},
 updated:'2026-11-27T09:00:00Z'
};
const prefix=[
 'const today="2026-11-27";',
 'const seed=ctx.seed,nationalSeed=ctx.nationalSeed,liveEvents=ctx.liveEvents;',
 'const discoveryEvents=ctx.discovery,discoveriesUpdated=ctx.updated;',
 'const state=ctx.state,all=()=>ctx.catalog;',
 'const statusOf=e=>ctx.status[e.id]||"";',
 'const suggestionIdentity=e=>String(e.name||"").toLowerCase().replace(/[^a-z0-9]/g,"")+"|"+e.date;',
 'const h=x=>String(x??"").replace(/&/g,"&amp;").replace(/</g,"&lt;");',
 'const dt=x=>x;',
 'const tasteResult=e=>({score:8.1});',
 'const euro=x=>"€ "+x;',
 'const hasDirectConcertLink=e=>Boolean(e.url);',
 'const concertLink=e=>e.url||"https://example.org/search";'
].join('\n');
const fn=new Function('ctx',prefix+'\n'+script.slice(first,last)+'\nreturn {isFestivalEvent,newOverviewData,newDashboardMarkup,newMarkup,newEntryMarkup,shortlistMarkup};')(ctx);
const e=(id,name,date,opts={})=>({id,name,date,venue:'Testpodium',city:'Groningen',genre:'Americana',url:'https://example.org/event/'+id,...opts});
ctx.liveEvents.push(e('f','TakeRoot 2027','2027-11-06',{verification:'historical_unverified'}));
ctx.catalog.push(...ctx.liveEvents,e('a','New Americana Show','2027-01-03',{verification:'auto_verified_schema',source_checked_at:'2026-11-27T08:00:00Z'}));
ctx.discovery.push(
 e('d','Fresh Country Act','2027-04-04',{first_seen_at:'2026-11-27T10:00:00Z'}),
 e('z','New Bluegrass Festival','2027-06-05',{event_kind:'festival',first_seen_at:'2026-11-27T11:00:00Z'}),
 e('dup','TakeRoot 2027','2027-11-06',{event_kind:'festival'}),
 e('past','Past Show','2026-11-20'),
 e('old','New Americana Show','2027-01-03')
);
const data=fn.newOverviewData();
assert.equal(data.concerts.length,2,'Catalog auto and new candidate, no duplicates/past');
assert.equal(data.festivals.length,2,'Future known and new festivals are visible');
assert.equal(data.festivals.filter(x=>x.event.name==='TakeRoot 2027').length,1,'No duplicate festival');
assert.equal(data.concerts[0].event.id,'d','Most recent found shown first');
const markup=fn.newMarkup();
assert(markup.includes('Nieuwe concertvondsten (2)'));
assert(markup.includes('Aankomende festivals (2)'));
assert(markup.includes('Kandidaat uit podiumagenda'));
assert(markup.includes('Bekend festival uit masterlijst'));
assert(markup.includes('data-action="shortlisted"'),'Shortlist button for concerts and festivals');
assert(markup.includes('data-action="interested"'));
assert(markup.includes('data-action="rejected"'));
assert(markup.includes('data-new-kind="festival"'));
assert(markup.includes('data-new-kind="concert"'));
assert(markup.includes('data-new-kind="all"'));
assert(markup.includes('tickets controleren'));
assert(fn.newDashboardMarkup().includes('data-tab="new"'));
assert(fn.newDashboardMarkup().includes('data-action="shortlisted"'),'Shortcut on start screen');
assert(fn.newDashboardMarkup().includes('data-action="rejected"'),'Reject from start screen');
ctx.state.newDecision='pending';
ctx.status.d='shortlisted';
assert(!fn.newMarkup().includes('Fresh Country Act'),'Shortlisted show hidden by pending filter');
assert(fn.shortlistMarkup().includes('Fresh Country Act'),'Shortlisted candidate appears in saved list');
assert(fn.shortlistMarkup().includes('Mijn shortlist (1)'),'Shortlist count');
ctx.status.d='interested';
assert(!fn.shortlistMarkup().includes('Fresh Country Act'),'Interested moves out of shortlist');
assert(!fn.newMarkup().includes('Fresh Country Act'),'Interested show hidden by pending filter');
ctx.state.newKind='festival';
assert(!fn.newMarkup().includes('Nieuwe concertvondsten ('),'Festival-only filter');
ctx.state.newOrder='event';
assert.equal(fn.newOverviewData().concerts[0].event.id,'a','Date sort works');
assert(script.includes("newDashboardMarkup()+dashboardShortlistMarkup()"),'Dashboard includes overview');
assert(script.includes("state.tab==='shortlist'?shortlistMarkup()"),'Shortlist tab is wired');
assert(html.includes('data-action="shortlisted"'),'Shortlist action available on event card');
assert(html.includes('Nieuw & festivals'),'Easy-to-find navigation');
console.log('New concerts and festivals shortlist overview tests passed');