// Utility functions for the frontend

// Show loading state on form submit
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Loading...';
            }
        });

    // Modal Confirm handler: when user clicks Download in modal
    document.getElementById('confirmDownloadReportBtn')?.addEventListener('click', async function() {
        const studentId = document.getElementById('reportStudentId').value;
        const studentName = document.getElementById('reportStudentName').value || `student_${studentId}`;
        const startDate = document.getElementById('reportStartDate').value;
        const endDate = document.getElementById('reportEndDate').value;
        const errorEl = document.getElementById('reportDateError');
        // Basic presence check
        if (!studentId || !startDate || !endDate) {
            if (errorEl) { errorEl.style.display = 'block'; errorEl.textContent = 'Please provide both start and end dates.'; }
            return;
        }

        // Validate that end >= start
        const s = new Date(startDate);
        const e = new Date(endDate);
        if (e < s) {
            if (errorEl) { errorEl.style.display = 'block'; errorEl.textContent = 'End date cannot be earlier than start date.'; }
            return;
        }

        // clear any previous error
        if (errorEl) { errorEl.style.display = 'none'; errorEl.textContent = ''; }

        // close modal
        const modalEl = document.getElementById('reportDateModal');
        const bsModal = bootstrap.Modal.getInstance(modalEl);
        if (bsModal) bsModal.hide();

        try {
            const attendanceResp = await fetch(`/api/v1/attendance/?student_id=${studentId}&start_date=${startDate}&end_date=${endDate}`, { credentials: 'include' });
            if (!attendanceResp.ok) throw new Error('Failed to fetch attendance');
            const attendance = await attendanceResp.json();

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            const pageWidth = doc.internal.pageSize.getWidth();
            doc.setFontSize(18);
            doc.text('Individual Student Report', pageWidth / 2, 20, { align: 'center' });
            doc.setFontSize(12);
            doc.text(`${studentName}`, pageWidth / 2, 28, { align: 'center' });
            doc.setFontSize(10);
            doc.text(`Period: ${new Date(startDate).toLocaleDateString()} - ${new Date(endDate).toLocaleDateString()}`, pageWidth / 2, 35, { align: 'center' });

            const classes = attendance.length;
            let pricePerClass = 0;
            const found = studentsData.find(x => x.id == studentId);
            if (found) pricePerClass = parseFloat(found.price_per_class || 0);
            const totalFees = classes * pricePerClass;

            doc.setFontSize(11);
            doc.text(`Classes Attended: ${classes}`, 20, 45);
            doc.text(`Price per Class: £${pricePerClass.toFixed(2)}`, 20, 52);
            doc.setFont(undefined, 'bold');
            doc.text(`Total Fees: £${totalFees.toFixed(2)}`, 20, 59);
            doc.setFont(undefined, 'normal');

            const rows = attendance.map(a => [new Date(a.date).toLocaleDateString()]);
            doc.autoTable({ startY: 70, head: [['Date']], body: rows, theme: 'grid', headStyles: { fillColor: [41, 128, 185] } });

            const timestamp = new Date().toISOString().split('T')[0];
            doc.save(`attendance-report-${studentName.replace(/\s+/g, '_')}-${timestamp}.pdf`);
        } catch (err) {
            alert('Error generating report: ' + err.message);
        }
    });

    // Clear inline error when user changes date inputs
    const startEl = document.getElementById('reportStartDate');
    const endEl = document.getElementById('reportEndDate');
    const errorEl = document.getElementById('reportDateError');
    [startEl, endEl].forEach(el => {
        if (!el) return;
        el.addEventListener('input', () => {
            if (errorEl) { errorEl.style.display = 'none'; errorEl.textContent = ''; }
        });
    });
    });
});

// Confirm dangerous actions
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to perform this action?');
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-GB', {
        style: 'currency',
        currency: 'GBP'
    }).format(amount);
}

