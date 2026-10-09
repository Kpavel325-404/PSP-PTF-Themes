'use strict';
const fs=require('fs'), path=require('path');
const modules=process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
const sharp=require(modules?require.resolve('sharp',{paths:[modules]}):'sharp');
const root=path.resolve(__dirname,'..');
async function main(){
  for(const theme of JSON.parse(fs.readFileSync(path.join(root,'themes.json')))){
    const assets=path.join(root,'themes',theme.slug,'assets');
    const output=path.join(assets,'indexed');
    fs.mkdirSync(output,{recursive:true});
    let count=0;
    for(const entry of JSON.parse(fs.readFileSync(path.join(assets,'manifest.json')))){
      if(entry.obj===1||(entry.obj===0&&entry.sub===1))continue;
      const source=path.join(assets,entry.file), dest=path.join(output,entry.file);
      if(entry.focus)fs.copyFileSync(source,dest);
      else await sharp(source).png({palette:true,colours:256,dither:0,effort:10}).toFile(dest);
      count++;
    }
    console.log(JSON.stringify({theme:theme.slug,indexedIcons:count,dithering:false}));
  }
}
main().catch(e=>{console.error(e);process.exit(1)});
