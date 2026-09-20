// web/static/app.js
/**
 * Polinema Log Book Client Application.
 * Reactive Vanilla JS SPA State Manager & API Orchestrator.
 */

(function () {
  'use strict';

  // Constants
  const STATUS_BADGES = {
    izin: 'badge-izin',
    sakit: 'badge-sakit',
    cuti: 'badge-cuti',
    libur: 'badge-libur',
  };

  // State
  const state = {
    calendar: null,
    activeMonth: 'all',     // 'all' or month_index (1..N)
    activeFilter: 'all',    // 'all', 'missing', 'filled'
    activeEditingDay: null, // { date, hari, tanggal_str, jam_masuk, jam_pulang, note, status }
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
    editorStatus: document.getElementById('editor-status'),
    editorHoursGroup: document.getElementById('editor-hours-group'),
    editorHours: document.getElementById('editor-hours'),
    editorNoteLabel: document.getElementById('editor-note-label'),
    editorNote: document.getElementById('editor-note'),
    editorAssistBar: document.getElementById('editor-assist-bar'),
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
    cfgLapanganNama: document.getElementById('cfg-lapangan-nama'),
    cfgPeriodeMulai: document.getElementById('cfg-periode-mulai'),
    cfgPeriodeSelesai: document.getElementById('cfg-periode-selesai'),
    tableJamKerja: document.getElementById('table-jam-kerja'),
    rowJamSabtu: document.getElementById('row-jam-sabtu'),
  };

  const DAYS_OF_WEEK = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu'];

  function toggleSaturdayRow(schedule) {
    if (dom.rowJamSabtu) {
      if (schedule === 'senin_jumat') {
        dom.rowJamSabtu.classList.add('hidden-row');
      } else {
        dom.rowJamSabtu.classList.remove('hidden-row');
      }
    }
  }

  // Utilities
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    toast.innerHTML = `<span>${icon}</span><span>${escapeHtml(message)}</span>`;
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
      renderMonthTabs();
      renderPdfOptions();
      renderApp();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function saveDayNote(dateStr, noteText, status = 'hadir') {
    try {
      const res = await fetch('/api/save-day', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: dateStr, note: noteText, status: status }),
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
      const periode = cfg.periode || {};
      const pengaturan = cfg.pengaturan || {};

      dom.cfgMhsNama.value = mhs.nama || '';
      dom.cfgMhsNim.value = mhs.nim || '';
      dom.cfgMhsProdi.value = mhs.prodi || '';
      dom.cfgMhsMitra.value = mhs.mitra || '';
      dom.cfgDosenNama.value = dosen.nama || '';
      dom.cfgLapanganNama.value = lapangan.nama || '';

      const jamKerja = pengaturan.jam_kerja || {};
      const legacySj = jamKerja.senin_jumat || {};
      const legacySabtu = jamKerja.sabtu || {};

      DAYS_OF_WEEK.forEach(day => {
        const masukInput = document.getElementById(`cfg-jam-${day}-masuk`);
        const pulangInput = document.getElementById(`cfg-jam-${day}-pulang`);
        if (masukInput && pulangInput) {
          const daySpec = jamKerja[day] || (day === 'sabtu' ? legacySabtu : legacySj);
          masukInput.value = (daySpec && daySpec.masuk) || '08.00';
          pulangInput.value = (daySpec && daySpec.pulang) || (day === 'sabtu' ? '14.00' : '16.00');
        }
      });

      if (dom.cfgPeriodeMulai) dom.cfgPeriodeMulai.value = periode.tanggal_mulai || '2026-07-01';
      if (dom.cfgPeriodeSelesai) dom.cfgPeriodeSelesai.value = periode.tanggal_selesai || '2026-12-31';

      const hariKerja = pengaturan.hari_kerja || 'senin_sabtu';
      const radio = document.querySelector(`input[name="cfg-hari-kerja"][value="${hariKerja}"]`);
      if (radio) radio.checked = true;
      toggleSaturdayRow(hariKerja);

      openModal(dom.modalConfig);
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function saveConfigData() {
    const selectedHariKerja = document.querySelector('input[name="cfg-hari-kerja"]:checked')?.value || 'senin_sabtu';

    let existingCfg = {};
    try {
      const res = await fetch('/api/config');
      if (res.ok) existingCfg = await res.json();
    } catch (_) {}

    const jamKerjaPayload = {};
    DAYS_OF_WEEK.forEach(day => {
      const masukInput = document.getElementById(`cfg-jam-${day}-masuk`);
      const pulangInput = document.getElementById(`cfg-jam-${day}-pulang`);
      jamKerjaPayload[day] = {
        masuk: masukInput ? masukInput.value.trim() : '08.00',
        pulang: pulangInput ? pulangInput.value.trim() : (day === 'sabtu' ? '14.00' : '16.00')
      };
    });

    const payload = {
      ...existingCfg,
      mahasiswa: {
        ...(existingCfg.mahasiswa || {}),
        nama: dom.cfgMhsNama.value.trim(),
        nim: dom.cfgMhsNim.value.trim(),
        prodi: dom.cfgMhsProdi.value.trim(),
        mitra: dom.cfgMhsMitra.value.trim(),
      },
      pembimbing: {
        dosen: { nama: dom.cfgDosenNama.value.trim() },
        lapangan: { nama: dom.cfgLapanganNama.value.trim() }
      },
      periode: {
        ...(existingCfg.periode || {}),
        tanggal_mulai: dom.cfgPeriodeMulai ? dom.cfgPeriodeMulai.value : '2026-07-01',
        tanggal_selesai: dom.cfgPeriodeSelesai ? dom.cfgPeriodeSelesai.value : '2026-12-31',
      },
      pengaturan: {
        ...(existingCfg.pengaturan || {}),
        hari_kerja: selectedHariKerja,
        jam_kerja: jamKerjaPayload
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
      await fetchCalendar();
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
    if (modal) modal.classList.remove('hidden');
  }

  function closeModal(modal) {
    if (modal) modal.classList.add('hidden');
  }

  function updateEditorStatusUI(status) {
    const isHadir = status === 'hadir';
    if (isHadir) {
      if (dom.editorHoursGroup) dom.editorHoursGroup.style.opacity = '1';
      if (state.activeEditingDay) {
        dom.editorHours.innerText = `${state.activeEditingDay.jam_masuk} - ${state.activeEditingDay.jam_pulang} WIB`;
      }
      if (dom.editorAssistBar) dom.editorAssistBar.style.display = 'flex';
      dom.btnFormalize.disabled = false;
      dom.btnSuggestTask.disabled = false;
      if (dom.editorNoteLabel) dom.editorNoteLabel.innerText = 'Catatan Kegiatan Harian:';
      dom.editorNote.placeholder = 'Ketik catatan kegiatan atau gunakan tombol bantuan di bawah...';
    } else {
      if (dom.editorHoursGroup) dom.editorHoursGroup.style.opacity = '0.5';
      const label = status ? status.toUpperCase() : 'NON-HADIR';
      dom.editorHours.innerText = `Tidak ada jam kerja (${label})`;
      if (dom.editorAssistBar) dom.editorAssistBar.style.display = 'none';
      dom.btnFormalize.disabled = true;
      dom.btnSuggestTask.disabled = true;
      if (dom.editorNoteLabel) dom.editorNoteLabel.innerText = `Keterangan ${label} (Opsional):`;
      dom.editorNote.placeholder = `Keterangan atau alasan ${status} (opsional)...`;
    }
  }

  function openEditor(day) {
    state.activeEditingDay = day;
    const currentStatus = (day.status || day.attendance_status || 'hadir').toLowerCase();
    if (dom.editorStatus) dom.editorStatus.value = currentStatus;
    dom.editorHariBadge.innerText = day.hari;
    dom.editorTanggalTitle.innerText = day.tanggal_str;
    dom.editorNote.value = day.note || day.kegiatan || '';
    updateEditorStatusUI(currentStatus);
    openModal(dom.modalEditor);
  }

  // Dynamic Navigation & Selects
  function renderMonthTabs() {
    if (!state.calendar || !state.calendar.months || !dom.monthTabs) return;
    dom.monthTabs.innerHTML = '';

    const allBtn = document.createElement('button');
    allBtn.className = `tab-btn ${state.activeMonth === 'all' ? 'active' : ''}`;
    allBtn.setAttribute('data-month', 'all');
    allBtn.textContent = 'Semua Bulan';
    allBtn.addEventListener('click', () => {
      dom.monthTabs.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
      allBtn.classList.add('active');
      state.activeMonth = 'all';
      renderApp();
    });
    dom.monthTabs.appendChild(allBtn);

    const validIndices = ['all'];
    state.calendar.months.forEach((m) => {
      validIndices.push(String(m.month_index));
      const btn = document.createElement('button');
      btn.className = `tab-btn ${String(state.activeMonth) === String(m.month_index) ? 'active' : ''}`;
      btn.setAttribute('data-month', m.month_index);
      btn.textContent = m.name;
      btn.addEventListener('click', () => {
        dom.monthTabs.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeMonth = String(m.month_index);
        renderApp();
      });
      dom.monthTabs.appendChild(btn);
    });

    if (!validIndices.includes(String(state.activeMonth))) {
      state.activeMonth = 'all';
      allBtn.classList.add('active');
    }
  }

  function renderPdfOptions() {
    if (!state.calendar || !state.calendar.months || !dom.pdfTargetSelect) return;
    const currentVal = dom.pdfTargetSelect.value || 'cumulative';
    dom.pdfTargetSelect.innerHTML = '';

    state.calendar.months.forEach((m) => {
      const opt = document.createElement('option');
      opt.value = m.month_index;
      opt.textContent = `Bulan ${m.month_index} (${m.name} - ${m.weeks.length} Minggu)`;
      dom.pdfTargetSelect.appendChild(opt);
    });

    const cumulativeOpt = document.createElement('option');
    cumulativeOpt.value = 'cumulative';
    const totalWeeks = state.calendar.months.reduce((acc, m) => acc + (m.weeks ? m.weeks.length : 0), 0);
    const firstMonth = state.calendar.months[0]?.name?.split(' ')[0] || '';
    const lastMonth = state.calendar.months[state.calendar.months.length - 1]?.name?.split(' ')[0] || '';
    const rangeStr = firstMonth && lastMonth && firstMonth !== lastMonth ? `${firstMonth} - ${lastMonth}` : firstMonth;
    cumulativeOpt.textContent = `Lengkap Kumulatif (${rangeStr}, ${totalWeeks} Minggu)`;
    dom.pdfTargetSelect.appendChild(cumulativeOpt);

    const allOpt = document.createElement('option');
    allOpt.value = 'all';
    allOpt.textContent = `Kompilasi Seluruh Bundel (${state.calendar.months.length} Bulanan + 1 Kumulatif)`;
    dom.pdfTargetSelect.appendChild(allOpt);

    if ([...dom.pdfTargetSelect.options].some((o) => o.value === currentVal)) {
      dom.pdfTargetSelect.value = currentVal;
    } else {
      dom.pdfTargetSelect.value = 'cumulative';
    }
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
            <span>Minggu ke-${escapeHtml(week.minggu_ke)}</span>
            <span class="badge badge-primary">${escapeHtml(month.name)}</span>
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

          const status = (d.status || d.attendance_status || 'hadir').toLowerCase();
          const isNonHadir = status !== 'hadir';

          let previewText = '';
          let previewClasses = 'day-note-preview';
          if (isNonHadir) {
            previewClasses += ' text-danger';
            const statusLabel = status.charAt(0).toUpperCase() + status.slice(1);
            previewText = d.note ? `[${statusLabel}] ${d.note}` : `[Status: ${statusLabel}]`;
          } else if (d.note) {
            previewText = d.note;
          } else {
            previewClasses += ' empty';
            previewText = 'Belum ada catatan kegiatan';
          }

          const safeNoteText = escapeHtml(previewText);
          const datePart0 = d.tanggal_str ? d.tanggal_str.split(' ')[0] : '';
          const datePart1 = d.tanggal_str && d.tanggal_str.split(' ')[1] ? d.tanggal_str.split(' ')[1].slice(0, 3) : '';
          const metaStr = `${d.hari}, ${datePart0} ${datePart1}`;

          let hoursHtml = '';
          if (isNonHadir) {
            const badgeClass = STATUS_BADGES[status] || `badge-${status}`;
            hoursHtml = `<span class="badge ${badgeClass}">${escapeHtml(status.toUpperCase())}</span>`;
          } else {
            hoursHtml = `${escapeHtml(d.jam_masuk)}-${escapeHtml(d.jam_pulang)}`;
          }

          item.innerHTML = `
            <div class="day-meta">${escapeHtml(metaStr)}</div>
            <div class="day-hours">${hoursHtml}</div>
            <div class="${previewClasses}" title="${safeNoteText}">${safeNoteText}</div>
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

    // Attendance Status change in editor
    if (dom.editorStatus) {
      dom.editorStatus.addEventListener('change', (e) => {
        updateEditorStatusUI(e.target.value);
      });
    }

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
        const selectedStatus = dom.editorStatus ? dom.editorStatus.value : 'hadir';
        saveDayNote(state.activeEditingDay.date, dom.editorNote.value.trim(), selectedStatus);
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
      renderPdfOptions();
      openModal(dom.modalPdf);
    });
    dom.btnTriggerCompile.addEventListener('click', compileAndPreviewPdf);

    // Toggle Saturday row on schedule radio change
    document.querySelectorAll('input[name="cfg-hari-kerja"]').forEach((radio) => {
      radio.addEventListener('change', (e) => {
        toggleSaturdayRow(e.target.value);
      });
    });
  }

  // Boot
  document.addEventListener('DOMContentLoaded', () => {
    applyTheme(state.theme);
    initEvents();
    fetchCalendar();
  });
})();