// Populate students table on the /students page
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname !== '/students') return;

    const tbody = document.querySelector('table.table tbody');
    if (!tbody) return;

    // load students and enable client-side sorting
    let studentsData = [];
    let currentSort = { key: 'name', dir: 'asc' };

    fetch('/api/v1/students/', { credentials: 'include' })
        .then(resp => {
            if (!resp.ok) throw new Error('Failed to fetch students');
            return resp.json();
        })
        .then(data => {
            studentsData = data;

            const renderStudents = () => {
                tbody.innerHTML = '';
                if (!studentsData || studentsData.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center">No students found. <a href="/students/create">Add a student</a></td></tr>';
                    return;
                }

                const sorted = [...studentsData].sort((a, b) => {
                    const k = currentSort.key;
                    let va = a[k];
                    let vb = b[k];
                    if (va == null) va = '';
                    if (vb == null) vb = '';
                    if (typeof va === 'string') va = va.toLowerCase();
                    if (typeof vb === 'string') vb = vb.toLowerCase();
                    if (va < vb) return currentSort.dir === 'asc' ? -1 : 1;
                    if (va > vb) return currentSort.dir === 'asc' ? 1 : -1;
                    return 0;
                });

                sorted.forEach(s => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${s.name}</td>
                        <td>${s.age ?? ''}</td>
                        <td>${s.level}</td>
                        <td>${formatCurrency(s.price_per_class)}</td>
                                    <td class="actions">
                                        <a class="btn btn-sm btn-info" href="/students/${s.id}">View</a>
                                        <a class="btn btn-sm btn-warning" href="/students/${s.id}/edit">Edit</a>
                                        <button class="btn btn-sm btn-outline-primary download-report-btn" data-id="${s.id}" data-name="${s.name}">Download Report</button>
                                        <button class="btn btn-sm btn-danger delete-btn" data-id="${s.id}">Delete</button>
                                    </td>
                    `;
                    tbody.appendChild(tr);
                });

                // attach delete handlers
                document.querySelectorAll('.delete-btn').forEach(btn => {
                    btn.addEventListener('click', async function(e) {
                        e.preventDefault();
                        const studentId = this.getAttribute('data-id');
                        if (!confirm('Are you sure you want to delete this student?')) return;
                        try {
                            const response = await fetch(`/api/v1/students/${studentId}`, { method: 'DELETE', credentials: 'include' });
                            if (response.ok) {
                                studentsData = studentsData.filter(x => x.id != studentId);
                                renderStudents();
                            } else {
                                const error = await response.json();
                                alert('Error: ' + (error.detail || 'Failed to delete student'));
                            }
                        } catch (err) {
                            alert('Error: ' + err.message);
                        }
                    });
                });

                // attach download handlers - open modal to choose date range
                document.querySelectorAll('.download-report-btn').forEach(btn => {
                    btn.addEventListener('click', function(e) {
                        e.preventDefault();
                        const studentId = this.dataset.id;
                        const studentName = this.dataset.name || `student_${studentId}`;

                        // Set hidden fields in modal and default dates
                        const today = new Date();
                        const start = new Date(today.getFullYear(), today.getMonth(), 1);
                        const startStr = start.toISOString().split('T')[0];
                        const endStr = today.toISOString().split('T')[0];

                        document.getElementById('reportStudentId').value = studentId;
                        document.getElementById('reportStudentName').value = studentName;
                        document.getElementById('reportStartDate').value = startStr;
                        document.getElementById('reportEndDate').value = endStr;

                        const modalEl = document.getElementById('reportDateModal');
                        const modal = new bootstrap.Modal(modalEl);
                        modal.show();
                    });
                });
            };

            // setup header sorting
            const headers = document.querySelectorAll('th.sortable');
            headers.forEach(h => {
                h.addEventListener('click', () => {
                    const key = h.dataset.key;
                    if (currentSort.key === key) currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
                    else { currentSort.key = key; currentSort.dir = 'asc'; }
                    headers.forEach(hh => hh.querySelector('.sort-indicator').textContent = '');
                    h.querySelector('.sort-indicator').textContent = currentSort.dir === 'asc' ? '▲' : '▼';
                    renderStudents();
                });
            });

            // default indicator and render
            const defaultH = document.querySelector('th.sortable[data-key="name"]');
            if (defaultH) defaultH.querySelector('.sort-indicator').textContent = '▲';
            renderStudents();
        })
        .catch(err => {
            console.error(err);
            const msg = err && err.status === 401 ?
                '<tr><td colspan="5">Please <a href="/auth/login">login</a> to view students.</td></tr>' :
                '<tr><td colspan="5">Could not load students.</td></tr>';
            tbody.innerHTML = msg;
        });
});