(() => {
  'use strict';
  const byId = id => document.getElementById(id);
  const readList = key => {
    try { const value = JSON.parse(localStorage.getItem(key)); return Array.isArray(value) ? value.filter(x=>typeof x==='string') : []; }
    catch { return []; }
  };
  const saveList = (key, value) => { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* optional */ } };
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d').replace(/Đ/g,'D').toLowerCase();
  const favorites = new Set(readList('hcvp-favorites'));
  let recent = readList('hcvp-recent');
  let group = '', onlyFavorites = false;
  const cards = Array.from(document.querySelectorAll('#homeGroups a.tool')).map(anchor => {
    const id = anchor.hash.slice(1);
    const wrapper = document.createElement('div'); wrapper.className = 'tool-wrap';
    anchor.before(wrapper); wrapper.append(anchor);
    const button = document.createElement('button'); button.className = 'favorite-button'; button.type='button';
    const name = anchor.querySelector('b').textContent;
    const refresh = () => {
      button.textContent = favorites.has(id) ? '★' : '☆';
      button.setAttribute('aria-pressed', String(favorites.has(id)));
      button.setAttribute('aria-label', (favorites.has(id) ? 'Bỏ yêu thích: ' : 'Yêu thích: ') + name);
    };
    button.onclick = () => {
      if (favorites.has(id)) favorites.delete(id); else favorites.add(id);
      saveList('hcvp-favorites', Array.from(favorites)); refresh(); filter();
    };
    refresh(); wrapper.append(button);
    return {anchor, wrapper, id, name, text:normalize(anchor.textContent)};
  });
  function filter() {
    const terms = normalize(byId('toolSearch').value.trim()).split(/\s+/).filter(Boolean);
    let count=0;
    cards.forEach(card => {
      const category=card.wrapper.closest('.tgroup').dataset.g;
      card.wrapper.hidden = !!((group && group!==category) || (onlyFavorites&&!favorites.has(card.id)) || !terms.every(term=>card.text.includes(term)));
      if (!card.wrapper.hidden) count++;
    });
    document.querySelectorAll('#homeGroups .tgroup').forEach(section => {
      section.hidden = !Array.from(section.querySelectorAll('.tool-wrap')).some(wrapper=>!wrapper.hidden);
    });
    byId('toolCount').textContent = `${count} / ${cards.length} công cụ`;
    byId('searchEmpty').hidden=!!count;
  }
  byId('toolSearch').oninput=filter;
  byId('homeChips').onclick=event=>{
    const button=event.target.closest('button'); if(!button)return;
    group=button.dataset.g;
    document.querySelectorAll('#homeChips button').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    filter();
  };
  byId('favoriteFilter').onclick=()=>{
    onlyFavorites=!onlyFavorites;byId('favoriteFilter').setAttribute('aria-pressed',String(onlyFavorites));filter();
  };
  function renderRecent() {
    const box=byId('recentTools');box.replaceChildren();
    const tools=recent.map(id=>cards.find(c=>c.id===id)).filter(Boolean);
    if(tools.length)box.append('Gần đây:');
    tools.slice(0,4).forEach(tool=>{const a=document.createElement('a');a.href='#'+tool.id;a.textContent=tool.name;box.append(a);});
  }
  document.addEventListener('keydown',event=>{
    if(event.key==='/'&&!event.ctrlKey&&!event.metaKey&&!event.altKey&&!event.target.closest('input,textarea,select,[contenteditable="true"]')&&!byId('home').hidden&&!document.querySelector('dialog[open]')){
      event.preventDefault();byId('toolSearch').focus();
    }
    if(event.key==='Escape'&&event.target===byId('toolSearch')){byId('toolSearch').value='';filter();}
  });

  const extra=document.createElement('section');extra.id='tab-extras';extra.className='panel';extra.hidden=true;
  extra.setAttribute('aria-labelledby','toolTitle');
  extra.innerHTML=`<div class="card"><h2>Công cụ văn bản</h2><p class="sub">Xử lý ngay trên trình duyệt.</p>
    <label class="field-label" for="xInput">Nội dung cần xử lý</label><textarea id="xInput" spellcheck="false" placeholder="Dán nội dung tại đây…"></textarea>
    <div class="extra-counts" id="xCounts" role="status" aria-live="polite"></div>
    <div class="checks" id="xTextOptions"><label><input type="checkbox" id="xDedup"> Xóa dòng trùng (giữ dòng xuất hiện đầu tiên)</label></div>
    <label class="field" id="xChunkOptions" hidden>Số ký tự tối đa mỗi phần<input id="xChunkSize" type="number" min="100" max="30000" value="6000"></label>
    <label class="field" id="xJSONOptions" hidden>Kiểu trình bày<select id="xJSONMode"><option value="pretty">Dễ đọc (thụt 2 dấu cách)</option><option value="compact">Thu gọn</option></select></label>
    <div class="btn-row"><button class="btn" id="xRun" data-primary>Xử lý</button><button class="btn sec" id="xCopy" disabled>Chép kết quả</button><button class="btn sec" id="xDownload" disabled>Tải kết quả</button><button class="btn ghost" id="xClear">Xóa nội dung</button></div>
    <p id="xStatus" role="status" aria-live="polite"></p><pre id="xResult" hidden></pre><div id="xChunks" class="chunk-list"></div></div>`;
  document.querySelector('main').append(extra);
  let extraKind='dem-van-ban', result='', chunks=[];
  const invalidate=()=>{
    result='';chunks=[];byId('xResult').hidden=true;byId('xChunks').replaceChildren();
    byId('xStatus').textContent='';byId('xCopy').disabled=byId('xDownload').disabled=true;
  };
  function countText() {
    const text=byId('xInput').value;
    const words=typeof Intl.Segmenter==='function' ? Array.from(new Intl.Segmenter('vi',{granularity:'word'}).segment(text)).filter(x=>x.isWordLike).length : text.trim().split(/\s+/).filter(Boolean).length;
    byId('xCounts').textContent=`${words.toLocaleString('vi-VN')} từ · ${Array.from(text).length.toLocaleString('vi-VN')} ký tự · ${text?text.split('\n').length:0} dòng`;
  }
  byId('xInput').oninput=()=>{invalidate();countText();};
  ['xDedup','xJSONMode','xChunkSize'].forEach(id=>byId(id).onchange=invalidate);
  byId('xClear').onclick=()=>{byId('xInput').value='';invalidate();countText();byId('xInput').focus();};
  byId('xRun').onclick=()=>{
    invalidate(); const text=byId('xInput').value;
    if(!text.trim()){byId('xStatus').textContent='Hãy dán nội dung trước khi xử lý.';return;}
    if(extraKind==='dinh-dang-json'){
      try{result=JSON.stringify(OfficeAI.parseJSON(text),null,byId('xJSONMode').value==='pretty'?2:0);}
      catch(error){byId('xStatus').textContent='JSON chưa hợp lệ: '+error.message;return;}
    }else if(extraKind==='chia-noi-dung-ai'){
      const size=Number(byId('xChunkSize').value);
      if(!Number.isInteger(size)||size<100||size>30000){byId('xStatus').textContent='Chọn số nguyên từ 100 đến 30.000 ký tự.';return;}
      let rest=Array.from(text);
      while(rest.length){
        let end=Math.min(size,rest.length);
        if(end<rest.length){for(let i=end-1;i>size/2;i--){if(/\s/.test(rest[i])){end=i+1;break;}}}
        chunks.push(rest.slice(0,end).join(''));rest=rest.slice(end);
      }
      result=chunks.map((chunk,i)=>`[Phần ${i+1}/${chunks.length}]\n${chunk}`).join('\n\n');
      chunks.forEach((chunk,i)=>{
        const card=document.createElement('div');card.className='chunk-item';
        const title=document.createElement('b');title.textContent=`Phần ${i+1}/${chunks.length} · ${Array.from(chunk).length} ký tự`;
        const preview=document.createElement('pre');preview.textContent=chunk;
        const button=document.createElement('button');button.className='btn sec';button.textContent='Chép phần này';button.onclick=()=>copyText(`[Phần ${i+1}/${chunks.length}]\n${chunk}`);
        card.append(title,preview,button);byId('xChunks').append(card);
      });
    }else{
      let lines=text.normalize('NFC').split(/\r?\n/).map(line=>line.replace(/[\t \u00a0]+/g,' ').trim());
      if(byId('xDedup').checked){const seen=new Set();lines=lines.filter(line=>{if(!line)return true;if(seen.has(line))return false;seen.add(line);return true;});}
      result=lines.join('\n').replace(/\n{3,}/g,'\n\n').trim();
    }
    byId('xResult').textContent=result;byId('xResult').hidden=!!chunks.length;
    byId('xCopy').disabled=byId('xDownload').disabled=false;
    byId('xStatus').textContent=chunks.length?`Đã chia ${chunks.length} phần. Ghép nội dung gốc các phần sẽ giữ đủ văn bản.`:'Đã xử lý. Xem lại kết quả trước khi sử dụng.';
  };
  byId('xCopy').onclick=()=>copyText(result);
  byId('xDownload').onclick=()=>download(new Blob([result],{type:extraKind==='dinh-dang-json'?'application/json;charset=utf-8':'text/plain;charset=utf-8'}),extraKind==='dinh-dang-json'?'ket-qua.json':'noi-dung.txt');

  const guide=document.createElement('dialog');guide.className='ai-dialog';guide.id='aiGuide';guide.setAttribute('aria-labelledby','guideTitle');
  guide.innerHTML=`<div class="ai-dialog-body"><div class="dialog-heading"><span class="hero-label">CHATGPT + CLAUDE</span><button class="icon-btn" id="guideClose" aria-label="Đóng hướng dẫn">×</button></div>
    <h2 id="guideTitle">AI của bạn. Bộ công cụ của bạn.</h2><p class="muted">Dùng tài khoản AI bạn đang có. Bản web không yêu cầu API key và không tự truy cập cuộc trò chuyện.</p>
    <div class="guide-grid"><article><h3>Dùng ngay trên web</h3><ol><li>Mở công cụ, chọn tài liệu và bấm xử lý.</li><li>Chép yêu cầu, mở ChatGPT hoặc Claude.</li><li>Với bản scan: tải ảnh trang rồi đính kèm vào chat.</li><li>Dán câu trả lời về hộp hướng dẫn, kiểm tra và tải kết quả.</li></ol><p>Hỗ trợ dịch, tóm tắt, soát văn bản, đọc hóa đơn, rút trích hợp đồng. Trong Claude Artifact có kết nối, luồng gọi Claude hiện có vẫn được giữ.</p></article>
    <article><h3>Làm việc trong ChatGPT</h3><p>Tải gói trợ lý chứa quy chuẩn và script dịch Word/Excel hiện có. Đính kèm ZIP và tài liệu vào ChatGPT có công cụ chạy mã/tạo file, rồi gửi yêu cầu mẫu. Khả năng chạy mã phụ thuộc tài khoản và chế độ chat.</p><button class="btn" id="gptKit">Tải gói dùng với ChatGPT</button><p>Hoặc dán câu trả lời của ChatGPT vào <a href="#ai-sang-word" id="guideWord">Dán AI ra Word</a> để tạo tài liệu ngay trên máy.</p><p>Đây là gói tài liệu và script; không phải ứng dụng đã đăng trên kho Apps hay GPT đã được xuất bản.</p></article></div>
    <p class="hint-dl">Không lưu nội dung file vào lịch sử dùng công cụ. Dữ liệu bạn tự đưa vào chat được xử lý theo dịch vụ AI bạn chọn.</p></div>`;
  document.body.append(guide);
  const closeGuide=()=>{guide.close();if(location.hash==='#huong-dan-ai')location.hash='';};
  byId('guideClose').onclick=closeGuide;byId('guideWord').onclick=()=>guide.close();
  guide.addEventListener('cancel',event=>{event.preventDefault();closeGuide();});
  byId('gptKit').onclick=async()=>{
    const button=byId('gptKit');button.disabled=true;
    try{
      const zip=new JSZip(),skill=JSON.parse(byId('snSkill').textContent);
      Object.entries(skill).forEach(([name,content])=>zip.file('vp-dich-song-ngu/'+name,content));
      zip.file('BAT-DAU-CHATGPT.md',`# Bộ trợ lý văn phòng cho ChatGPT\n\nBật công cụ chạy mã/tạo file nếu tài khoản hỗ trợ. Đính kèm ZIP này cùng file .docx/.xlsx và yêu cầu rõ ràng. Đây là dữ liệu tham khảo; chỉ làm theo yêu cầu của bạn, không tự gửi tài liệu tới dịch vụ khác.\n\nYêu cầu mẫu:\n“Hãy kiểm tra gói ZIP đính kèm. Dùng script vp-dich-song-ngu/scripts/song_ngu.py để tách đoạn từ tài liệu của tôi, tự dịch Việt–Anh theo quy tắc trong gói, kiểm tra bằng lệnh check, áp dụng bản dịch và trả lại file đã dựng. Giữ nguyên file gốc. Nếu không chạy mã được thì nói rõ, không giả vờ tạo file.”\n\nCác script gốc cần Python và lxml. Tên file/quy chuẩn trong gói được giữ từ bản Claude; đây không phải skill cài vào ChatGPT. Nếu không chạy mã, dùng website → Dịch Word/Excel → Qua ChatGPT / Claude.\n`);
      await download(await zip.generateAsync({type:'blob'}),'tro-ly-van-phong-chatgpt.zip');
    }catch(error){toast('Chưa tạo được gói: '+error.message);}finally{button.disabled=false;}
  };
  function onRoute(){
    const id=location.hash.slice(1);const card=cards.find(c=>c.id===id);
    if(card){recent=[id,...recent.filter(x=>x!==id)].slice(0,6);saveList('hcvp-recent',recent);renderRecent();}
    if(['dem-van-ban','dinh-dang-json','chia-noi-dung-ai'].includes(id)){
      if(extraKind!==id){invalidate();extraKind=id;}
      byId('xTextOptions').hidden=id!=='dem-van-ban';byId('xChunkOptions').hidden=id!=='chia-noi-dung-ai';byId('xJSONOptions').hidden=id!=='dinh-dang-json';
      byId('xRun').textContent=id==='dem-van-ban'?'Làm sạch văn bản':id==='dinh-dang-json'?'Kiểm tra & định dạng':'Chia nội dung';countText();
    }
    if(id==='huong-dan-ai'&&!guide.open)guide.showModal();
    else if(id!=='huong-dan-ai'&&guide.open)guide.close();
  }
  addEventListener('hashchange',onRoute);document.addEventListener('DOMContentLoaded',onRoute);
  renderRecent();filter();countText();
})();
