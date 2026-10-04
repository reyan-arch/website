import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';

const source = readFileSync(new URL('../site/lead-capture.js', import.meta.url), 'utf8');
function capture(formName, fields, hidden = []) {
  const posts = [], timers = []; let submit;
  const context = {
    URLSearchParams,
    location: { href:'https://irgmedia.org/contact' },
    navigator: { sendBeacon(url,body) { posts.push({url,body:Object.fromEntries(body)}); return true; } },
    document: { referrer:'', addEventListener(event,callback) { if (event==='submit') submit=callback; } },
    setTimeout(callback,ms) { timers.push({callback,ms}); },
  };
  vm.runInNewContext(source, context);
  const elements = Object.entries(fields).map(([name,value]) => ({name,value,tagName:'INPUT',type:'text',tabIndex:0,offsetParent:{},closest:()=>null,getAttribute:()=>null}));
  for (const [name,value] of hidden) elements.push({name,value,tagName:'INPUT',type:'hidden',tabIndex:-1,getAttribute:()=>null,closest:()=>null});
  submit({target:{tagName:'FORM',elements,getAttribute:()=>formName}});
  return {posts,timers};
}
const enquiry = {name:'Example Person',email:'test@example.com',company:'Example',timing:'Next quarter',project_context:'An illustrative campaign brief.'};
test('Project enquiry retains its Make recipient and exact field names without timer-based success', () => {
  const {posts,timers}=capture('Project enquiry',enquiry);
  assert.equal(posts.length,1);
  assert.equal(posts[0].url,'https://hook.eu2.make.com/2zijd3f6yfwi3d4brzk9gwrlmz2a9mll');
  for (const [key,value] of Object.entries(enquiry)) assert.equal(posts[0].body[key],value);
  assert.equal(timers.some(t=>t.ms===250),false);
});
test('Excluded Resource download flow retains its existing confirmation timing', () => {
  const {posts,timers}=capture('Resource download form',enquiry);
  assert.equal(posts.length,1);
  assert.equal(timers.some(t=>t.ms===250),true);
});
test('Filled honeypot prevents recipient traffic and confirmation', () => {
  const {posts,timers}=capture('Project enquiry',enquiry,[['company','spam']]);
  assert.equal(posts.length,0); assert.equal(timers.length,0);
});
test('Invalid email never reaches the Make recipient', () => {
  assert.equal(capture('Project enquiry',{...enquiry,email:'invalid'}).posts.length,0);
});
