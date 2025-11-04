// server.js - API REST + frontend estático + SLA Escalado→Pendiente (2h)
import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import morgan from 'morgan';
import { fileURLToPath } from 'url';
import { nanoid } from 'nanoid';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

const DB_DIR = path.join(__dirname, 'db');
const CASES_FILE = path.join(DB_DIR, 'cases.json');
const HISTORY_FILE = path.join(DB_DIR, 'history.json');

if (!fs.existsSync(DB_DIR)) fs.mkdirSync(DB_DIR, { recursive: true });
if (!fs.existsSync(CASES_FILE)) fs.writeFileSync(CASES_FILE, JSON.stringify([]));
if (!fs.existsSync(HISTORY_FILE)) fs.writeFileSync(HISTORY_FILE, JSON.stringify([]));

app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

const readJson = (filePath) => JSON.parse(fs.readFileSync(filePath, 'utf-8'));
const writeJson = (filePath, data) => fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
const nowIso = () => new Date().toISOString();

function pushHistory({ action, caseId, before = null, after = null, meta = {} }) {
  const history = readJson(HISTORY_FILE);
  history.push({
    id: nanoid(),
    timestamp: nowIso(),
    action, // 'CREATE' | 'UPDATE' | 'DELETE' | 'SLA_AUTO'
    caseId,
    before,
    after,
    meta
  });
  writeJson(HISTORY_FILE, history);
}

// === SLA ===
const DEFAULT_SLA_HOURS = 2;
const toMs = (h) => Number(h || 0) * 60 * 60 * 1000;

function computeEscaladoUntil(creadoEn, slaHours = DEFAULT_SLA_HOURS) {
  const t = new Date(creadoEn).getTime() + toMs(slaHours);
  return new Date(t).toISOString();
}

function withSlaProjection(c) {
  if (c.estado !== 'Escalado' || !c.escaladoUntil) return { ...c, remainingSlaSeconds: null };
  const remaining = Math.max(0, Math.floor((new Date(c.escaladoUntil).getTime() - Date.now()) / 1000));
  return { ...c, remainingSlaSeconds: remaining };
}

// === API: CASOS ===
app.get('/api/cases', (req, res) => {
  let cases = readJson(CASES_FILE);
  const { q, categoria, estado, escalado } = req.query;

  if (q && q.trim()) {
    const t = q.toLowerCase();
    cases = cases.filter(c =>
      (c.titulo || '').toLowerCase().includes(t) ||
      (c.notas || '').toLowerCase().includes(t) ||
      (c.categoria || '').toLowerCase().includes(t)
    );
  }
  if (categoria && categoria !== 'Todas') {
    cases = cases.filter(c => (c.categoria || '') === categoria);
  }
  if (estado && estado !== 'Todos') {
    cases = cases.filter(c => c.estado === estado);
  }
  if (typeof escalado !== 'undefined' && escalado !== 'Todos') {
    const bool = String(escalado).toLowerCase() === 'si';
    cases = cases.filter(c => c.escalado === bool);
  }

  res.json(cases.map(withSlaProjection));
});

app.post('/api/cases', (req, res) => {
  const cases = readJson(CASES_FILE);
  let { titulo, categoria, escalado, notas, estado, slaHours } = req.body;

  if (!titulo) return res.status(400).json({ error: 'titulo es obligatorio' });

  const isEscalado = (estado === 'Escalado') || Boolean(escalado);
  const createdAt = nowIso();

  const newCase = {
    id: nanoid(),
    titulo: String(titulo),
    categoria: categoria ? String(categoria) : '',
    escalado: Boolean(isEscalado),
    estado: isEscalado ? 'Escalado' : (estado === 'OK' ? 'OK' : 'Pendiente'),
    notas: notas ? String(notas) : '',
    slaHours: isEscalado ? Number(slaHours || DEFAULT_SLA_HOURS) : null,
    escaladoUntil: isEscalado ? computeEscaladoUntil(createdAt, slaHours || DEFAULT_SLA_HOURS) : null,
    creadoEn: createdAt,
    actualizadoEn: createdAt
  };

  cases.push(newCase);
  writeJson(CASES_FILE, cases);
  pushHistory({ action: 'CREATE', caseId: newCase.id, after: newCase });

  res.status(201).json(withSlaProjection(newCase));
});

