// Targeted replacement on an accepted 900x1200 cover. Original pixels are the base.
async function replaceVariantsOnCover(d) {
  const root = document.getElementById('root');
  root.replaceChildren();
  root.style.cssText='position:relative;width:900px;height:1200px;padding:0;overflow:hidden;font-family:Manrope,sans-serif;color:#1E1C1A';
  const put=(e,css)=>{e.style.cssText=css;e.style.setProperty('position','absolute','important');root.append(e);return e;};
  const original=put(new Image(),'left:0;top:0;width:900px;height:1200px');original.src=d.original;
  await original.decode();await document.fonts.load('800 26px Manrope');await document.fonts.load('600 20px Manrope');
  const height=d.mode==='collage'?300:142;
  const oldTop=d.qty===1?740:716,top=oldTop-(height-142);
  if(d.mode==='collage'){
    const clear=put(new Image(),'left:56px;top:350px;width:788px;height:'+(oldTop-350)+'px');clear.src=d.background;await clear.decode();
    const main=put(new Image(),'left:56px;top:350px;width:788px;height:'+(top-362)+'px;object-fit:contain');main.src=d.acceptedMain;await main.decode();
  }
  const panel=put(document.createElement('div'),'left:56px;top:'+top+'px;width:788px;height:'+(984-top)+'px;box-sizing:border-box;display:flex;flex-direction:column;gap:8px;background:#fff;border-radius:22px;padding:14px 18px 16px;box-shadow:0 2px 6px #0001');
  const heading=document.createElement('div');heading.textContent=d.mode==='fragments'?'Фрагменты возможных дизайнов обложек':'Возможные дизайны обложек';heading.style.cssText='font-size:26px;font-weight:800;line-height:1.2;text-align:center';panel.append(heading);
  const row=document.createElement('div');row.style.cssText='display:flex;justify-content:center;align-items:center;gap:12px;height:'+height+'px;flex-shrink:0';panel.append(row);
  for(const src of d.variants){const im=new Image();im.src=src;im.style.cssText='height:'+height+'px;max-width:'+Math.floor((752-12*(d.variants.length-1))/d.variants.length)+'px;object-fit:contain;min-width:0';row.append(im);}
  const text=document.createElement('div');text.style.cssText='text-align:center;font-size:20px;font-weight:600;line-height:1.2';panel.append(text);
  const lines=d.qty===1?['Дизайн без возможности выбора из наличия на складе']:['В комплекте могут быть одинаковые или разные дизайны','(без возможности выбора из наличия на складе).'];
  for(const line of lines){const e=document.createElement('div');e.textContent=line;e.style.whiteSpace='nowrap';text.append(e);}
  await Promise.all([...row.children].map(im=>im.decode()));await document.fonts.ready;
  for(const e of text.children){let size=20;while(e.scrollWidth>text.clientWidth&&size>15)e.style.fontSize=(--size)+'px';}
  const tb=text.getBoundingClientRect().bottom;
  if(tb>996||panel.scrollHeight>panel.clientHeight||[...text.children].some(e=>e.scrollWidth>text.clientWidth))throw Error('Variant panel overflow');
  return {mode:d.mode,variantCount:d.variants.length,panelTop:top,textBottom:tb,variantHeight:height,originalMainPreserved:d.mode!=='collage'};
}
