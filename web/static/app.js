// web/static/app.js
/**
 * Polinema Log Book Client Application.
 * Reactive Vanilla JS SPA State Manager & API Orchestrator.
 */

(function () {
  'use strict';

  // State
  const state = {
    calendar: null,
    activeMonth: 'all',     // 'all' or 1..6
    activeFilter: 'all',    // 'all', 'missing', 'filled'
    activeEditingDay: null, // { date, hari, tanggal_str, jam_masuk, jam_pulang, note }
    theme: localStorage.getItem('logbook_theme') || 'light',
  };

  // DOM Elements
  const dom = {
    bentoContainer: document.getElementById('bento-container'),
    progressRatio: document.getElementById('progress-ratio'),
    progressPercent: document.getElementById('progress-percent'),
    progressBar: document.getElementById('progress-bar'),
    monthTabs: document.getElementById('month-tabs'),
    filterButtons: document.querySelectorAll('.filter-btn'),
    btnThemeToggle: document.getElementById('btn-theme-toggle'),
    btnAutofill: document.getElementById('btn-autofill'),
    btnOpenPdf: document.getElementById('btn-open-pdf'),
    btnOpenConfig: document.getElementById('btn-open-config'),
    toastContainer: document.getElementById('toast-container'),

    // Modals
    modalEditor: document.getElementById('modal-editor'),
    editorHariBadge: document.getElementById('editor-hari-badge'),
    editorTanggalTitle: document.getElementById('editor-tanggal-title'),
    editorHours: document.getElementById('editor-hours'),
    editorNote: document.getElementById('editor-note'),
    btnFormalize: document.getElementById('btn-formalize'),
    btnSuggestTask: document.getElementById('btn-suggest-task'),
    btnSaveNote: document.getElementById('btn-save-note'),

    modalPdf: document.getElementById('modal-pdf'),
    pdfTargetSelect: document.getElementById('pdf-target-select'),
    btnTriggerCompile: document.getElementById('btn-trigger-compile'),
    pdfIframe: document.getElementById('pdf-iframe'),
    pdfPlaceholder: document.querySelector('.pdf-placeholder'),

    modalConfig: document.getElementById('modal-config'),
    btnSaveConfig: document.getElementById('btn-save-config'),
    cfgMhsNama: document.getElementById('cfg-mhs-nama'),
    cfgMhsNim: document.getElementById('cfg-mhs-nim'),
    cfgMhsProdi: document.getElementById('cfg-mhs-prodi'),
    cfgMhsMitra: document.getElementById('cfg-mhs-mitra'),
    cfgDosenNama: document.getElementById('cfg-dosen-nama'),
    cfgDosenNip: document.getElementById('cfg-dosen-nip'),
    cfgLapanganNama: document.getElementById('cfg-lapangan-nama'),
    cfgLapanganNik: document.getElementById('cfg-lapangan-nik'),
  };

  // Utilities
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    dom.toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 250);
    }, 3500);
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('logbook_theme', theme);
    state.theme = theme;
  }

  // API Calls
  async function fetchCalendar() {
    try {
      const res = await fetch('/api/calendar');
      if (!res.ok) throw new Error('Gagal memuat kalender');
      state.calendar = await res.json();
      renderApp();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function saveDayNote(dateStr, noteText) {
    try {
      const res = await fetch('/api/save-day', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: dateStr, note: noteText }),
      });
      if (!res.ok) throw new Error('Gagal menyimpan catatan');
      showToast(`Catatan untuk ${dateStr} berhasil disimpan`, 'success');
      closeModal(dom.modalEditor);
      await fetchCalendar();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function formalizeCurrentNote() {
    const rawNote = dom.editorNote.value.trim();
    if (!rawNote) {
      showToast('Ketik catatan terlebih dahulu sebelum diformalkan.', 'error');
      return;
    }
    try {
      dom.btnFormalize.disabled = true;
      dom.btnFormalize.innerText = '⚡ Memproses...';
      const res = await fetch('/api/formalize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ note: rawNote }),
      });
      if (!res.ok) throw new Error('Gagal memformalkan narasi');
      const data = await res.json();
      dom.editorNote.value = data.formalized;
      showToast('Narasi berhasil diformalkan!', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      dom.btnFormalize.disabled = false;
      dom.btnFormalize.innerText = '⚡ Formalize Narasi';
    }
  }
  const formalizeNote = formalizeCurrentNote;

  async function triggerBatchAutofill() {
    const confirmRun = confirm(
      'Apakah Anda yakin ingin mengisi semua hari kerja aktif yang masih kosong dengan kurikulum kegiatan IT PT Naraya Telematika?\n\nCatatan yang sudah diisi manual tidak akan ditimpa.'
    );
    if (!confirmRun) return;

    try {
      dom.btnAutofill.disabled = true;
      dom.btnAutofill.innerHTML = '<span class="icon">⏳</span><span>Mengisi...</span>';
      const res = await fetch('/api/batch-autofill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ overwrite_existing: false }),
      });
      if (!res.ok) throw new Error('Gagal mengisi otomatis');
      const data = await res.json();
      showToast(data.message, 'success');
      await fetchCalendar();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      dom.btnAutofill.disabled = false;
      dom.btnAutofill.innerHTML = '<span class="icon">⚡</span><span>Lengkapi Kosong</span>';
    }
  }

  async function loadConfigData() {
    try {
      const res = await fetch('/api/config');
      if (!res.ok) throw new Error('Gagal memuat konfigurasi');
      const cfg = await res.json();
      const mhs = cfg.mahasiswa || {};
      const dosen = (cfg.pembimbing && cfg.pembimbing.dosen) || {};
      const lapangan = (cfg.pembimbing && cfg.pembimbing.lapangan) || {};

      dom.cfgMhsNama.value = mhs.nama || '';
      dom.cfgMhsNim.value = mhs.nim || '';
      dom.cfgMhsProdi.value = mhs.prodi || '';
      dom.cfgMhsMitra.value = mhs.mitra || '';
      dom.cfgDosenNama.value = dosen.nama || '';
      dom.cfgDosenNip.value = dosen.nip || '';
      dom.cfgLapanganNama.value = lapangan.nama || '';
      dom.cfgLapanganNik.value = lapangan.nik || '';

      openModal(dom.modalConfig);
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function saveConfigData() {
    const payload = {
      mahasiswa: {
        nama: dom.cfgMhsNama.value.trim(),
        nim: dom.cfgMhsNim.value.trim(),
        prodi: dom.cfgMhsProdi.value.trim(),
        mitra: dom.cfgMhsMitra.value.trim(),
      },
      pembimbing: {
        dosen: {
          nama: dom.cfgDosenNama.value.trim(),
          nip: dom.cfgDosenNip.value.trim(),
        },
        lapangan: {
          nama: dom.cfgLapanganNama.value.trim(),
          nik: dom.cfgLapanganNik.value.trim(),
        },
      },
      pengaturan: {
        jam_kerja: {
          senin_jumat: { masuk: '08.00', pulang: '16.00' },
          sabtu: { masuk: '08.00', pulang: '14.00' },
        },
      },
    };

    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('Gagal memperbarui konfigurasi');
      showToast('Konfigurasi profil berhasil diperbarui', 'success');
      closeModal(dom.modalConfig);
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function compileAndPreviewPdf() {
    const target = dom.pdfTargetSelect.value;
    try {
      dom.btnTriggerCompile.disabled = true;
      dom.btnTriggerCompile.innerHTML = '<span class="icon">⏳</span><span>Kompilasi...</span>';

      const res = await fetch('/api/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target }),
      });
      if (!res.ok) throw new Error('Kompilasi XeLaTeX gagal');
      const data = await res.json();

      dom.pdfPlaceholder.classList.add('hidden');
      dom.pdfIframe.classList.remove('hidden');
      dom.pdfIframe.src = `${data.pdf_url}?t=${Date.now()}`;
      showToast('Berkas PDF berhasil dikompilasi!', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      dom.btnTriggerCompile.disabled = false;
      dom.btnTriggerCompile.innerHTML = '<span class="icon">⚙️</span><span>Kompilasi PDF (XeLaTeX)</span>';
    }
  }

  // Modals Control
  function openModal(modal) {
    modal.classList.remove('hidden');
  }

  function closeModal(modal) {
    modal.classList.add('hidden');
  }

  function openEditor(day) {
    state.activeEditingDay = day;
    dom.editorHariBadge.innerText = day.hari;
    dom.editorTanggalTitle.innerText = day.tanggal_str;
    dom.editorHours.innerText = `${day.jam_masuk} - ${day.jam_pulang} WIB`;
    dom.editorNote.value = day.note || '';
    openModal(dom.modalEditor);
  }

  // Rendering
  function renderApp() {
    if (!state.calendar) return;

    // 1. Progress Bar
    const total = state.calendar.total_days;
    const filled = state.calendar.filled_days;
    const percent = state.calendar.percentage;
    dom.progressRatio.innerText = `${filled} / ${total} Hari`;
    dom.progressPercent.innerText = `${percent}%`;
    dom.progressBar.style.width = `${percent}%`;

    // 2. Bento Grid
    dom.bentoContainer.innerHTML = '';

    // Filter months
    let targetMonths = state.calendar.months;
    if (state.activeMonth !== 'all') {
      const mIdx = parseInt(state.activeMonth, 10);
      targetMonths = targetMonths.filter((m) => m.month_index === mIdx);
    }

    targetMonths.forEach((month) => {
      month.weeks.forEach((week) => {
        // Filter days based on status filter
        let filteredDays = week.days;
        if (state.activeFilter === 'missing') {
          filteredDays = filteredDays.filter((d) => !d.is_filled);
        } else if (state.activeFilter === 'filled') {
          filteredDays = filteredDays.filter((d) => d.is_filled);
        }

        // If filter results in empty week, skip or show empty note
        if (filteredDays.length === 0 && state.activeFilter !== 'all') {
          return;
        }

        const card = document.createElement('div');
        card.className = 'week-card';

        const weekHeader = document.createElement('div');
        weekHeader.className = 'week-header';
        weekHeader.innerHTML = `
          <div class="week-title">
            <span>Minggu ke-${week.minggu_ke}</span>
            <span class="badge badge-primary">${month.name}</span>
          </div>
          <span class="badge ${week.days.every((d) => d.is_filled) ? 'badge-emerald' : 'badge-amber'}">
            ${week.days.filter((d) => d.is_filled).length} / ${week.days.length} Terisi
          </span>
        `;
        card.appendChild(weekHeader);

        const dayList = document.createElement('div');
        dayList.className = 'day-list';

        filteredDays.forEach((d) => {
          const item = document.createElement('div');
          item.className = `day-item ${d.is_filled ? 'filled' : 'missing'}`;

          const hasNote = d.is_filled && d.note;
          const noteText = hasNote ? d.note : 'Belum ada catatan kegiatan';

          item.innerHTML = `
            <div class="day-meta">${d.hari}, ${d.tanggal_str.split(' ')[0]} ${d.tanggal_str.split(' ')[1].slice(0, 3)}</div>
            <div class="day-hours">${d.jam_masuk}-${d.jam_pulang}</div>
            <div class="day-note-preview ${hasNote ? '' : 'empty'}" title="${noteText}">${noteText}</div>
            <button class="btn btn-sm btn-outline-primary btn-edit-day">Edit</button>
          `;

          item.querySelector('.btn-edit-day').addEventListener('click', () => openEditor(d));
          dayList.appendChild(item);
        });

        card.appendChild(dayList);
        dom.bentoContainer.appendChild(card);
      });
    });

    if (dom.bentoContainer.children.length === 0) {
      dom.bentoContainer.innerHTML = `
        <div class="loading-state">
          <p>Tidak ada kegiatan yang sesuai dengan filter yang dipilih.</p>
        </div>
      `;
    }
  }

  // Event Listeners Initialization
  function initEvents() {
    // Theme toggle
    dom.btnThemeToggle.addEventListener('click', () => {
      applyTheme(state.theme === 'light' ? 'dark' : 'light');
    });

    // Month tabs
    dom.monthTabs.querySelectorAll('.tab-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        dom.monthTabs.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeMonth = btn.getAttribute('data-month');
        renderApp();
      });
    });

    // Status filter buttons
    dom.filterButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        dom.filterButtons.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeFilter = btn.getAttribute('data-filter');
        renderApp();
      });
    });

    // Modal Close buttons
    document.querySelectorAll('[data-close]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const modalId = btn.getAttribute('data-close');
        const modal = document.getElementById(modalId);
        if (modal) closeModal(modal);
      });
    });

    // Editor Actions
    dom.btnFormalize.addEventListener('click', formalizeCurrentNote);
    dom.btnSuggestTask.addEventListener('click', () => {
      if (!dom.editorNote.value) {
        dom.editorNote.value = 'Mempelajari modul sistem dan koordinasi dengan tim pengembang';
      }
      formalizeCurrentNote();
    });
    dom.btnSaveNote.addEventListener('click', () => {
      if (state.activeEditingDay) {
        saveDayNote(state.activeEditingDay.date, dom.editorNote.value.trim());
      }
    });

    // Header Action Modals
    dom.btnAutofill.addEventListener('click', triggerBatchAutofill);
    dom.btnOpenConfig.addEventListener('click', loadConfigData);
    dom.btnSaveConfig.addEventListener('click', (e) => {
      e.preventDefault();
      saveConfigData();
    });

    dom.btnOpenPdf.addEventListener('click', () => {
      openModal(dom.modalPdf);
    });
    dom.btnTriggerCompile.addEventListener('click', compileAndPreviewPdf);
  }

  // Boot
  document.addEventListener('DOMContentLoaded', () => {
    applyTheme(state.theme);
    initEvents();
    fetchCalendar();
  });
})();
