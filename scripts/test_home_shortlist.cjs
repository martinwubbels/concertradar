// Dashboard shortlisting: deterministic offline tests, no account or network.
const assert=require('assert').strict,fs=require('fs');
const html=fs.readFileSync('index.html','utf8');
const script=html.split('<script>')[1].split('</script>')[0];
const first=script.indexOf('function suggestionIdentity(e){');
const last=script.indexOf('function personalDashboardTop(){',first);
assert(first>0&&last>first,'Home shortlist helpers are present');
const context={catalog:[],discovery:[],status:{},assessments:{}};
const prefix=[
 'const today="2026-11-21";',
 'const all=()=>ctx.catalog;',
 'const discoveryEvents=ctx.discovery;',
 'const assessments=ctx.assessments;',
 'const statusOf=e=>ctx.status[e.id]||"";',
 'const sourceNeedsAttention=e=>Boolean(e.changed);',
 'const hasDirectConcertLink=e=>e.link_status!=="venue_or_generic"&&Boolean(e.url);',
 'const tasteResult=e=>({score:e.score??6});',
 'const normalizeConcertText=v=>String(v||"").toLowerCase().replace(/[^a-z0-9]+/g," ").trim();',
 'const photoOf=e=>e.image||"";',
 'const cleanArtist=e=>e.name;',
 'const h=s=>String(s??"").replace(/&/g,"&amp;").replace(/</g,"&lt;");',
 'const dt=s=>s;',
 'const concertLink=e=>e.url||"";'
].join('\n');
const funcs=new Function('ctx',prefix+'\n'+script.slice(first,last)+'\nreturn {dashboardSuggestionEntries,dashboardShortlistMarkup,suggestionIdentity};')(context);
const make=(id,name,score,opts={})=>({id,name,score,date:"2027-03-01",venue:"Podium",city:"Zwolle",genre:"Americana",url:"https://example.org/events/"+id,link_status:"event_page",...opts});
context.catalog=[
 make("a","Artist Alpha",9.7),
 make("b","Artist Bravo",9.1),
 make("c","Artist Charlie",8.8),
 make("d","Artist Delta",8.5),
 make("e","Artist Echo",7.6),
 make("f","Artist Foxtrot",7.3,{verification:"auto_verified_schema",genre:"Muziek / nog niet ingedeeld"}),
 make("g","Artist Golf",7.0,{verification:"historical_unverified"}),
 make("h","Artist Hotel",9.9,{date:"2026-11-19"}),
 make("i","Artist India",9.9,{priority:"UITVERKOCHT"}),
 make("j","Artist Juliet",9.9,{changed:true})
];
context.discovery=[make("dis1","New Candidate",6.5,{genre:"",link_status:undefined,verification:"review_schema"}),
 make("dis2","Artist Alpha",10.0,{link_status:undefined})];
let initial=funcs.dashboardSuggestionEntries();
assert(initial.length===6,'Only six suggestions, got '+initial.length);
assert(new Set(initial.map(x=>x.event.name)).size===initial.length,'Do not show same artist twice');
assert(initial.some(x=>x.event.id==="a"),'High match shows');
assert(initial.some(x=>x.event.id==="f"),'New official venue discovery shows');
assert(!initial.some(x=>["h","i","j"].includes(x.event.id)),'Past, sold out and changed are excluded');
assert(!initial.some(x=>x.event.id==="dis2"),'Identical discovery candidate must be deduplicated');
const markup=funcs.dashboardShortlistMarkup();
assert(markup.includes('Nieuwe suggesties om te shortlisten'));
assert(markup.includes('data-action="interested"'));
assert(markup.includes('data-action="rejected"'));
assert(markup.includes('data-tab="inbox"'));
assert(markup.includes('data-tab="all"'));
context.status.a="interested";
context.status.b="rejected";
context.status.c="booked";
context.assessments.d={overall:8};
const after=funcs.dashboardSuggestionEntries();
assert(after.every(x=>!["a","b","c","d"].includes(x.event.id)),'Handled and reviewed shows disappear');
context.catalog=[];
context.discovery=[make("dis3","New Discovery",7.8,{genre:"",link_status:undefined})];
context.status={};
context.assessments={};
assert.equal(funcs.dashboardSuggestionEntries()[0].event.id,"dis3");
context.status.dis3="interested";
assert.equal(funcs.dashboardSuggestionEntries().length,0,'Selected discovery not repeated');
assert(script.includes("verification:'candidate_unverified'"),'Chosen discovery stays explicitly unverified');
assert(script.includes('extra=[...extra.filter(x=>x.id!==id)'), 'Chosen discovery saved in personal list');
console.log('Startscherm shortlist tests passed');
