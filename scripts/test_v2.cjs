// Offline checks for ConcertRadar v2. No network.
const fs=require('fs'),assert=require('assert').strict;
const html=fs.readFileSync('index.html','utf8');
const js=html.split('<script>')[1].split('</script>')[0];
new Function(js);
for(const term of ['mobileTab','compactCards','scoreDetails(e)','listeningHistoryBoost','musicHistoryMarkup','bindMusicHistory','freshness(e)','checkMaxAgeDays','googleCalendarEventUrl','outlookCalendarEventUrl','Check nu bij podium','Prijs onbekend','Bronprijs (niet live)']){
 assert(js.includes(term),'Missing feature: '+term);
}
const start=js.indexOf('function nextDateYMD(day){'),end=js.indexOf('function calendarIcs(){',start);
assert(start>0&&end>start);
const fn=new Function('const statusOf=()=>"";'+js.slice(start,end)+'return {nextDateYMD,googleCalendarEventUrl,outlookCalendarEventUrl};')();
const e={id:'test',name:'Willow Avalon',date:'2027-03-14',venue:'Testpodium',city:'Groningen',url:'https://example.org/event'};
assert.equal(fn.nextDateYMD('2027-03-14'),'2027-03-15');
const google=new URL(fn.googleCalendarEventUrl(e)),outlook=new URL(fn.outlookCalendarEventUrl(e));
assert.equal(google.hostname,'calendar.google.com');
assert.equal(google.searchParams.get('dates'),'20270314/20270315');
assert.equal(google.searchParams.get('text'),'Willow Avalon');
assert.equal(outlook.hostname,'outlook.live.com');
assert.equal(outlook.searchParams.get('allday'),'true');
assert.equal(outlook.searchParams.get('startdt'),'2027-03-14T00:00:00');
assert.equal(outlook.searchParams.get('enddt'),'2027-03-15T00:00:00');
const a=js.indexOf('function listeningHistoryBoost(e){'),b=js.indexOf('function saveMusicHistory(',a);
assert(a>0&&b>a);
const script='const appSettings=ctx;const tasteNorm=s=>s.toLowerCase();const artistTokens=e=>[e.name];'+js.slice(a,b)+';return listeningHistoryBoost;';
const boost=new Function('ctx',script)({listeningHistory:{artists:{'willow avalon':12}}});
assert(boost({name:'Willow Avalon'})>0);
assert.equal(boost({name:'Unheard Artist'}),0);
assert(boost({name:'Willow Avalon'})<=.65);
console.log('ConcertRadar v2 offline checks passed');
