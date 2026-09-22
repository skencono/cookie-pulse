#!/usr/bin/env python3
"""Build public/thread.html from X_THREAD.md (tiny markdown renderer, no deps)."""
import json, re

md = open("/home/ubuntu/cookiechain/X_THREAD.md").read()

page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Cookie Pulse — X Thread</title>
<style>
 body{background:#0b0710;color:#f3ecff;font-family:system-ui,-apple-system,sans-serif;
   max-width:820px;margin:0 auto;padding:26px 20px 70px;line-height:1.7}
 h1{font-size:25px}h2{font-size:17px;color:#ffb545;margin-top:24px}
 h3{font-size:12.5px;color:#9d8bb8;margin:18px 0 6px;text-transform:uppercase;letter-spacing:1px}
 pre{background:#1a1128;border:1px solid #33224d;border-radius:10px;padding:13px;
   white-space:pre-wrap;font-size:12.5px;font-family:ui-monospace,Menlo,monospace}
 a{color:#7cc4ff}code{background:#00000044;padding:2px 6px;border-radius:5px}
 .back{display:inline-block;margin-bottom:14px;font-size:13px}
 hr{border:0;border-top:1px solid #33224d;margin:20px 0}
 ul{padding-left:22px}li{margin:3px 0}
</style></head><body>
<a class="back" href="/">← back to Cookie Pulse</a>
<div id="body"></div>
<script>
const MD = __MD__;
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function md2html(src){
  let s = esc(src);
  s = s.replace(/```([a-z]*)\\n([\\s\\S]*?)```/g, (m,l,c)=> '\\u0000PRE'+btoa(unescape(encodeURIComponent(c)))+'PRE\\u0000');
  s = s.replace(/^### (.*)$/gm,'<h3>$1</h3>')
       .replace(/^## (.*)$/gm,'<h2>$1</h2>')
       .replace(/^# (.*)$/gm,'<h1>$1</h1>')
       .replace(/^---$/gm,'<hr>')
       .replace(/\\*\\*(.+?)\\*\\*/g,'<strong>$1</strong>')
       .replace(/`([^`]+)`/g,'<code>$1</code>')
       .replace(/\\[(.+?)\\]\\((.+?)\\)/g,'<a href="$2" target="_blank">$1</a>');
  s = s.replace(/^(- .*)$/gm,'<li>$1</li>')
       .replace(/(?:<li>[\\s\\S]*?<\\/li>\\n?)+/g, m => '<ul>'+m+'</ul>');
  s = s.split('\\n').map(l => l.startsWith('<')||l.startsWith('\\u0000') ? l : (l.trim()? '<p>'+l+'</p>' : '')).join('');
  s = s.replace(/\\u0000PRE([A-Za-z0-9+/=]+)PRE\\u0000/g, (m,b)=>'<pre>'+decodeURIComponent(escape(atob(b)))+'</pre>');
  return s;
}
document.getElementById('body').innerHTML = md2html(MD);
</script></body></html>
""".replace("__MD__", json.dumps(md))

open("/home/ubuntu/cookiechain/public/thread.html", "w").write(page)
print("wrote thread.html", len(page), "bytes")
