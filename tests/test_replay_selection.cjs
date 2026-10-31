const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const elements=new Map();
function element(id){if(!elements.has(id))elements.set(id,{value:id==='firm'?'1':'2026',textContent:'stale',disabled:false,options:[],setAttribute(k,v){this[k]=v},replaceChildren(){this.textContent='';this.options=[]},append(){},add(v){this.options.push(v)}});return elements.get(id)}
const context=vm.createContext({document:{getElementById:element,createElementNS:()=>({setAttribute(){}})},setInterval,clearInterval,fetch:()=>new Promise(()=>{}),Option:function(text,value){this.text=text;this.value=String(value)}});
vm.runInContext(fs.readFileSync('web/index.html','utf8').match(/<script>([\s\S]*)<\/script>/)[1],context);
// A previously rendered selection followed by a malformed later firm.
vm.runInContext("records=[{firm_id:2,technology:'CES',policy:'random',round:1}];pair={random:[{round:200}],guided:[{round:200}]}",context);
element('firm').value='2';
element('firm').onchange();
assert.match(element('status').textContent,/missing or duplicate rounds/);
for(const id of ['random','guided','advantage'])assert.equal(element(id).textContent,'—');
for(const id of ['chart','values','source'])assert.equal(element(id).textContent,'');
for(const id of ['firm','play','step','round'])assert.equal(element(id).disabled,true);
assert.equal(element('seed').disabled,false);
assert.equal(element('status').role,'alert');
assert.equal(vm.runInContext('records.length+pair.random.length+pair.guided.length',context),0);
console.log('PASS: malformed firm selection clears stale values, stops replay and allows seed recovery');
