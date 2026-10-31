const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes=new Map();function node(id){if(!nodes.has(id))nodes.set(id,{value:'1',textContent:'',options:[],children:[],setAttribute(k,v){this[k]=v},replaceChildren(){this.children=[]},append(v){this.children.push(v)},add(v){this.options.push(v)}});return nodes.get(id)}
const ctx=vm.createContext({document:{getElementById:node,createElementNS:()=>({setAttribute(){},textContent:''})},setInterval,clearInterval,fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/index.html','utf8').match(/<script>([\s\S]*)<\/script>/)[1],ctx);
for(const [t,s,y] of [['Cobb-Douglas',.7,54.28814526898254],['Leontief',.7,100],['Linear',.95,68],['CES',.6375775139385773,52.893571900785915]]){
 const got=vm.runInContext(`productionOptimum('${t}')`,ctx);assert.ok(Math.abs(got-s)<1e-12);
 assert.ok(Math.abs(vm.runInContext(`productionOutput('${t}',${s})`,ctx)-y)<1e-10);
 for(let j=0;j<=180;j++)assert.ok(vm.runInContext(`productionOutput('${t}',${Math.min(.95,.05+j*.9/180)})`,ctx)<=y+1e-10);
}
vm.runInContext("drawProduction({seed:2026,firm_id:3,technology:'Linear',round:200,capital_share:.9396700129004708,current_output:67.58680051601883},{capital_share:.95,current_output:68})",ctx);
assert.match(node('productionDetail2').textContent,/Random: s = 0.939670, Y = 67.586801/);
assert.match(node('productionContext').textContent,/firm 3.*round 200/);
vm.runInContext('clearProductionObservations()',ctx);
assert.doesNotMatch(node('productionDetail2').textContent,/Random:/);
assert.match(node('productionContext').textContent,/no selected observations/);
console.log('PASS: four fixed production optima, feasible grid bounds, observed markers and stale-marker clearing');
