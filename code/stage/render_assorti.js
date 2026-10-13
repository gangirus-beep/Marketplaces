async function renderAssorti(d){
const nb=v=>v.replaceAll(' %','\u00a0%').replaceAll(' г/м²','\u00a0г/м²').replaceAll('ГОСТ ','ГОСТ\u00a0').replaceAll(' — ','\u00a0— ').replace(/(\d+) (лист)/g,'$1\u00a0$2');
d={...d,sub:nb(d.sub),chips:d.chips.map(nb)};
const root=document.getElementById('root');let panel=document.getElementById('variants');if(!panel){panel=document.createElement('div');panel.id='variants';root.insertBefore(panel,document.getElementById('chips'));}
root.style.paddingBottom=d.assorti?'120px':'48px';root.style.gap=d.assorti?'12px':'22px';panel.style.display=d.assorti?'block':'none';if(!d.assorti)return render(d);
panel.replaceChildren();panel.style.cssText='display:flex;flex-direction:column;gap:8px;flex:0 0 auto;background:#fff;border-radius:22px;padding:14px 18px 16px;box-sizing:border-box;box-shadow:0 2px 6px #0001';
const h=document.createElement('div');h.textContent=d.variantTitle||(d.variantMode==='fragments'?'Фрагменты возможных дизайнов обложек':'Возможные дизайны обложек');h.style.cssText='font-size:26px;font-weight:800;text-align:center;line-height:1.2';panel.append(h);
const variantHeight=d.variantMode==='collage'?300:142;
const row=document.createElement('div');row.style.cssText='display:flex;align-items:center;justify-content:center;gap:12px;height:'+variantHeight+'px';panel.append(row);
for(const src of d.variants){let im=new Image();im.src=src;im.style.cssText='position:static;max-width:'+Math.floor((752-12*(d.variants.length-1))/d.variants.length)+'px;height:'+variantHeight+'px;object-fit:contain;min-width:0';row.append(im);}
const text=document.createElement('div');text.style.cssText='text-align:center;font-size:20px;line-height:1.2;font-weight:600';panel.append(text);
for(const line of (d.qty===1?['Дизайн без возможности выбора из наличия на складе']:['В комплекте могут быть одинаковые или разные дизайны','(без возможности выбора из наличия на складе).'])){const e=document.createElement('div');e.textContent=line;e.style.whiteSpace='nowrap';text.append(e);}
await Promise.all([...row.querySelectorAll('img')].map(i=>i.decode()));const chips=d.chips.filter(t=>!/(?:ассортимент|ассорти)/i.test(t));const picked=chips.length>=3?[chips[1],chips[2]]:chips.slice(0,2);
const result=await render({...d,chips:picked,layout:undefined,copies:1,tone:d.tone||'light',line2:'в комплекте',plaque:true});
const caption=document.createElement('div');caption.textContent=d.mainCaption||'Один из возможных вариантов';caption.style.cssText='position:absolute;left:0;bottom:0;width:100%;text-align:center;font-size:18px;font-weight:600;line-height:22px;color:#514e49';document.getElementById('zone').append(caption);
for(const e of text.children){let size=20;while(e.scrollWidth>text.clientWidth&&size>15)e.style.fontSize=(--size)+'px';}
const props=document.getElementById('chips').getBoundingClientRect(),tb=text.getBoundingClientRect().bottom;if(props.bottom>1081||tb>996||[...text.children].some(e=>e.scrollWidth>text.clientWidth))throw Error('Assortment overflow');
return {...result,assorti:true,variantCount:d.variants.length,variabilityTextBottom:tb,propertiesBottom:props.bottom,safeFooter:120};
}
