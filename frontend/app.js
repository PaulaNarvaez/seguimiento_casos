// app.js - UI con SLA 2h, estado editable y link al HILO por Case ID
const API = (p) => `/api${p}`;
const $ = (s)=>document.querySelector(s);
const rows = $('#rows');

function badgeEstado(estado){
  return estado === 'OK'
    ? '<span class="badge ok">OK</span>'
    : (estado === 'Escalado'
        ? '<span class="badge escalado">Escalado</span>'
        : '<span class="badge pending">Pendiente</span>');
}
function fmtDate(iso){ const d = new Date(iso); return d.toLocaleString(); }
function fmtCountdown(sec){
  if (sec == null) return '';
  const s = Math.max(0, Number(sec));
  const mm = String(Math.floor(s/60)).padStart(2,'0');
  const ss = String(s%60).padStart(2,'0');
  return `${mm}:${ss}`;
}

async function cargarCategorias(){
  const res = await fetch(API('/categories'));
  const cats = await res.json();
  const fSel = $('#fCategoria');
  fSel.innerHTML = '<option value="Todas">Todas las categorías</option>' +
    cats.map(c=>`<option>${c}</option>`).join('');
}

async function listar(){
  const q = $('#q').value.trim();
  const fCategoria = $('#fCategoria').value;
  const fEstado = $('#fEstado').value;
  const fEscalado = $('#fEscalado').value;

  const params = new URLSearchParams();
  if (q) params.set('q', q);
  if (fCategoria && fCategoria !== 'Todas') params.set('categoria', fCategoria);
  if (fEstado && fEstado !== 'Todos') params.set('estado', fEstado);
  if (fEscalado && fEscalado !== 'Todos') params.set('escalado', fEscalado.toLowerCase());

  const res = await fetch(API('/cases?'+params.toString()));
  const data = await res.json();

  rows.innerHTML = '';
  data.forEach((c, i)=>{
    const escaladoInfo = c.estado === 'Escalado'
      ? `<div style="font-size:12px;color:#93a3b8">SLA restante: <strong>${fmtCountdown(c.remainingSlaSeconds)}</strong></div>`
      : '';

    const row = document.createElement('div');
    row.className = 'row';
    row.style.gridTemplateColumns = '40px 1.2fr .9fr .8fr 1.2fr .8fr 1.1fr .8fr';
    row.innerHTML = `
      <div class="td"><div class="idbadge">${String(i+1).padStart(2,'0')}</div></div>
      <div class="td">
        <input data-k="titulo" data-id="${c.id}" type="text" value="${escapeHtml(c.titulo)}">
        <div style="margin-top:6px;font-size:12px"><a class="link" href="./history.html?caseId=${c.id}" target="_blank">Ver hilo »</a></div>
      </div>
      <div class="td"><input data-k="categoria" data-id="${c.id}" type="text" value="${escapeHtml(c.categoria||'')}"></div>
      <div class="td">
        <select data-k="escalado" data-id="${c.id}">
          <option value="no" ${!c.escalado?'selected':''}>No</option>
          <option value="si" ${c.escalado?'selected':''}>Sí</option>
        </select>
        ${escaladoInfo}
      </div>
      <div class="td"><input data-k="notas" data-id="${c.id}" type="text" value="${escapeHtml(c.notas||'')}"></div>
      <div class="td" style="font-size:12px;color:#93a3b8">${fmtDate(c.actualizadoEn)}</div>
      <div class="td actions">
        <button data-act="guardar" data-id="${c.id}">Guardar</button>
        <button data-act="borrar" data-id="${c.id}">Borrar</button>
      </div>
      <div class="td">
        <select data-k="estado" data-id="${c.id}">
          <option value="Pendiente" ${c.estado==='Pendiente'?'selected':''}>Pendiente</option>
          <option value="Escalado" ${c.estado==='Escalado'?'selected':''}>Escalado</option>
          <option value="OK" ${c.estado==='OK'?'selected':''}>OK</option>
        </select>
      </div>
    `;
    rows.appendChild(row);
  });
}

