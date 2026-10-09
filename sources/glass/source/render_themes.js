'use strict';
// Desktop approximation only. Artwork is imported from the final PTF bytes.
const fs=require('fs'),path=require('path'),vm=require('vm');
const {makeContext,declaration,source,canvas,root}=require('./verify_themes.js');
const first={2:'Memory Stick™',4:'UMD™',6:'Камера',8:'Обмен играми',10:'Управление сохранениями',
  12:'Обновление UMD™',14:'Обновление системы',16:'Соединение USB',18:'Настройки видео',
  20:'Настройки фото',22:'Настройки системы',24:'Настройки темы',26:'Дата и время',
  28:'Энергосбережение',30:'Внешний дисплей',32:'Настройки звука',34:'Безопасность',
  36:'Настройки RSS',38:'Настройки сети',40:'Руководство пользователя',42:'Дистанционное воспроизведение',
  44:'Интернет-радио',46:'Канал RSS',48:'Интернет-браузер',50:'Поиск в Интернете',
  52:'Управление учетной записью',54:'Дополнительно',56:'Настройки Bluetooth',58:'SensMe™'};
const category={0:'Дополнительно',1:'Настройки',2:'Фото',3:'Музыка',4:'Видео',5:'ТВ',6:'Игра',7:'Сеть',8:'Дополнительно'};
const names=['currentProfile','visibleCategoryAssets','visibleItemsForCategory','firstLevelDisplayLabel',
  'imageDataToCanvas','drawImageDataFit','getAsset','categoryAssets','bodyAsset','focusAsset',
  'isPspGoVirtualFirstLevel','resolvedBodyAsset','resolvedFocusAsset','clamp01','easeOutCubic',
  'setPspFont','drawPspText','registerPreviewHit','drawXmb','drawStatusBar','focusPulse',
  'firstLevelDimAlpha','drawVerticalItems','secondLevelAssetPair','drawSecondLevelMenu'];
const screens=[{name:'settings',category:1,selected:24},{name:'music',category:3,selected:2},
  {name:'games',category:6,selected:10},{name:'network',category:7,selected:48},
  {name:'rss',category:7,selected:46},{name:'photo',category:2,selected:6},
  {name:'video',category:4,selected:2},{name:'update',category:1,selected:14},
  {name:'power',category:1,selected:28}];
async function main(){
  canvas.GlobalFonts.registerFromPath(path.join(__dirname,'vendor/preview-font.ttf'),'PSP Preview');
  for(const theme of JSON.parse(fs.readFileSync(path.join(root,'themes.json')))){
    const context=makeContext(),bytes=new Uint8Array(fs.readFileSync(path.join(root,'dist',theme.file)));
    const parsed=await context.parsePtf(bytes.buffer);
    context.state={theme:parsed.theme,assets:parsed.assets,previewHitRegions:[],modelProfile:'3000',
      nav:{categoryPos:0,itemPos:0,secondPos:0,level:1},animationStart:0,viewMode:'xmb',showGuides:false};
    context.FIRST_LABELS=first;context.CATEGORY_LABELS=category;
    for(const a of parsed.assets)if(a.objIdx===2)a.role.label=category[a.subIdx];
    context.MODEL_PROFILES={'3000':{categories:[1,2,3,4,5,6,7,8],excludedItems:[56]}};
    context.PROFILE_CATEGORY_ITEMS={};context.PSP_GO_VIRTUAL_FIRST_LEVEL_IDS=new Set([60,62,64]);
    context.PSP_SCALE=2;context.PSP_FONT_STACK='PSP Preview';context.els={pulseToggle:{checked:false}};
    context.requestAnimationFrame=()=>{};
    context.document={createElement:tag=>{if(tag!=='canvas')throw new Error('Unexpected DOM tag');return canvas.createCanvas(1,1);}};
    context.assetVisibleForProfile=()=>true;context.formatPspDateTime=()=>'7/10 19:01';
    context.drawStorageItemLabel=()=>false;
    context.PSP_BATTERY_IMAGE=await canvas.loadImage(path.join(__dirname,'vendor/psp_battery.png'));
    const layoutStart=source.indexOf('const XMB_LAYOUT ='),layoutEnd=source.indexOf('\n});',layoutStart)+4;
    vm.runInContext(source.slice(layoutStart,layoutEnd).replace('const XMB_LAYOUT =','globalThis.XMB_LAYOUT ='),context);
    const catsStart=source.indexOf('const CATEGORY_ITEMS ='),catsEnd=source.indexOf('\n};',catsStart)+3;
    vm.runInContext(source.slice(catsStart,catsEnd).replace('const CATEGORY_ITEMS =','globalThis.CATEGORY_ITEMS ='),context);
    vm.runInContext(names.map(declaration).join('\n'),context);
    const target=canvas.createCanvas(960,544);context.ctx=target.getContext('2d');
    const out=path.join(root,'verification',theme.slug);fs.mkdirSync(out,{recursive:true});
    for(const screen of screens){
      const cats=context.visibleCategoryAssets();
      context.state.nav={categoryPos:cats.findIndex(a=>a.subIdx===screen.category),itemPos:0,secondPos:0,level:1};
      const ids=context.visibleItemsForCategory(screen.category);
      context.state.nav.itemPos=ids.indexOf(screen.selected);
      if(context.state.nav.itemPos<0)throw new Error('Selected menu item absent');
      context.drawXmb(2000);
      fs.writeFileSync(path.join(out,'xmb-'+screen.name+'.png'),target.toBuffer('image/png'));
      const small=canvas.createCanvas(480,272),ctx=small.getContext('2d');
      ctx.drawImage(target,0,0,480,272);
      fs.writeFileSync(path.join(out,'native-'+screen.name+'.png'),small.toBuffer('image/png'));
    }
    console.log(JSON.stringify({theme:theme.slug,renderedScreens:screens.length,source:'Compiled PTF',
      notice:'Desktop preview, not a physical PSP screenshot'}));
  }
}
main().catch(e=>{console.error(e);process.exit(1)});
