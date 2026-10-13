import {createRequire} from 'node:module';
const require=createRequire(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES+'/playwright/package.json');
const {chromium}=require('playwright');
import fs from 'node:fs/promises';import path from 'node:path';
const goods=JSON.parse(await fs.readFile('goods.json','utf8'));const meta=JSON.parse(await fs.readFile('stage4_v13/metadata.json','utf8'));
const only=new Set(process.argv.slice(2));
const b=await chromium.launch({executablePath:process.env.WB_CHROMIUM,args:['--no-sandbox','--single-process','--disable-gpu','--allow-file-access-from-files']});
const pg=await b.newPage({viewport:{width:900,height:1200}});await pg.goto('file://'+path.resolve('cover.html'));
const log=[];
for(const x of goods){
 if(only.size&&!only.has(x.code))continue;const m=meta[x.code];if(!m)throw Error('Missing mask '+x.code);
 if(m.mask_review!=='checked-v13')throw Error('Review mask before replication: '+x.code);
 for(const c of x.cards){
  const copies=m.assorti?1:c.quant*(m.count||1)/m.source_units;
  const grid=!m.assorti&&copies<=20&&(!m.cord||copies<=4||m.count);
  const img=(grid&&m.tone==='white'?'stage4_v13/white/':'stage4_v13/cut/')+x.code+(grid&&m.tone==='white'?'.jpg':'.png');
  const d={qty:c.quant,forms:m.forms,heading:m.heading,sub:m.sub,chips:m.chips,bg:m.bg,tone:m.tone,accent:'#136F63',font:'grotesk',img,ratio:m.width/m.height,
   line2:m.count?(c.quant===1?`${m.count} бейджей`:`по ${m.count} бейджей`):'в наборе',plaque:!x.cards.every(c=>c.quant===1),layout:grid?'grid':'stack',displayQty:copies,copies:Math.min(40,copies),compactCord:!!m.cord};
  const result=await pg.evaluate(d=>render(d),d);const name=`${c.idvh}_${c.quant}.jpg`;
  await pg.screenshot({path:'stage4_v13/covers/'+name,type:'jpeg',quality:94});
  log.push({file:name,code:x.code,idvh:c.idvh,quant:c.quant,tone:m.tone,layout:d.layout,sourceQty:copies,visibleCopies:grid?copies:Math.min(40,copies),...result});
 }
 console.log(x.code,log.length);
}
await b.close();await fs.writeFile(only.size?'stage4_v13/probe_log.json':'stage4_v13/coverlog.json',JSON.stringify(log,null,1));
if(log.some(l=>l.overflow))throw Error('Overflow in covers');
