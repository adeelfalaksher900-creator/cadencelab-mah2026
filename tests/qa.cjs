const {chromium}=require('playwright'),path=require('path'),fs=require('fs');
const {default:AxeBuilder}=require('../web/node_modules/@axe-core/playwright');
(async()=>{
 const b=await chromium.launch({executablePath:path.resolve('tools/chromium'),args:['--no-sandbox','--no-zygote','--disable-features=V8TrapHandler','--use-gl=angle','--use-angle=swiftshader','--disable-dev-shm-usage']});
 const context=await b.newContext({viewport:{width:1440,height:1024}});const p=await context.newPage(),errors=[],requests=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>requests.push({url:r.url(),method:r.method()}));
 await p.goto('http://127.0.0.1:4178');await p.locator('.finding').first().waitFor();await p.evaluate(()=>document.fonts.ready);
 const scans=[];
 for(const tab of ['Compare','Dataset','Method']){
  await p.getByRole('button',{name:tab,exact:true}).click();const a=await new AxeBuilder({page:p}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();scans.push({screen:tab,violations:a.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)}))});
 }
 await p.getByRole('button',{name:'Compare',exact:true}).click();await p.getByRole('button',{name:'Compare recordings',exact:true}).click();
 await p.getByRole('button',{name:'Run local comparison'}).click();if(!await p.getByRole('alert').count())throw Error('Empty-input validation missing');
 await p.locator('textarea').fill('</textarea><img src=x onerror="window.__injected=1">');if(await p.evaluate(()=>window.__injected))throw Error('HTML injection');
 const dialog=await new AxeBuilder({page:p}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();scans.push({screen:'Upload',violations:dialog.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)}))});
 await p.getByRole('button',{name:'Close upload dialog'}).click();
 await p.setViewportSize({width:390,height:844});const overflow=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth);await p.screenshot({path:'docs/mobile.png',fullPage:true});
 if(overflow)throw Error('Mobile overflow');await p.setViewportSize({width:1440,height:1024});await p.screenshot({path:'docs/dashboard.png',fullPage:true});
 if(requests.some(r=>r.method!=='GET'))throw Error('Unexpected write or telemetry request');if(errors.length)throw Error(errors.join('\n'));
 const result={screens:scans,page_errors:errors,mobile_overflow:overflow,network_methods:[...new Set(requests.map(r=>r.method))],note:'Automated checks of the owned local app. No human usability study.'};fs.writeFileSync('docs/browser-qa.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));if(scans.some(s=>s.violations.length))process.exitCode=1;await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
