'use strict';
// Independent import: unchanged upstream PTF Studio parser + Skia BMP decoder.
const fs=require('fs'), path=require('path'), vm=require('vm');
const modules=process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
const canvas=require(modules?require.resolve('@napi-rs/canvas',{paths:[modules]}):'@napi-rs/canvas');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(__dirname,'vendor/ptf-studio-reader.js'),'utf8');
const declarations=[...source.matchAll(/^(?:async )?function (\w+)\(/gm)];
function declaration(name){
  const index=declarations.findIndex(m=>m[1]===name);
  if(index<0)throw new Error('Reader function absent: '+name);
  const start=declarations[index].index, next=declarations[index+1]?.index||source.length;
  const fragment=source.slice(start,next);
  return fragment.slice(0,fragment.lastIndexOf('}')+1);
}
function makeContext(){
  let context;
  const sandbox={console,TextEncoder,TextDecoder,ImageData:canvas.ImageData,
    CompressionStream,DecompressionStream,Response,Blob,
    window:{DecompressionStream}, CATEGORY_LABELS:{},FIRST_LABELS:{},
    decodeAsset:async asset=>{
      if(asset.fileType===5){
        const decoded=context.decodeGim(asset.rawCurrent);
        asset.imageData=decoded.imageData;asset.gimMeta=decoded.meta;asset.paletteCount=decoded.paletteCount;
      }else{
        const image=await canvas.loadImage(Buffer.from(asset.rawCurrent));
        const target=canvas.createCanvas(image.width,image.height),ctx=target.getContext('2d');
        ctx.drawImage(image,0,0);asset.imageData=ctx.getImageData(0,0,image.width,image.height);
      }
    }
  };
  context=vm.createContext(sandbox);
  const names=['align','u16','u32','readFixedString','normalizeThemeColor','roleFor',
    'decompressDeflate','parsePtf','decodeGim','countColors','readThemeColorRecord',
    'readThemeColorFromPtf','verifyBuiltPtfMetadata'];
  vm.runInContext(names.map(declaration).join('\n'),context);
  return context;
}
async function main(){
  const reports=[];
  for(const config of JSON.parse(fs.readFileSync(path.join(root,'themes.json')))){
    const context=makeContext(), file=path.join(root,'dist',config.file);
    const bytes=new Uint8Array(fs.readFileSync(file));
    const parsed=await context.parsePtf(bytes.buffer,path.basename(file));
    const assets=path.join(root,'themes',config.slug,'assets');
    const manifest=JSON.parse(fs.readFileSync(path.join(assets,'manifest.json')));
    if(parsed.assets.length!==manifest.length)throw new Error('Asset count mismatch');
    const output=path.join(root,'verification',config.slug,'decoded');
    fs.mkdirSync(output,{recursive:true});
    const failures=[];
    for(const asset of parsed.assets){
      const original=manifest.find(e=>e.obj===asset.objIdx&&e.sub===asset.subIdx);
      if(!original||asset.decodeError||!asset.imageData){
        failures.push({slot:`${asset.objIdx}:${asset.subIdx}`,error:asset.decodeError||'Missing image'});continue;
      }
      if(asset.imageData.width!==original.size[0]||asset.imageData.height!==original.size[1])
        failures.push({slot:`${asset.objIdx}:${asset.subIdx}`,error:'Dimensions changed'});
      if(asset.fileType===5&&(asset.gimMeta.format!==3||asset.paletteCount>256))
        failures.push({slot:`${asset.objIdx}:${asset.subIdx}`,error:'Invalid RGBA8888 palette'});
      if(original.focus&&asset.paletteCount>64)
        failures.push({slot:`${asset.objIdx}:${asset.subIdx}`,error:'Focus exceeds 64 colours'});
      fs.writeFileSync(path.join(output,original.file+'.rgba'),Buffer.from(asset.imageData.data));
      const image=canvas.createCanvas(asset.imageData.width,asset.imageData.height);
      image.getContext('2d').putImageData(asset.imageData,0,0);
      fs.writeFileSync(path.join(output,original.file),image.toBuffer('image/png'));
    }
    context.verifyBuiltPtfMetadata(bytes,{title:config.title,productId:config.product_id,
      version:config.version,themeColor:config.theme_color});
    const report={file:config.file,reader:'PTF Studio 1.0 independent reader + Skia BMP decoder',
      decodedAssets:parsed.assets.length,metadata:{title:parsed.theme.title,productId:parsed.theme.productId,
        version:parsed.theme.version,firmware:parsed.theme.pspVersion,color:parsed.theme.backgroundMode},failures};
    fs.writeFileSync(path.join(root,'verification',config.slug,'independent-verification.json'),JSON.stringify(report,null,2));
    reports.push(report);
    if(failures.length)throw new Error('Independent theme verification failed: '+config.slug);
  }
  console.log(JSON.stringify(reports));
}
module.exports={makeContext,declaration,source,canvas,root};
if(require.main===module)main().catch(e=>{console.error(e);process.exit(1)});
