import { chromium } from 'playwright';
import fs from 'node:fs';

const browser=await chromium.launch({headless:true});
const context=await browser.newContext({
  userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  locale:'en-AU', viewport:{width:1440,height:1000}
});
const page=await context.newPage();
const responses=[];
page.on('response',async r=>{
  const u=r.url(); const ct=(await r.allHeaders())['content-type']||'';
  if(/map\.ocearch\.org|mapotic|ocearch/i.test(u)&&(/json/i.test(ct)||/api\/v1/i.test(u))){
    try{const text=await r.text(); if(text.length<15_000_000)responses.push({url:u,status:r.status(),contentType:ct,body:text});}catch{}
  }
});
const target='https://map.ocearch.org/2344847-contender';
let nav=null;
try{nav=await page.goto(target,{waitUntil:'domcontentloaded',timeout:60000});}catch(e){console.error('goto',e.message)}
await page.waitForTimeout(15000);
const body=await page.content();
fs.mkdirSync('report',{recursive:true});
fs.writeFileSync('report/ocearch-browser-page.html',body);
fs.writeFileSync('report/ocearch-browser-responses.json',JSON.stringify(responses.map(x=>({...x,body:x.body.slice(0,2_000_000)})),null,2));
console.log('NAV',nav?.status(), 'URL',page.url(),'RESPONSES',responses.length);
for(const x of responses){console.log('\nRESP',x.status,x.url,x.contentType,'bytes',x.body.length);console.log(x.body.slice(0,3000));}
await browser.close();
