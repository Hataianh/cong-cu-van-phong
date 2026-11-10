/* Recover simple ruled tables from PDF paths, before joining text into paragraphs. */
(() => {
  'use strict';
  const EPS=1.5;
  function strokeSegments(list,OPS){
    const result=[],stack=[];let matrix=[1,0,0,1,0,0],path=[],point=null,start=null;
    const transform=(x,y)=>({x:matrix[0]*x+matrix[2]*y+matrix[4],y:matrix[1]*x+matrix[3]*y+matrix[5]});
    const line=(a,b)=>{
      if(!a||!b)return;
      if(Math.abs(a.y-b.y)<EPS&&Math.abs(a.x-b.x)>4)path.push({axis:'h',at:(a.y+b.y)/2,lo:Math.min(a.x,b.x),hi:Math.max(a.x,b.x)});
      else if(Math.abs(a.x-b.x)<EPS&&Math.abs(a.y-b.y)>4)path.push({axis:'v',at:(a.x+b.x)/2,lo:Math.min(a.y,b.y),hi:Math.max(a.y,b.y)});
    };
    for(let i=0;i<list.fnArray.length;i++){
      const op=list.fnArray[i],args=list.argsArray[i];
      if(op===OPS.save)stack.push(matrix.slice());
      else if(op===OPS.restore)matrix=stack.pop()||[1,0,0,1,0,0];
      else if(op===OPS.transform){const [a,b,c,d,e,f]=matrix,[A,B,C,D,E,F]=args;matrix=[a*A+c*B,b*A+d*B,a*C+c*D,b*C+d*D,a*E+c*F+e,b*E+d*F+f];}
      else if(op===OPS.constructPath){
        const [operations,coordinates]=args;let at=0;
        for(const command of operations){
          if(command===OPS.moveTo){point=transform(coordinates[at++],coordinates[at++]);start=point;}
          else if(command===OPS.lineTo){const next=transform(coordinates[at++],coordinates[at++]);line(point,next);point=next;}
          else if(command===OPS.rectangle){
            const x=coordinates[at++],y=coordinates[at++],w=coordinates[at++],h=coordinates[at++];
            const p=[transform(x,y),transform(x+w,y),transform(x+w,y+h),transform(x,y+h)];
            for(let j=0;j<4;j++)line(p[j],p[(j+1)%4]);point=start=p[0];
          }else if(command===OPS.closePath){line(point,start);point=start;}
          else if(command===OPS.curveTo){at+=4;point=transform(coordinates[at++],coordinates[at++]);}
          else if(command===OPS.curveTo2||command===OPS.curveTo3){at+=2;point=transform(coordinates[at++],coordinates[at++]);}
        }
      }else if([OPS.stroke,OPS.closeStroke,OPS.fillStroke,OPS.eoFillStroke,OPS.closeFillStroke,OPS.closeEOFillStroke].includes(op)){
        if(op===OPS.closeStroke||op===OPS.closeFillStroke||op===OPS.closeEOFillStroke)line(point,start);
        result.push(...path);path=[];point=start=null;
      }else if([OPS.fill,OPS.eoFill,OPS.endPath].includes(op)){path=[];point=start=null;}
    }
    return result;
  }
  function merged(segments){
    const out=[];
    for(const segment of segments){
      let current={...segment},again=true;
      while(again){
        again=false;
        for(let i=out.length-1;i>=0;i--){const old=out[i];
          if(old.axis===current.axis&&Math.abs(old.at-current.at)<EPS&&old.lo<=current.hi+EPS&&current.lo<=old.hi+EPS){
            current.lo=Math.min(current.lo,old.lo);current.hi=Math.max(current.hi,old.hi);out.splice(i,1);again=true;
          }
        }
      }
      out.push(current);
    }
    return out;
  }
  const crosses=(a,b)=>a.axis!==b.axis&&a.at>=b.lo-EPS&&a.at<=b.hi+EPS&&b.at>=a.lo-EPS&&b.at<=a.hi+EPS;
  function ruledTables(list,OPS,lines){
    const segments=merged(strokeSegments(list,OPS));
    // Keep graphic-heavy pages bounded; text remains available without tables.
    if(segments.length>1500)return [];
    const seen=new Set(),tables=[];
    for(let i=0;i<segments.length;i++){
      if(seen.has(i))continue;
      const queue=[i],group=[];seen.add(i);
      while(queue.length){const id=queue.pop(),line=segments[id];group.push(line);
        for(let j=0;j<segments.length;j++)if(!seen.has(j)&&crosses(line,segments[j])){seen.add(j);queue.push(j);}
      }
      const vertical=group.filter(s=>s.axis==='v'),horizontal=group.filter(s=>s.axis==='h');
      if(vertical.length<3||horizontal.length<3)continue;
      const xs=vertical.map(s=>s.at).sort((a,b)=>a-b),ys=horizontal.map(s=>s.at).sort((a,b)=>b-a);
      if(xs.some((x,j)=>j&&x-xs[j-1]<4)||ys.some((y,j)=>j&&ys[j-1]-y<4))continue;
      const left=xs[0],right=xs.at(-1),top=ys[0],bottom=ys.at(-1);
      // Only complete rectangular grids: do not invent cells for charts or merged headers.
      if(!vertical.every(s=>s.lo<=bottom+EPS&&s.hi>=top-EPS)||!horizontal.every(s=>s.lo<=left+EPS&&s.hi>=right-EPS))continue;
      const cells=Array.from({length:ys.length-1},()=>Array.from({length:xs.length-1},()=>[]));
      const items=lines.flatMap(l=>l.items).filter(it=>it.x+it.w/2>=left-EPS&&it.x+it.w/2<=right+EPS&&it.y>=bottom-EPS&&it.y<=top+EPS);
      for(const item of items){
        const x=item.x+item.w/2,row=ys.findIndex((y,j)=>j<ys.length-1&&item.y<=y+EPS&&item.y>ys[j+1]-EPS),col=xs.findIndex((v,j)=>j<xs.length-1&&x>=v-EPS&&x<xs[j+1]+EPS);
        if(row>=0&&col>=0)cells[row][col].push(item);
      }
      const rows=cells.map(row=>row.map(items=>{
        const cellLines=[];
        items.sort((a,b)=>(b.y-a.y)||(a.x-b.x));
        for(const item of items){let ln=cellLines.find(l=>Math.abs(l.y-item.y)<Math.max(2,item.h*.4));if(!ln){ln={y:item.y,items:[]};cellLines.push(ln);}ln.items.push(item);}
        return cellLines.map(l=>textLine(l.items).text).join('\n');
      }));
      if(rows.filter(row=>row.some(Boolean)).length<2)continue;
      const first=cells[0].flat(),header=first.length>0&&first.filter(it=>it.b).length>first.length/2;
      const sizes=items.map(it=>it.h).sort((a,b)=>a-b);
      tables.push({t:'table',rows,header,widths:xs.slice(1).map((x,j)=>x-xs[j]),fontSize:sizes[Math.floor(sizes.length/2)]||10,left,right,top,bottom,items:new Set(items)});
    }
    return tables.sort((a,b)=>b.top-a.top);
  }
  function textLine(items){
    items=items.slice().sort((a,b)=>a.x-b.x);const runs=[];let end=null,text='';
    for(const item of items){
      const space=end!==null&&item.x-end>.18*item.h&&!/\s$/.test(text)&&!/^\s/.test(item.s)?' ':'';
      const t=space+item.s;const last=runs.at(-1),size=Math.round(item.h*2)/2;
      if(last&&!!last.b===!!item.b&&!!last.i===!!item.i&&last.size===size)last.t+=t;
      else runs.push({t,b:!!item.b,i:!!item.i,size});
      text+=t;end=item.x+item.w;
    }
    return {items,runs,text:text.replace(/\s+/g,' ').trim(),raw:text,x0:items[0]?.x||0,x1:end||0,y:items[0]?.y||0,h:Math.max(...items.map(i=>i.h),1)};
  }
  function blocks(pages,plain){
    const result=[];
    // Use the document's body size even when a table splits the prose into small groups.
    const heights=pages.flatMap(page=>{
      const tableItems=new Set((page.lines.tables||[]).flatMap(table=>[...table.items]));
      return page.lines.flatMap(line=>{
        const prose=line.items.filter(item=>!tableItems.has(item));
        return prose.length?[Math.max(...prose.map(item=>item.h))]:[];
      });
    }).sort((a,b)=>a-b);
    const bodySize=heights[Math.floor(heights.length/2)]||11;
    for(const page of pages){
      const tables=page.lines.tables||[];
      if(!tables.length){result.push(...plain([page],bodySize));continue;}
      const inTable=new Set(tables.flatMap(t=>[...t.items]));
      const prose=page.lines.map(line=>textLine(line.items.filter(item=>!inTable.has(item)))).filter(line=>line.text);
      const events=[...prose.map(line=>({y:line.y,line})),...tables.map(table=>({y:table.top,table}))].sort((a,b)=>b.y-a.y);
      let pending=[];
      const flush=()=>{if(pending.length){result.push(...plain([{lines:pending,w:page.w}],bodySize));pending=[];}};
      for(const event of events){if(event.table){flush();result.push(event.table);}else pending.push(event.line);}
      flush();
    }
    return result;
  }
  window.OfficePdfLayout={ruledTables,textLine,blocks};
})();
