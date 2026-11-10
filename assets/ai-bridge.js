/* Manual AI handoff: document content never leaves this page automatically. */
(() => {
  'use strict';
  let nativeSample;
  let active = false;
  const readPreference = () => {
    try { return localStorage.getItem('hcvp-ai-provider') === 'claude' ? 'claude' : 'chatgpt'; }
    catch { return 'chatgpt'; }
  };
  function parseJSON(text) {
    const clean = text.trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '');
    return JSON.parse(clean);
  }
  function handoff(input, options = {}, json = false) {
    return new Promise((resolve, reject) => {
      if (active) { reject({code:'queue_overflow'}); return; }
      if (options.signal?.aborted) { reject({code:'cancelled'}); return; }
      active = true;
      const dialog = document.createElement('dialog');
      dialog.className = 'ai-dialog';
      dialog.setAttribute('aria-labelledby', 'aiDialogTitle');
      dialog.innerHTML = `<form method="dialog" class="ai-dialog-body">
        <div class="dialog-heading"><span class="hero-label">BƯỚC CHUYỂN SANG AI</span><button class="icon-btn" value="cancel" aria-label="Đóng">×</button></div>
        <h2 id="aiDialogTitle">Dùng AI của bạn, theo cách bạn chọn</h2>
        <p class="muted">Trang chưa gửi nội dung đi đâu. Chỉ nội dung bạn chép hoặc ảnh bạn đính kèm mới được đưa vào chat AI.</p>
        <label class="field">Nơi nhận yêu cầu<select id="aiProvider"><option value="chatgpt">ChatGPT</option><option value="claude">Claude</option></select></label>
        <h3>1. Chép yêu cầu sang chat AI</h3>
        <label class="vh" for="aiPrompt">Yêu cầu gửi AI</label><textarea id="aiPrompt" readonly spellcheck="false"></textarea>
        <div class="btn-row"><button type="button" class="btn" id="aiCopy">Chép yêu cầu</button><a class="btn sec" id="aiOpen" target="_blank" rel="noopener noreferrer">Mở ChatGPT ↗</a></div>
        <div id="aiImages" hidden><p>Yêu cầu này có ảnh trang. Tải từng ảnh rồi đính kèm <b>cùng yêu cầu</b> vào chat AI.</p><div class="btn-row" id="aiImageLinks"></div></div>
        <h3>2. Dán toàn bộ câu trả lời về đây</h3>
        <label class="vh" for="aiAnswer">Câu trả lời từ AI</label><textarea id="aiAnswer" placeholder="Dán câu trả lời của AI…" spellcheck="false"></textarea>
        <p id="aiValidation" role="status" aria-live="polite"></p>
        <div class="btn-row"><button type="button" class="btn" id="aiAccept">Nhận kết quả & tiếp tục</button><button class="btn sec" value="cancel">Dừng</button></div>
        <p class="hint-dl">Có thể có nhiều phần. Dữ liệu chỉ giữ trong bộ nhớ của trang; tải kết quả trước khi đóng hoặc làm mới.</p>
      </form>`;
      const q = selector => dialog.querySelector(selector);
      const prompt = String(input) + (json ? '\n\nChỉ trả về JSON hợp lệ theo cấu trúc đã yêu cầu. Không thêm giải thích.' : '');
      q('#aiPrompt').value = prompt;
      q('#aiProvider').value = readPreference();
      const providerChanged = () => {
        const provider = q('#aiProvider').value;
        const link = q('#aiOpen');
        link.href = provider === 'claude' ? 'https://claude.ai/new' : 'https://chatgpt.com/';
        link.textContent = provider === 'claude' ? 'Mở Claude ↗' : 'Mở ChatGPT ↗';
        try { localStorage.setItem('hcvp-ai-provider', provider); } catch { /* optional preference */ }
      };
      q('#aiProvider').onchange = providerChanged;
      providerChanged();
      q('#aiCopy').onclick = async () => {
        try { await navigator.clipboard.writeText(prompt); q('#aiValidation').textContent = 'Đã chép. Dán vào chat AI rồi quay lại đây.'; }
        catch { q('#aiPrompt').focus(); q('#aiPrompt').select(); q('#aiValidation').textContent = 'Nhấn Ctrl+C / Cmd+C để chép phần đã chọn.'; }
      };
      const urls = [];
      (options.images || []).forEach((image, i) => {
        // Existing PDF/scan engines supply Blob objects, not remote image URLs.
        if (!(image instanceof Blob)) return;
        const url = URL.createObjectURL(image); urls.push(url);
        const link = document.createElement('a');
        link.className = 'btn sec'; link.href = url;
        link.download = `trang-ai-${i+1}.${image.type === 'image/png' ? 'png' : 'jpg'}`;
        link.textContent = `Tải ảnh ${i+1}`;
        q('#aiImageLinks').append(link); q('#aiImages').hidden = false;
      });
      let finished = false;
      const previousFocus = document.activeElement;
      const finish = (result, error) => {
        if (finished) return;
        finished = true; active = false;
        options.signal?.removeEventListener('abort', abort);
        dialog.close(); dialog.remove(); urls.forEach(url => URL.revokeObjectURL(url));
        previousFocus?.focus({preventScroll:true});
        if (error) reject(error); else resolve(result);
      };
      const abort = () => finish(null, {code:'cancelled'});
      dialog.addEventListener('close', () => { if (!finished) abort(); });
      dialog.addEventListener('cancel', event => { event.preventDefault(); abort(); });
      q('#aiAccept').onclick = () => {
        const text = q('#aiAnswer').value.trim();
        if (!text) { q('#aiValidation').textContent = 'Bạn chưa dán câu trả lời.'; q('#aiAnswer').focus(); return; }
        let result;
        try { result = json ? parseJSON(text) : {text}; }
        catch (error) { q('#aiValidation').textContent = 'JSON chưa hợp lệ. Chép đủ khối JSON hoặc nhờ AI sửa định dạng. ' + error.message; return; }
        if (json && (!result || typeof result !== 'object')) {
          q('#aiValidation').textContent = 'Cần một đối tượng hoặc mảng JSON theo yêu cầu, không phải giá trị đơn.'; return;
        }
        if (!json) options.onText?.({text});
        finish(result);
      };
      options.signal?.addEventListener('abort', abort, {once:true});
      document.body.append(dialog); dialog.showModal();
      q('#aiCopy').focus();
    });
  }
  const sample = (input, options) => handoff(input, options, false);
  sample.json = (input, options) => handoff(input, options, true);
  sample.manual = true;
  sample.limits = async () => ({maxPromptBytes:32000, images:{maxInputBytes:8*1024*1024}});
  window.OfficeAI = {
    async getSample() {
      if (window.claude && typeof window.claude.use === 'function') {
        if (nativeSample === undefined) nativeSample = Promise.resolve().then(() => window.claude.use('sample')).catch(() => null);
        const connected = await nativeSample;
        if (connected) return connected;
      }
      return sample;
    },
    parseJSON,
  };
})();
