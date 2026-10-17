/* ==========================================================================
   AquaAlerta — cliente de la API del supervisor (FastAPI local)
   Cambia la URL definiendo window.AQUA_API_BASE antes de cargar este archivo.
   ========================================================================== */

const API_BASE = window.AQUA_API_BASE || 'http://127.0.0.1:8000';

/* GET/POST con tiempo de espera; lanza Error con un mensaje legible si falla la red o la respuesta. */
async function apiFetch(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: options.body ? { 'Content-Type': 'application/json' } : undefined,
      signal: controller.signal,
    });
  } catch (e) {
    throw new Error('No se pudo conectar con la API. Verifica que el backend esté en ejecución.');
  } finally {
    clearTimeout(timer);
  }
  let data = null;
  try { data = await res.json(); } catch (e) { /* respuesta sin JSON */ }
  if (!res.ok) {
    const detail = data && typeof data.detail === 'string' ? data.detail : `Error HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

/* Escapa texto antes de insertarlo con innerHTML (los datos vienen de reportes ciudadanos). */
function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

/* Estados reales del backend (schemas/models.py → Estado) con las clases de badge existentes. */
const ESTADOS = {
  recibido: { label: 'Recibido', badge: 'badge-cyan' },
  en_analisis: { label: 'En análisis', badge: 'badge-purple' },
  pendiente_de_informacion: { label: 'Pendiente de información', badge: 'badge-slate' },
  pendiente_de_revision: { label: 'Pendiente de revisión', badge: 'badge-purple' },
  validado: { label: 'Validado', badge: 'badge-cyan' },
  propuesto: { label: 'Propuesto', badge: 'badge-cyan' },
  pendiente_de_aprobacion: { label: 'Pendiente de aprobación', badge: 'badge-orange' },
  aprobado: { label: 'Aprobado', badge: 'badge-green' },
  rechazado: { label: 'Rechazado', badge: 'badge-slate' },
  cambios_solicitados: { label: 'Cambios solicitados', badge: 'badge-purple' },
  ejecutado: { label: 'Ejecutado', badge: 'badge-blue' },
  verificado: { label: 'Verificado', badge: 'badge-green' },
  bloqueado: { label: 'Bloqueado', badge: 'badge-critical' },
};

const TIPOS = {
  falta_de_agua: 'Falta de agua',
  tuberia_rota: 'Tubería rota',
  agua_contaminada: 'Agua contaminada',
  indeterminado: 'Indeterminado',
};

function estadoLabel(estado) {
  return (ESTADOS[estado] || { label: estado }).label;
}

function estadoBadge(estado, sufijo = '') {
  const e = ESTADOS[estado] || { label: estado, badge: 'badge-slate' };
  return `<span class="badge-status ${e.badge}">${esc(e.label)}${sufijo ? ` · ${esc(sufijo)}` : ''}</span>`;
}

function fechaCorta(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return isNaN(d) ? esc(iso) : d.toLocaleString('es-PA', { dateStyle: 'short', timeStyle: 'short' });
}

/* Decisión del supervisor desde el panel: la API la registra SIEMPRE como simulada (sin autenticación). */
async function decidirPlan(idPlan, decision, boton) {
  let motivo = '';
  if (decision !== 'aprobado' || boton.dataset.extraordinaria === 'true') {
    motivo = window.prompt('Motivo de la decisión (obligatorio en aprobaciones extraordinarias):', '') ?? null;
    if (motivo === null) return false;
  }
  const botones = boton.parentElement.querySelectorAll('button');
  botones.forEach((b) => { b.disabled = true; });
  try {
    await apiFetch(`/api/plans/${encodeURIComponent(idPlan)}/decision`, {
      method: 'POST',
      body: JSON.stringify({ decision, supervisor: 'panel-web (sin autenticación)', motivo }),
    });
    showToast('success', 'Decisión registrada (simulada)', `Plan ${idPlan}: ${estadoLabel(decision)}. No autoriza ejecución real.`);
    return true;
  } catch (e) {
    showToast('error', 'No se registró la decisión', e.message);
    botones.forEach((b) => { b.disabled = false; });
    return false;
  }
}

function accionesPlan(plan) {
  if (!plan || plan.estado !== 'pendiente_de_aprobacion') return '<span style="font-size:0.8rem; color:#64748b;">—</span>';
  const extra = plan.tipo_aprobacion === 'extraordinaria';
  return `<div style="display:flex; gap:0.4rem; flex-wrap:wrap;">
    <button type="button" class="btn btn-outline btn-sm" data-plan="${esc(plan.id_plan)}" data-decision="aprobado" data-extraordinaria="${extra}">Aprobar (simulado)</button>
    <button type="button" class="btn btn-outline btn-sm" data-plan="${esc(plan.id_plan)}" data-decision="rechazado">Rechazar</button>
  </div>`;
}
