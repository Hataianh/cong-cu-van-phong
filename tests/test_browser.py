"""Functional browser regression checks; AI responses are fixtures, not live model calls."""
import base64
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import shutil
import threading
import unittest
import zipfile
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
LOCKED_TOOLS = {
    'song-ngu','dich-pdf','soat-van-ban','rut-hop-dong','tom-tat-pdf',
    'hoa-don-xml','hoa-don-scan','soat-khau-tru-thue','doi-chieu-112','bien-ban-cong-no',
}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def word_fixture():
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w') as z:
        z.writestr('[Content_Types].xml', '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>''')
        z.writestr('_rels/.rels', '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>''')
        z.writestr('word/document.xml', '''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Hợp đồng dịch vụ</w:t></w:r></w:p><w:p><w:r><w:t>Thanh toán vào ngày 15 tháng 11 năm 2026.</w:t></w:r></w:p><w:sectPr/></w:body></w:document>''')
    return {'name':'hop-dong.docx', 'mimeType':'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'buffer':data.getvalue()}


def word_text_fixture(text):
    fixture=word_fixture();output=io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(fixture['buffer'])) as source,zipfile.ZipFile(output,'w') as target:
        for name in source.namelist():
            data=source.read(name)
            if name=='word/document.xml':
                data=f'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>{escape(text)}</w:t></w:r></w:p><w:sectPr/></w:body></w:document>'.encode()
            target.writestr(name,data)
    fixture['buffer']=output.getvalue()
    return fixture


