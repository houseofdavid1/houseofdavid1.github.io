// gen_research.py가 수식(KaTeX)을 HTML로 미리 렌더링할 때 호출하는 보조 스크립트.
// 필요: 이 폴더에서  npm install katex@0.16.11   (assets/katex/katex.min.css 버전과 맞출 것)
const k=require('katex');
const a=JSON.parse(require('fs').readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(a.map(s=>k.renderToString(s,{displayMode:true,throwOnError:true,output:'html'}))));
