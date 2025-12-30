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

    fetch('/api/v1/students/', {
        credentials: 'include'
    })
        .then(resp => {
            if (!resp.ok) throw new Error('Failed to fetch students');
            return resp.json();
        })
        .then(data => {
            tbody.innerHTML = '';
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No students found. <a href="/students/create">Add a student</a></td></tr>';
                return;
            }
            data.forEach(s => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${s.id}</td>
                    <td>${s.name}</td>
                    <td>${s.age ?? ''}</td>
                    <td>${s.level}</td>
                    <td>${formatCurrency(s.price_per_class)}</td>
                    <td>
                      <a class="btn btn-sm btn-info" href="/students/${s.id}">View</a>
                      <button class="btn btn-sm btn-danger delete-btn" data-id="${s.id}">Delete</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            
            // Add delete handlers
            document.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', async function(e) {
                    e.preventDefault();
                    const studentId = this.getAttribute('data-id');
                    if (!confirm('Are you sure you want to delete this student?')) {
                        return;
                    }
                    
                    try {
                        const response = await fetch(`/api/v1/students/${studentId}`, {
                            method: 'DELETE',
                            credentials: 'include'
                        });
                        
                        if (response.ok) {
                            window.location.reload();
                        } else {
                            const error = await response.json();
                            alert('Error: ' + (error.detail || 'Failed to delete student'));
                        }
                    } catch (error) {
                        alert('Error: ' + error.message);
                    }
                });
            });
        })
        .catch(err => {
            console.error(err);
            const msg = err && err.status === 401 ?
                '<tr><td colspan="6">Please <a href="/auth/login">login</a> to view students.</td></tr>' :
                '<tr><td colspan="6">Could not load students.</td></tr>';
            tbody.innerHTML = msg;
        });
});