class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1',0), partial(QuietHandler,directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}/'
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path=shutil.which('chromium'), headless=True, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop();cls.server.shutdown();cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context(accept_downloads=True)
        self.page = self.context.new_page()
        self.errors=[];self.external=[]
        self.page.on('pageerror', lambda e:self.errors.append(str(e)))
        # Normal workflows must work even without CDNs.
        def route(request):
            if not request.request.url.startswith(self.base):
                self.external.append(request.request.url);request.abort()
            else:
                request.continue_()
        self.page.route('https://**/*',route)
        self.page.goto(self.base,wait_until='networkidle')

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors,[], 'Browser runtime errors')

    def go(self, tool):
        self.page.evaluate('(id)=>location.hash=id',tool)
        expect(self.page.locator('#toolHead')).to_be_visible()

    def load_full_version(self):
        # Exercise the private/full build in the test response only. The
        # production document remains the trial; no URL parameter unlocks it.
        original=(ROOT/'index.html').read_text()
        self.assertEqual(original.count('window.__MOI=true;'),1)
        full=original.replace('window.__MOI=true;','window.__MOI=false;',1)
        def serve_full(route):
            route.fulfill(status=200,content_type='text/html; charset=utf-8',body=full)
        self.page.route(self.base,serve_full)
        self.page.reload(wait_until='networkidle')
        self.page.unroute(self.base,serve_full)
        expect(self.page.locator('#trialInfo')).to_be_hidden()

    def downloaded(self, selector):
        with self.page.expect_download() as event:
            self.page.locator(selector).click()
        download=event.value
        self.assertIsNone(download.failure())
        return Path(download.path()).read_bytes()

    def read_xlsx(self, data):
        return self.page.evaluate('''data=>{const w=XLSX.read(Uint8Array.from(data),{type:'array'});return {sheets:w.SheetNames,rows:XLSX.utils.sheet_to_json(w.Sheets[w.SheetNames[0]],{header:1,raw:true})};}''',list(data))

    def test_all_routes_and_legacy_links(self):
        ids=self.page.locator('#homeGroups a.tool').evaluate_all('(links)=>links.map(a=>a.hash.slice(1))')
        self.assertEqual(len(ids),43)
        tagged=set(self.page.locator('#homeGroups a.pro-locked').evaluate_all('(links)=>links.map(a=>a.hash.slice(1))'))
        self.assertEqual(tagged,LOCKED_TOOLS)
        for tool in ids:
            self.go(tool)
            expect(self.page.locator('main > .panel:visible')).to_have_count(1)
            if tool in LOCKED_TOOLS:
                expect(self.page.locator('#proLock')).to_be_visible()
                expect(self.page.locator('main > .panel:not(#proLock):visible')).to_have_count(0)
            else:
                expect(self.page.locator('#proLock')).to_be_hidden()
        self.go('word');expect(self.page.locator('#tab-word')).to_be_visible()
        self.page.evaluate("location.hash='%E0%A4%A'")
        expect(self.page.locator('#home')).to_be_visible()
        self.assertEqual(self.external,[])

    def test_search_filters_favorites_recent_theme(self):
        self.page.locator('#toolSearch').fill('hoa don xml')
        expect(self.page.locator('.tool-wrap:visible')).to_have_count(2)
        self.page.locator('.tool-wrap').filter(has=self.page.locator('a[href="#hoa-don-xml"]')).locator('.favorite-button').click()
        self.page.locator('#toolSearch').fill('')
        self.page.locator('#favoriteFilter').click()
        expect(self.page.locator('.tool-wrap:visible')).to_have_count(1)
        self.page.locator('.tool-wrap:visible a.tool').click()
        expect(self.page.locator('#toolTitle')).to_have_text('Hóa đơn XML ra bảng kê')
        self.page.evaluate("location.hash=''")
        expect(self.page.locator('#recentTools')).to_contain_text('Hóa đơn XML')
        self.page.locator('#themeBtn').click()
        self.assertIn(self.page.locator('html').get_attribute('data-theme'),['dark','light'])
        self.page.reload(wait_until='networkidle')
        self.page.locator('#favoriteFilter').click()
        expect(self.page.locator('.tool-wrap:visible')).to_have_count(1)

    def test_word_export_and_html_escaping(self):
        self.go('ai-sang-word')
        self.page.locator('#wIn').fill('# BÁO CÁO\n\n## Nội dung\nXin chào **Việt Nam**\n\n| Mục | Số |\n|---|---|\n| A | 12 |\n\n<img src=x onerror=alert(1)>')
        self.page.locator('#wGo').click()
        expect(self.page.locator('#wPrev')).to_contain_text('Việt Nam')
        expect(self.page.locator('#wPrev table')).to_have_count(1)
        expect(self.page.locator('#wPrev img')).to_have_count(0)
        data=self.downloaded('#wDoc')
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            self.assertIn('word/document.xml',z.namelist())
            self.assertTrue(any(b'Vi' in z.read(n) for n in z.namelist() if n.endswith('.mht')))

    def test_clean_excel_real_output(self):
        self.go('lam-sach-excel')
        content='Họ tên,Số điện thoại,Số tiền\n nguyễn   văn an ,901234567,500k\n nguyễn   văn an ,901234567,500k\n'
        self.page.locator('#cFile').set_input_files({'name':'danh-sach.csv','mimeType':'text/csv','buffer':content.encode('utf-8-sig')})
        expect(self.page.locator('#cConfig')).to_be_visible()
        self.page.locator('#cGo').click()
        data=self.read_xlsx(self.downloaded('#cDl'))
        self.assertEqual(len(data['rows']),2)
        self.assertIn('Nguyễn Văn An',data['rows'][1])
        self.assertIn('0901234567',data['rows'][1])
        self.assertIn(500000,data['rows'][1])

    def test_trial_file_picker_caps_merge_at_three(self):
        self.go('gop-excel')
        files=[{'name':f'{i}.csv','mimeType':'text/csv','buffer':f'Ma,So luong\nA{i},{i}\n'.encode()} for i in range(1,5)]
        self.page.locator('#mFile').set_input_files(files)
        expect(self.page.locator('#toast')).to_contain_text('Chỉ nhận 3 file đầu tiên')
        self.page.locator('#mGo').click()
        data=self.read_xlsx(self.downloaded('#mDl'))
        self.assertEqual(len(data['rows']),4)
        self.assertEqual([row[0] for row in data['rows'][1:]],['A1','A2','A3'])

    def test_full_version_accepts_four_files(self):
        self.load_full_version();self.go('gop-excel')
        files=[{'name':f'{i}.csv','mimeType':'text/csv','buffer':f'Ma,So luong\nA{i},{i}\n'.encode()} for i in range(1,5)]
        self.page.locator('#mFile').set_input_files(files)
        self.page.locator('#mGo').click()
        data=self.read_xlsx(self.downloaded('#mDl'))
        self.assertEqual(len(data['rows']),5)

    def test_trial_drag_and_drop_caps_merge_at_three(self):
        self.go('gop-excel')
        self.page.locator('#mDrop').evaluate('''drop=>{const transfer=new DataTransfer();for(let i=1;i<=4;i++)transfer.items.add(new File([`Ma,So luong\nA${i},${i}\n`],`${i}.csv`,{type:'text/csv'}));drop.dispatchEvent(new DragEvent('drop',{dataTransfer:transfer,bubbles:true,cancelable:true}));}''')
        expect(self.page.locator('#toast')).to_contain_text('Chỉ nhận 3 file đầu tiên')
        self.page.locator('#mGo').click()
        self.assertEqual(len(self.read_xlsx(self.downloaded('#mDl'))['rows']),4)

    def test_bilingual_roundtrip_manual_chatgpt(self):
        self.load_full_version()
        self.go('song-ngu');self.page.locator('#bFile').set_input_files(word_fixture())
        expect(self.page.locator('#bModes')).to_be_visible()
        self.page.locator('#bGo').click()
        expect(self.page.locator('.ai-dialog[open]')).to_be_visible()
        prompt=self.page.locator('#aiPrompt').input_value()
        self.assertIn('Hợp đồng dịch vụ',prompt)
        self.page.locator('#aiAnswer').fill('{bad json')
        self.page.locator('#aiAccept').click()
        expect(self.page.locator('#aiValidation')).to_contain_text('JSON chưa hợp lệ')
        self.page.locator('#aiAnswer').fill('```json\n'+json.dumps({'p':1,'t':{'1':'Service agreement','2':'Payment on 15 November 2026.'},'terms':{}})+'\n```')
        self.page.locator('#aiAccept').click()
        expect(self.page.locator('#bRows textarea')).to_have_count(2)
        self.page.locator('#bBuild').click()
        data=self.downloaded('#bDl')
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            xml=z.read('word/document.xml').decode()
            self.assertIn('Service agreement',xml);self.assertIn('Hợp đồng dịch vụ',xml)
            self.assertIn('w:b',xml)

    def test_summary_from_word_and_export(self):
        self.load_full_version()
        self.go('tom-tat-pdf');self.page.locator('#qFile').set_input_files(word_fixture())
        expect(self.page.locator('#qGo')).to_be_enabled();self.page.locator('#qGo').click()
        expect(self.page.locator('#aiPrompt')).to_be_visible()
        self.page.locator('#aiAnswer').fill('## Tóm tắt\nHợp đồng dịch vụ, thanh toán ngày 15/11/2026.')
        self.page.locator('#aiAccept').click()
        expect(self.page.locator('#qRes')).to_contain_text('15/11/2026')
        with zipfile.ZipFile(io.BytesIO(self.downloaded('#qDl'))) as z:
            self.assertIn('15/11/2026',z.read('word/document.xml').decode())

    def test_manual_cancel_and_scan_attachment(self):
        self.page.evaluate('''()=>{window.aiOutcome='pending';OfficeAI.getSample().then(s=>s.json('Đọc hóa đơn',{images:[new Blob(['image'],{type:'image/jpeg'})]})).then(v=>window.aiOutcome=v).catch(e=>window.aiOutcome=e.code);}''')
        expect(self.page.locator('#aiImages')).to_be_visible()
        self.assertEqual(self.downloaded('#aiImageLinks a'),b'image')
        self.page.locator('#aiAnswer').fill('null');self.page.locator('#aiAccept').click()
        expect(self.page.locator('#aiValidation')).to_contain_text('Cần một đối tượng')
        self.page.keyboard.press('Escape')
        self.page.wait_for_function("window.aiOutcome==='cancelled'")

    def test_abort_signal_closes_pending_handoff(self):
        self.page.evaluate("()=>{window.controller=new AbortController();window.aiOutcome='pending';OfficeAI.getSample().then(s=>s('test',{signal:controller.signal})).catch(e=>window.aiOutcome=e.code);}")
        expect(self.page.locator('#aiPrompt')).to_be_visible()
        self.page.evaluate('controller.abort()')
        self.page.wait_for_function("window.aiOutcome==='cancelled'")
        expect(self.page.locator('dialog[open]')).to_have_count(0)

    def test_scan_invoice_to_excel_formulas(self):
        self.load_full_version()
        image=self.page.evaluate("()=>{const c=document.createElement('canvas');c.width=200;c.height=200;c.getContext('2d').fillText('Invoice',20,20);return c.toDataURL('image/png').split(',')[1];}")
        self.go('hoa-don-scan')
        self.page.locator('#qFile').set_input_files({'name':'invoice.png','mimeType':'image/png','buffer':base64.b64decode(image)})
        expect(self.page.locator('#qGo')).to_be_enabled();self.page.locator('#qGo').click()
        expect(self.page.locator('#aiImages')).to_be_visible()
        self.page.locator('#aiAnswer').fill(json.dumps({'invoices':[{'so':'00012','mst_ban':'0123456789','ten_ban':'Công ty A','ngay':'10/11/2026','tien_truoc_thue':100000,'thue':10000,'tong':110000}]}))
        self.page.locator('#aiAccept').click()
        expect(self.page.locator('#qRes')).to_contain_text('00012')
        data=self.downloaded('#qDl')
        # Formula cells without cached values may be omitted by SheetJS's
        # reader. Inspect actual OOXML rather than treating that as lost data.
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            sheets=''.join(z.read(n).decode() for n in z.namelist() if n.startswith('xl/worksheets/') and n.endswith('.xml'))
            self.assertIn('SUBTOTAL(9,I2:I2)',sheets)
            self.assertIn('I2+J2-K2',sheets)
        self.assertEqual(self.page.evaluate("data=>XLSX.read(Uint8Array.from(data),{type:'array'}).Sheets['Bang ke hoa don'].C2.v",list(data)),'00012')

    def test_image_zip_preserves_duplicate_names(self):
        image=self.page.evaluate("()=>{const c=document.createElement('canvas');c.width=10;c.height=10;c.getContext('2d').fillRect(0,0,10,10);return c.toDataURL('image/png').split(',')[1];}")
        self.go('nen-anh')
        self.page.locator('#gFile').set_input_files([{'name':'same.png','mimeType':'image/png','buffer':base64.b64decode(image)} for _ in range(3)])
        with zipfile.ZipFile(io.BytesIO(self.downloaded('#gGo'))) as z:
            self.assertEqual(len(z.namelist()),3)

    def test_native_claude_preserved(self):
        self.page.add_init_script('''window.claude={use:async name=>name==='sample'?Object.assign(async()=>({text:'native works'}),{limits:async()=>({})}):null};''')
        self.page.reload(wait_until='networkidle')
        result=self.page.evaluate("async()=>{const s=await OfficeAI.getSample();return (await s('test')).text;}")
        self.assertEqual(result,'native works')

    def test_pdf_merge_and_download(self):
        self.page.add_script_tag(url=self.base+'vendor/pdf-lib.min.js')
        data=self.page.evaluate('''async()=>{const d=await PDFLib.PDFDocument.create();d.addPage().drawText('Office smoke test');return Array.from(await d.save());}''')
        self.go('gop-pdf')
        self.page.locator('#pFile').set_input_files([{'name':f'{i}.pdf','mimeType':'application/pdf','buffer':bytes(data)} for i in range(2)])
        expect(self.page.locator('#pGrid .pg')).to_have_count(2)
        output=self.downloaded('#pSave')
        count=self.page.evaluate('async data=>(await PDFLib.PDFDocument.load(Uint8Array.from(data))).getPageCount()',list(output))
        self.assertEqual(count,2);self.assertEqual(self.external,[])

    def test_image_resize_real_dimensions(self):
        img=self.page.evaluate("()=>{const c=document.createElement('canvas');c.width=120;c.height=80;c.getContext('2d').fillRect(0,0,120,80);return c.toDataURL('image/png').split(',')[1];}")
        self.go('doi-co-anh');self.page.locator('#gFile').set_input_files({'name':'anh.png','mimeType':'image/png','buffer':base64.b64decode(img)})
        self.page.locator('#gResizeOn').check();self.page.locator('#gMax').fill('60')
        output=self.downloaded('#gGo')
        size=self.page.evaluate('''async data=>{const image=await createImageBitmap(new Blob([Uint8Array.from(data)]));return [image.width,image.height];}''',list(output))
        self.assertEqual(size,[60,40])

    def test_word_to_pdf_vietnamese_and_arrow_glyphs(self):
        text='Hiểu ý & lập kế hoạch · Gọi công cụ (tool-use) · Tổng hợp câu trả lời kèm trích nguồn (prompt caching giảm chi phí). → Gọi công cụ / nhận kết quả đã lọc. ← ↔'
        self.page.add_script_tag(url=self.base+'vendor/fontkit.umd.min.js')
        missing=self.page.evaluate('''()=>{const fonts=JSON.parse(document.getElementById('pdfFonts').textContent);return Object.values(fonts).flatMap(base64=>{const font=fontkit.create(Uint8Array.from(atob(base64),c=>c.charCodeAt(0)));return [...'→←↔ấệ'].filter(char=>font.glyphForCodePoint(char.codePointAt(0)).id===0);});}''')
        self.assertEqual(missing,[],'Symbols must have real outlines, not glyph 0/tofu')
        self.go('word-sang-pdf');self.page.locator('#oFile').set_input_files(word_text_fixture(text))
        data=self.downloaded('#oGo')
        self.page.add_script_tag(url=self.base+'vendor/pdf.min.js')
        extracted=self.page.evaluate('''async bytes=>{pdfjsLib.GlobalWorkerOptions.workerSrc='vendor/pdf.worker.min.js';const doc=await pdfjsLib.getDocument({data:Uint8Array.from(bytes),isEvalSupported:false}).promise;const page=await doc.getPage(1);const result=(await page.getTextContent()).items.map(item=>item.str).join(' ');await doc.destroy();return result;}''',list(data))
        self.assertEqual(' '.join(extracted.split()),' '.join(text.split()))

    def test_pdf_to_word_preserves_ruled_cells_and_bold_headings(self):
        self.page.add_script_tag(url=self.base+'vendor/pdf-lib.min.js')
        data=self.page.evaluate('''async()=>{
            const doc=await PDFLib.PDFDocument.create(),regular=await doc.embedFont(PDFLib.StandardFonts.TimesRoman),bold=await doc.embedFont(PDFLib.StandardFonts.TimesRomanBold);
            const makePage=(continued)=>{
              const page=doc.addPage([595,842]);
              page.drawText(continued?'Continued report':'Report heading',{x:50,y:790,size:14,font:bold});
              const xs=[50,220,545],ys=[750,715,665,630];
              for(const x of xs)page.drawLine({start:{x,y:ys[0]},end:{x,y:ys.at(-1)},thickness:0.5});
              for(const y of ys)page.drawLine({start:{x:xs[0],y},end:{x:xs.at(-1),y},thickness:0.5});
              const rows=continued?[['A2','Second page value'],['A3',''],['A4','42']]:[['Code','Description'],['A1','First line'],['','0']];
              rows.forEach((row,i)=>row.forEach((text,j)=>{if(text)page.drawText(text,{x:xs[j]+5,y:ys[i]-15,size:10,font:!continued&&i===0?bold:regular});}));
              if(!continued)page.drawText('Second line',{x:225,y:685,size:10,font:regular});
              page.drawText('After table paragraph.',{x:50,y:590,size:12,font:regular});
            };
            makePage(false);makePage(true);return Array.from(await doc.save());
        }''')
        self.go('pdf-sang-word')
        self.page.locator('#qFile').set_input_files({'name':'ruled-tables.pdf','mimeType':'application/pdf','buffer':bytes(data)})
        self.page.locator('#qHow').select_option('text');self.page.locator('#qGo').click()
        expect(self.page.locator('#qRes table')).to_have_count(2)
        with zipfile.ZipFile(io.BytesIO(self.downloaded('#qDl'))) as z:
            root=ET.fromstring(z.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        tables=root.findall('.//w:tbl',ns);self.assertEqual(len(tables),2)
        def text(node):return ''.join(node.itertext())
        rows=[[text(c) for c in row.findall('w:tc',ns)] for row in tables[0].findall('w:tr',ns)]
        self.assertEqual(rows,[['Code','Description'],['A1','First lineSecond line'],['','0']])
        columns=[int(col.attrib['{'+ns['w']+'}w']) for col in tables[0].findall('w:tblGrid/w:gridCol',ns)]
        self.assertGreater(columns[1],columns[0])
        self.assertEqual(len(tables[0].findall('.//w:tblHeader',ns)),1)
        self.assertEqual(len(tables[1].findall('.//w:tblHeader',ns)),0,'Continuation data must not become a header')
        self.assertTrue(any(text(p)=='Report heading' and p.find('.//w:b',ns) is not None for p in root.findall('.//w:p',ns)))
        self.assertIn('After table paragraph.',text(root))
        for paragraph in root.findall('.//w:p',ns):
            if text(paragraph)=='After table paragraph.':
                self.assertIsNone(paragraph.find('w:pPr/w:pStyle',ns),'Smaller table fonts must not turn body prose into headings')

    def test_new_tools_data_integrity_and_stale_output(self):
        self.go('dem-van-ban');self.page.locator('#xInput').fill('  Xin   chào  \nXin chào\n');self.page.locator('#xDedup').check();self.page.locator('#xRun').click()
        expect(self.page.locator('#xResult')).to_have_text('Xin chào')
        self.go('dinh-dang-json');self.page.locator('#xInput').fill('```json\n{"name":"Việt Nam","id":"0012"}\n```');self.page.locator('#xRun').click()
        self.assertEqual(json.loads(self.downloaded('#xDownload')),{'name':'Việt Nam','id':'0012'})
        self.page.locator('#xInput').fill('{invalid');expect(self.page.locator('#xDownload')).to_be_disabled();self.page.locator('#xRun').click();expect(self.page.locator('#xStatus')).to_contain_text('JSON chưa hợp lệ')
        self.go('chia-noi-dung-ai');text='Tiếng Việt 😀\n'*40
        self.page.locator('#xInput').fill(text);self.page.locator('#xChunkSize').fill('100');self.page.locator('#xRun').click()
        parts=self.page.locator('.chunk-item pre').all_text_contents()
        self.assertEqual(''.join(parts),text);self.assertTrue(all(len(p)<=100 for p in parts))

    def test_chatgpt_kit_contains_original_scripts(self):
        self.load_full_version()
        self.page.locator('a[href="#huong-dan-ai"]').first.click()
        data=self.downloaded('#gptKit')
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            self.assertIn('BAT-DAU-CHATGPT.md',z.namelist())
            self.assertIn('vp-dich-song-ngu/scripts/song_ngu.py',z.namelist())
            compile(z.read('vp-dich-song-ngu/scripts/song_ngu.py'),'song_ngu.py','exec')

    def test_trial_chatgpt_guide_cannot_download_translation_kit(self):
        downloads=[]
        self.page.on('download',lambda item:downloads.append(item.suggested_filename))
        self.page.locator('a[href="#huong-dan-ai"]').first.click()
        expect(self.page.locator('#gptKit')).to_have_text('Xem tính năng Pro')
        self.page.locator('#gptKit').click()
        expect(self.page.locator('#proLock')).to_be_visible()
        expect(self.page.locator('#tab-bilingual')).to_be_hidden()
        expect(self.page.locator('dialog[open]')).to_have_count(0)
        self.assertEqual(downloads,[])

    def test_locked_deep_links_after_reload_and_legacy_link(self):
        for tool in sorted(LOCKED_TOOLS | {'hoa-don'}):
            self.page.goto(self.base+'#'+tool,wait_until='networkidle')
            self.page.reload(wait_until='networkidle')
            expect(self.page.locator('#proLock')).to_be_visible()
            expect(self.page.locator('main > .panel:not(#proLock):visible')).to_have_count(0)
            expect(self.page.locator('#proLock a[href*="xxxxxx"]')).to_have_count(0)
            self.page.keyboard.press('Control+Enter')
            expect(self.page.locator('dialog[open]')).to_have_count(0)

    def test_trial_chatgpt_pdf_to_word_still_works(self):
        image=self.page.evaluate("()=>{const c=document.createElement('canvas');c.width=100;c.height=100;c.getContext('2d').fillText('Hello',20,20);return c.toDataURL('image/png').split(',')[1];}")
        self.go('pdf-sang-word')
        self.page.locator('#qFile').set_input_files({'name':'scan.png','mimeType':'image/png','buffer':base64.b64decode(image)})
        self.page.locator('#qGo').click()
        expect(self.page.locator('#aiImages')).to_be_visible()
        self.page.locator('#aiAnswer').fill('## Văn bản thử\nĐọc bản scan bằng ChatGPT.')
        self.page.locator('#aiAccept').click()
        expect(self.page.locator('#qRes')).to_contain_text('Đọc bản scan bằng ChatGPT.')
        with zipfile.ZipFile(io.BytesIO(self.downloaded('#qDl'))) as z:
            self.assertIn('Đọc bản scan bằng ChatGPT.',z.read('word/document.xml').decode())

    def test_mobile_layout_and_keyboard(self):
        for width in [375,768,1440]:
            self.page.set_viewport_size({'width':width,'height':900})
            self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),width)
        self.page.keyboard.press('/')
        expect(self.page.locator('#toolSearch')).to_be_focused()


if __name__ == '__main__':
    unittest.main(verbosity=2)