app.put('/api/cases/:id', (req, res) => {
  const { id } = req.params;
  const cases = readJson(CASES_FILE);
  const idx = cases.findIndex(c => c.id === id);
  if (idx === -1) return res.status(404).json({ error: 'Caso no encontrado' });

  const before = { ...cases[idx] };
  const { titulo, categoria, escalado, notas, estado, slaHours } = req.body;

  if (typeof titulo !== 'undefined') cases[idx].titulo = String(titulo);
  if (typeof categoria !== 'undefined') cases[idx].categoria = String(categoria);
  if (typeof notas !== 'undefined') cases[idx].notas = String(notas);

  if (estado === 'OK') {
    cases[idx].estado = 'OK';
    cases[idx].escalado = false;
    cases[idx].slaHours = null;
    cases[idx].escaladoUntil = null;
  } else if (estado === 'Pendiente') {
    cases[idx].estado = 'Pendiente';
    cases[idx].escalado = false;
    cases[idx].slaHours = null;
    cases[idx].escaladoUntil = null;
  } else if (estado === 'Escalado' || escalado === true || escalado === 'si') {
    const hours = Number(slaHours || cases[idx].slaHours || DEFAULT_SLA_HOURS);
    cases[idx].estado = 'Escalado';
    cases[idx].escalado = true;
    cases[idx].slaHours = hours;
    cases[idx].escaladoUntil = computeEscaladoUntil(nowIso(), hours);
  }
  if (typeof escalado !== 'undefined' && (escalado === false || escalado === 'no') && !estado) {
    cases[idx].estado = 'Pendiente';
    cases[idx].escalado = false;
    cases[idx].slaHours = null;
    cases[idx].escaladoUntil = null;
  }

  cases[idx].actualizadoEn = nowIso();
  writeJson(CASES_FILE, cases);
  pushHistory({ action: 'UPDATE', caseId: id, before, after: cases[idx] });

  res.json(withSlaProjection(cases[idx]));
});

app.delete('/api/cases/:id', (req, res) => {
  const { id } = req.params;
  const cases = readJson(CASES_FILE);
  const idx = cases.findIndex(c => c.id === id);
  if (idx === -1) return res.status(404).json({ error: 'Caso no encontrado' });

  const before = { ...cases[idx] };
  const updated = [...cases.slice(0, idx), ...cases.slice(idx + 1)];
  writeJson(CASES_FILE, updated);
  pushHistory({ action: 'DELETE', caseId: id, before });

  res.json({ ok: true });
});

// CATEGORÍAS
app.get('/api/categories', (req, res) => {
  const cases = readJson(CASES_FILE);
  const set = new Set();
  for (const c of cases) if (c.categoria) set.add(c.categoria);
  res.json(Array.from(set).sort());
});

// HISTORIAL
app.get('/api/history', (req, res) => {
  const { caseId } = req.query;
  let history = readJson(HISTORY_FILE);
  if (caseId) history = history.filter(h => h.caseId === caseId);
  history.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  res.json(history);
});

// === SCHEDULER: revisar SLA cada 60s y pasar Escalado -> Pendiente ===
setInterval(() => {
  const cases = readJson(CASES_FILE);
  let changed = false;

  for (let i = 0; i < cases.length; i++) {
    const c = cases[i];
    if (c.estado === 'Escalado' && c.escaladoUntil && Date.now() >= new Date(c.escaladoUntil).getTime()) {
      const before = { ...c };
      c.estado = 'Pendiente';
      c.escalado = false;
      c.slaHours = null;
      c.escaladoUntil = null;
      c.actualizadoEn = nowIso();
      cases[i] = c;
      pushHistory({
        action: 'SLA_AUTO',
        caseId: c.id,
        before,
        after: c,
        meta: { reason: 'Escalado vencido (2h por defecto)' }
      });
      changed = true;
    }
  }
  if (changed) writeJson(CASES_FILE, cases);
}, 60 * 1000);

// === Servir frontend ===
const FRONTEND_DIR = path.join(__dirname, '..', 'frontend');
app.use(express.static(FRONTEND_DIR));
app.get(/^(?!\/api).*/, (req, res) => {
  res.sendFile(path.join(FRONTEND_DIR, 'index.html'));
});

// Escucha en todas las interfaces (útil en red local)
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Servidor listo en: http://localhost:${PORT}`);
});