function escapeHtml(str){
  return String(str)
    .replaceAll('&','&amp;')
    .replaceAll('<','&lt;')
    .replaceAll('>','&gt;')
    .replaceAll('"','&quot;')
    .replaceAll("'","&#039;");
}

async function agregar(){
  const titulo = $('#titulo').value.trim();
  const categoria = $('#categoria').value.trim();
  const escalado = $('#escalado').value === 'si';
  const estado = $('#estado').value;
  const notas = $('#notas').value.trim();

  if (!titulo){ alert('El título es obligatorio'); return; }

  const body = { titulo, categoria, escalado, notas, estado };
  const res = await fetch(API('/cases'), {
    method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)
  });
  if (!res.ok){
    const err = await res.json().catch(()=>({})); alert('Error al crear: ' + (err.error || res.status)); return;
  }
  $('#titulo').value = ''; $('#notas').value = '';
  await cargarCategorias(); await listar();
}

async function actualizar(id){
  const inputs = rows.querySelectorAll(`[data-id="${id}"]`);
  const payload = {};
  let estadoElegido = null;

  inputs.forEach(el=>{
    const k = el.getAttribute('data-k');
    if (k === 'estado') {
      estadoElegido = el.value;
      payload.estado = estadoElegido;
    } else if (k === 'escalado') {
      payload.escalado = (el.value === 'si');
    } else {
      payload[k] = el.value;
    }
  });

  // Precedencia: ESTADO manda
  if (estadoElegido === 'Escalado') {
    payload.escalado = true;
  } else if (estadoElegido === 'OK' || estadoElegido === 'Pendiente') {
    payload.escalado = false;
  } else if (payload.escalado) {
    payload.estado = 'Escalado';
  }

  const res = await fetch(API(`/cases/${id}`), {
    method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)
  });
  if (!res.ok){
    const err = await res.json().catch(()=>({})); alert('Error al actualizar: ' + (err.error || res.status)); return;
  }
  await cargarCategorias(); await listar();
}

async function borrar(id){
  if (!confirm('¿Seguro que quieres borrar este caso?')) return;
  const res = await fetch(API(`/cases/${id}`), { method:'DELETE' });
  if (!res.ok){
    const err = await res.json().catch(()=>({})); alert('Error al borrar: ' + (err.error || res.status)); return;
  }
  await cargarCategorias(); await listar();
}

// sincronía visual
rows.addEventListener('change', (e)=>{
  const el = e.target;
  if (!el.matches('select[data-k]')) return;
  const id = el.getAttribute('data-id');
  if (el.getAttribute('data-k') === 'estado') {
    const esc = rows.querySelector(`select[data-k="escalado"][data-id="${id}"]`);
    if (esc) esc.value = (el.value === 'Escalado') ? 'si' : 'no';
  }
  if (el.getAttribute('data-k') === 'escalado') {
    const est = rows.querySelector(`select[data-k="estado"][data-id="${id}"]`);
    if (est && el.value === 'si') est.value = 'Escalado';
  }
});

$('#btnAdd').addEventListener('click', agregar);
$('#btnReset').addEventListener('click', async ()=>{
  $('#q').value = ''; $('#fCategoria').value = 'Todas'; $('#fEstado').value = 'Todos'; $('#fEscalado').value = 'Todos';
  await listar();
});
$('#q').addEventListener('input', listar);
['fCategoria','fEstado','fEscalado'].forEach(id => document.getElementById(id).addEventListener('change', listar));
rows.addEventListener('click', async (e)=>{
  const btn = e.target.closest('button'); if (!btn) return;
  const id = btn.getAttribute('data-id'); const act = btn.getAttribute('data-act');
  if (act === 'guardar') await actualizar(id);
  if (act === 'borrar') await borrar(id);
});

setInterval(listar, 15 * 1000);
(async function init(){ await cargarCategorias(); await listar(); })();
