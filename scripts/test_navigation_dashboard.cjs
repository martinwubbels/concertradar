// Focused navigation and dashboard, independent of browser, network and user data.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync('index.html','utf8');
const src=html.split('<script>')[1].split('</script>')[0];

const first=src.indexOf('/* Five daily destinations, with all advanced functions still reachable. */');
const last=src.indexOf('function render(){',first);
assert(first>0&&last>first,'Navigation functions present');
const state={tab:'dashboard'};
const nav=new Function('state','const h=x=>String(x);'+src.slice(first,last)+'return {navigationMarkup,NAV_PRIMARY,NAV_MORE};')(state);
assert.equal(nav.NAV_PRIMARY.length,5,'Five visible daily tabs');
const keys=[...nav.NAV_PRIMARY,...nav.NAV_MORE.flatMap(x=>x[1])].map(x=>x[0]);
assert.equal(new Set(keys).size,keys.length,'No duplicate tabs');
for(const key of ['new','shortlist','favorites','booked','inbox','rejected','taste','sync','updates','map','calendar','history','travel','add']){
 assert(keys.includes(key),'Existing page still reachable: '+key);
}
let markup=nav.navigationMarkup();
assert.equal((markup.match(/<button[^>]*data-tab=/g)||[]).length,keys.length);
assert.equal((markup.match(/class="nav-more"/g)||[]).length,1);
assert(markup.includes('aria-current="page"'));
assert(markup.includes('>Meer</summary>'));
state.tab='sync';
markup=nav.navigationMarkup();
assert(markup.includes('data-secondary-active="true"'),'Advanced page highlighted');
assert(markup.includes('data-tab="sync" class="active"'),'Selected secondary page preserved');
assert(html.includes('.nav{display:grid!important'),'Mobile navigation is visible');
assert(!src.includes('<select id="mobileTab" aria-label="Kies overzicht" class="mobile-navigation">'),
 'No second overwhelming mobile tab list');

const begin=src.indexOf('/* Compact daily dashboard. Existing calendar, notifications, and full lists remain available. */');
const stop=src.indexOf('function bindNewDashboard(){',begin);
assert(begin>0&&stop>begin,'Focused dashboard helpers exist');
const ctx={events:[
 {id:'booked',name:'Booked concert',venue:'Podium A',city:'Emmen',date:'2027-01-03',status:'booked'},
 {id:'short',name:'Saved festival',venue:'Podium B',city:'Zwolle',date:'2027-02-11',status:'shortlisted'},
 {id:'past',name:'Old concert',venue:'Podium C',date:'2026-01-01',status:'booked'},
],alerts:[{e:{name:'Booked concert',date:'2027-01-03'},reason:'Agenda-overlap'}],notices:[]};
const pre=[
 'const today="2026-11-27";',
 'const all=()=>ctx.events;',
 'const statusOf=e=>e.status||"";',
 'const isBooked=e=>statusOf(e)==="booked";',
 'const h=x=>String(x??"").replace(/&/g,"&amp;").replace(/</g,"&lt;");',
 'const dt=x=>x;',
 'const dashboardSuggestionEntries=()=>[{kind:"catalog",event:{id:"tip",name:"Roots act",date:"2027-03-03",venue:"Testpodium",genre:"Americana",match:"Folk"}}];',
 'const hasDirectConcertLink=e=>true;',
 'const tasteResult=e=>({score:8.7});',
 'const scoreDetails=e=>"<details>Waarom deze score?</details>";',
 'const sourceLabel=e=>"Niet recent gecontroleerd";',
 'const concertLink=e=>"https://example.org/concert";',
 'const agendaConflicts=()=>ctx.alerts;',
 'const busyDates=["2027-01-03"];',
 'const calendarCheckMarkup=()=>"<div id=busyDate>Agenda beheren</div>";',
 'const newDashboardMarkup=()=>"<section>Nieuwe vondsten</section>";',
 'const noticeCandidates=()=>ctx.notices;',
 'const noticeMarkup=()=>"<div>Meldingen</div>";'
].join('\n');
const fn=new Function('ctx',pre+'\n'+src.slice(begin,stop)+
 '\nreturn {dashboardUpcomingMarkup,dashboardTopMatchesMarkup,dashboardConflictMarkup,personalDashboardTop};')(ctx);
const dashboard=fn.personalDashboardTop();
assert(dashboard.includes('Mijn volgende concerten'),'Upcoming block');
assert(dashboard.includes('Booked concert')&&dashboard.includes('Saved festival'),'Booked and shortlist both present');
assert(!dashboard.includes('Old concert'),'Past concert excluded');
assert(dashboard.includes('Nieuwe vondsten'),'Discovery block');
assert(dashboard.includes('Topmatches voor jou'),'Match block');
assert(dashboard.includes('Agenda en conflicten'),'Conflict block');
assert(dashboard.includes('Agenda-overlap'),'Conflict reason visible');
assert(dashboard.includes('data-tab="calendar"'),'Calendar link');
assert(dashboard.includes('Bezette datums en agenda-import beheren'),'Old agenda management stays accessible');
assert(dashboard.includes('data-action="shortlisted"'),'Shortlist button on recommendation');
assert(dashboard.includes('data-tab="surprise"'),'More recommendations accessible');
assert(dashboard.includes('Hoogste huidige match'),'Best score highlighted');
assert(dashboard.includes('Waarom deze score?'),'Score explanation present');
assert(dashboard.includes('Nieuwe signalen (0)'),'Alerts remain in expandable panel');
assert(src.includes('function dashboardMarkup(){return personalDashboardTop();}'),'No giant duplicate bookings list');
assert(src.includes("state.tab==='new'?searchNowMarkup():''"),'Scanning tools reachable on discovery page');
assert(src.includes('state.tab===\'shortlist\'?shortlistMarkup()'),'Shortlist page preserved');
console.log('Focused navigation and dashboard tests passed');