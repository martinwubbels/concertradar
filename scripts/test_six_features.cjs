// Offline checks of the six dashboard additions. No network or real user data.
const fs=require('fs');
const assert=require('assert').strict;
const src=fs.readFileSync('index.html','utf8').split('<script>')[1].split('</script>')[0];
const first=src.indexOf('/* ConcertRadar 2026: source-aware');
const last=src.indexOf('function dashboardMarkup(){',first);
assert(first>0&&last>first,'six-feature block exists');
const context={
 appSettings:{travelLimits:{regular:85,special:190,enabled:true}},
 events:[],
 snapshots:[],
 storage:{getItem:()=>null,setItem:()=>{}}
};
const before=[
 'const localStorage=ctx.storage;',
 'let appSettings=ctx.appSettings;',
 'const today="2026-11-19";',
 'const venueLocations={origin:{lat:52.7254,lng:6.9852},venues:{}};',
 'const tasteNorm=s=>String(s||"").toLowerCase();',
 'const tasteGenres=e=>String(e.genre||"").split("/");',
 'const tasteWords=()=>[];',
 'const isBooked=e=>e.status==="booked";',
 'const statusOf=e=>e.status||"";',
 'const hasDirectConcertLink=e=>Boolean(e.url);',
 'const tasteResult=e=>({score:e.score??8});',
 'const tasteManualEffect=e=>({matched:[]});',
 'const all=()=>ctx.events;',
 'const venuePoint=e=>e.point;',
 'const dt=s=>s;',
 'const concertLink=e=>e.url||"";',
 'const concertLinkLabel=e=>"Concertlink";',
 'const h=x=>String(x??"").replace(/</g,"&lt;");',
 'const persist=()=>ctx.snapshots.push(JSON.parse(JSON.stringify(appSettings)));',
 'const render=()=>{};',
 'const assessments={};',
 'const listeningVerdict=e=>null;'
].join('\n');
const make=new Function('ctx',before+'\n'+src.slice(first,last)+'\nreturn {parseCalendarDates,travelInfo,travelSettings,agendaConflicts,saveBusyDates,notifySettings,noticeCandidates,artistProfile,sourceLabel,sourceNeedsAttention};');
const a=make(context);
assert.equal(a.travelSettings().regular,85);
const nearby={id:'a',name:'A',date:'2026-12-03',point:{lat:52.7254,lng:6.9852},score:8,status:'booked'};
const distant={id:'b',name:'B',date:'2026-12-03',point:{lat:53.9,lng:8.1},score:8,status:'booked'};
context.events=[nearby,distant];
assert.equal(a.travelInfo(nearby).km,0);
assert.equal(a.travelInfo(nearby).within,true);
assert.equal(a.travelInfo(distant).within,false);
assert.equal(a.travelInfo({id:'c',score:8}).km,null);
const dates=a.parseCalendarDates('BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nDTSTART;VALUE=DATE:20261203\r\nSUMMARY:Private\r\nEND:VEVENT\r\nEND:VCALENDAR');
assert.deepEqual(dates,['2026-12-03']);
a.saveBusyDates(dates);
assert.equal(a.agendaConflicts().length,2,'Same-day bookings and imported calendar dates conflict');
assert.equal(a.notifySettings().initialized,false);
assert.deepEqual(a.noticeCandidates(),[],'No notifications before baseline');
const profile=a.artistProfile({...nearby,name:'A',genre:'Americana',reason:'Unique roots show'});
assert.equal(profile.name,'A');
assert.equal(a.sourceLabel(nearby),'Niet opnieuw gecontroleerd');
console.log('Six-feature offline checks passed');
