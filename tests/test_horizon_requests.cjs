const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes=new Map(),pending=[];
function node(id){if(!nodes.has(id))nodes.set(id,{value:id==='horizon'?'200':'2026',textContent:'old',disabled:false,options:[],children:[],setAttribute(k,v){this[k]=v},replaceChildren(){this.children=[];this.textContent=''},append(v){this.children.push(v)},add(v){this.options.push(v)}});return nodes.get(id)}
const ctx=vm.createContext({document:{getElementById:node,createElementNS:()=>({setAttribute(){}})},setInterval,clearInterval,fetch:url=>new Promise((resolve,reject)=>pending.push({url,resolve,reject})),Option:function(text,value){this.value=String(value)}});
vm.runInContext(fs.readFileSync('web/index.html','utf8').match(/<script>([\s\S]*)<\/script>/)[1],ctx);
(async()=>{
 // Initial 200 metadata requests are pending. Start a 50 request, then reject old requests.
 vm.runInContext("records=[{seed:2026}];pair={random:[{}],guided:[{}]}",ctx);
 node('horizon').value='50';const latest=vm.runInContext('loadHorizon()',ctx);
 assert.equal(vm.runInContext('records.length+pair.random.length+pair.guided.length',ctx),0);
 assert.equal(node('random').textContent,'—');assert.equal(node('source').textContent,'');assert.equal(node('play').disabled,true);
 pending[0].reject(new Error('stale 200 manifest failure'));pending[1].reject(new Error('stale 200 summary failure'));
 await new Promise(resolve=>setImmediate(resolve));
 assert.equal(node('status').textContent,'Loading horizon…');assert.equal(node('horizon').disabled,true);
 pending[2].reject(new Error('current 50 manifest failure'));pending[3].reject(new Error('current 50 summary failure'));await latest;
 assert.match(node('status').textContent,/current 50/);assert.equal(node('seed').disabled,true);assert.equal(node('retry').disabled,false);assert.equal(vm.runInContext('manifest',ctx),null);assert.equal(node('horizon').disabled,false);assert.equal(node('play').disabled,true);
 // Seed rejection from the old generation must not replace a newer horizon status.
 vm.runInContext("manifest={partitions:{2026:{file:'seed-2026.json'}}};activeHorizon=200",ctx);
 const oldSeed=vm.runInContext('loadSeed()',ctx);node('horizon').value='100';const newer=vm.runInContext('loadHorizon()',ctx);
 pending[4].reject(new Error('old seed failure'));await oldSeed;
 assert.equal(node('status').textContent,'Loading horizon…');assert.equal(node('play').disabled,true);
 pending[5].reject(new Error('current 100 failure'));pending[6].reject(new Error('current 100 summary failure'));await newer;
 assert.match(node('status').textContent,/current 100/);
 console.log('PASS: overlapping horizons, stale metadata/seed failures, clearing and recoverable error controls');
})().catch(e=>{console.error(e);process.exitCode=1});
