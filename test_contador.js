const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const logic = html.split('// ===LOGIC-START===')[1].split('// ===LOGIC-END===')[0];
const { createCounter, thresholdsFrom, openness } = new Function(logic + '; return {createCounter, thresholdsFrom, openness};')();

function rng(seed){let s=seed>>>0;return()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};}
function gauss(r){let u=0,v=0;while(!u)u=r();v=r();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}

function run(signalFn, durMs, seed, opts) {
  const r = rng(seed), c = createCounter(opts), evs = [];
  let t = 0;
  while (t < durMs) {
    const v = signalFn(t, r);
    if (v === null) c.lost(t); else { const e = c.feed(t, v, 0.9); if (e) evs.push(e); }
    t += 20 + r() * 25;               // 20-45 ms, quadros irregulares
  }
  return { reps: c.reps, ignored: c.ignored, evs, c };
}
const cyc = (P, lo, hi, sd) => (t, r) => (lo+hi)/2 + (hi-lo)/2*Math.cos(2*Math.PI*t/P) + sd*gauss(r);

let allOk = true;
function report(name, expected, vals) {
  const err = vals.map(v => Math.abs(v - expected));
  const exact = err.filter(e => e === 0).length;
  const mean = err.reduce((a,b)=>a+b,0)/err.length;
  const mx = Math.max(...err);
  console.log(name.padEnd(46), 'esperado', String(expected).padStart(2), '| exato', exact+'/'+vals.length, '| erro médio', mean.toFixed(2), '| erro máx', mx);
  return exact;
}

console.log('--- A. ciclos limpos, faixa 1.0 a 2.0, ruído 0.05, 100 sementes ---');
for (const P of [700, 1500, 3000, 5000]) {
  const vals = []; for (let s=1;s<=100;s++) vals.push(run(cyc(P,1.0,2.0,0.05), 10*P+1, s).reps);
  report('período ' + P + ' ms, 10 ciclos', 10, vals);
}

console.log('--- B. tremor / mão parada (não deve contar) ---');
{
  const v1=[],v2=[];
  for (let s=1;s<=100;s++){
    v1.push(run((t,r)=>1.55+0.10*Math.sin(2*Math.PI*5*t/1000)+0.05*gauss(r), 20000, s).reps);
    v2.push(run((t,r)=>1.95+0.15*gauss(r), 20000, s).reps);
  }
  report('tremor 5 Hz em mão semicerrada', 0, v1);
  report('mão aberta parada, ruído 0.15', 0, v2);
}

console.log('--- C. mão some no meio do ciclo (ciclo parcial não deve contar) ---');
{
  const P=3000, vals=[];
  for (let s=1;s<=100;s++){
    // 5 ciclos; o 3º ciclo (t 6000-9000) perde a mão entre 7200 e 8800 (fechada) e volta aberta
    const base=cyc(P,1.0,2.0,0.05);
    vals.push(run((t,r)=> (t>7200&&t<8800)? null : base(t,r), 5*P+1, s).reps);
  }
  report('5 ciclos, 1 com perda de rastreio', 4, vals);
}

console.log('--- D. amplitude reduzida (1.5 a 1.9): padrão x calibrado ---');
{
  const P=3000, std=[], cal=[];
  for (let s=1;s<=100;s++){
    std.push(run(cyc(P,1.5,1.9,0.04), 10*P+1, s).reps);
    // calibração: 3 ciclos lentos de 10 s com o mesmo perfil, depois uso
    const r = rng(1000+s), vals=[]; let t=0;
    while (t<10000){ vals.push(cyc(3000,1.5,1.9,0.04)(t,r)); t+=33; }
    const th = thresholdsFrom(vals);
    cal.push(th ? run(cyc(P,1.5,1.9,0.04), 10*P+1, s, th).reps : -99);
  }
  report('limiares padrão (esperado 10, limitação)', 10, std);
  report('após calibração de 10 s', 10, cal);
}

console.log('--- E. calibração sem movimento suficiente ---');
{
  const vals=[]; const r=rng(7); for(let i=0;i<300;i++) vals.push(1.9+0.03*gauss(r));
  console.log('limiares com mão parada:', thresholdsFrom(vals), '(esperado null)');
}

console.log('--- F. evento: campos e valores típicos (período 3000 ms) ---');
{
  const x = run(cyc(3000,1.0,2.0,0.05), 9001, 42);
  console.log(JSON.stringify(x.evs[0]), '| duração mediana', x.evs.map(e=>e.duration_ms).sort((a,b)=>a-b)[1]);
}
