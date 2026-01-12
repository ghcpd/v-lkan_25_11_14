// State management
let currentPage = 1;
let pageSize = 10;
let currentSearch = '';
let currentSort = 'id';
let currentOrder = 'asc';
let deleteTargetId = null;
let editingUserId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('searchInput').addEventListener('input', debounce(() => {
        currentPage = 1;
        currentSearch = document.getElementById('searchInput').value;
        loadUsers();
    }, 300));

    document.getElementById('sortBy').addEventListener('change', () => {
        currentPage = 1;
        currentSort = document.getElementById('sortBy').value;
        loadUsers();
    });

    document.getElementById('sortOrder').addEventListener('change', () => {
        currentPage = 1;
        currentOrder = document.getElementById('sortOrder').value;
        loadUsers();
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API calls
async function loadUsers() {
    showLoading(true);
    try {
        const params = new URLSearchParams({
            search: currentSearch,
            page: currentPage,
            limit: pageSize,
            sort_by: currentSort,
            order: currentOrder
        });

        const response = await fetch(`/api/users?${params}`);
        if (!response.ok) {
            const error = await response.json();
            showError(error.error || 'Failed to load users');
            showEmptyState();
            return;
        }

        const data = await response.json();
        renderUsers(data);
        renderPagination(data);
    } catch (error) {
        showError('Network error: ' + error.message);
        showEmptyState();
    } finally {
        showLoading(false);
    }
}

function renderUsers(data) {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = '';

    if (!data.data || data.data.length === 0) {
        showEmptyState();
        return;
    }

    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('tableContainer').classList.remove('hidden');

    data.data.forEach(user => {
        const row = document.createElement('tr');
        row.className = 'table-row border-b border-gray-200';
        
        const roleBadgeClass = `badge-${user.role.toLowerCase()} text-white`;
        
        row.innerHTML = `
            <td class="px-6 py-4 font-semibold text-gray-800">#${user.id}</td>
            <td class="px-6 py-4">
                <div class="font-semibold text-gray-800">${escapeHtml(user.name)}</div>
            </td>
            <td class="px-6 py-4 text-gray-600">${escapeHtml(user.email)}</td>
            <td class="px-6 py-4">
                <span class="${roleBadgeClass} px-3 py-1 rounded-full text-sm font-medium">
                    ${user.role}
                </span>
            </td>
            <td class="px-6 py-4">
                <div class="flex justify-center gap-2">
                    <button onclick="openEditUserModal(${user.id})" 
                        class="px-3 py-2 rounded-lg bg-blue-100 text-blue-700 hover:bg-blue-200 font-medium text-sm transition-all">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="openDeleteModal(${user.id})" 
                        class="px-3 py-2 rounded-lg bg-red-100 text-red-700 hover:bg-red-200 font-medium text-sm transition-all">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function renderPagination(data) {
    const { page, pages, total, limit } = data;
    const paginationContainer = document.getElementById('paginationContainer');
    
    if (pages <= 1) {
        paginationContainer.classList.add('hidden');
        return;
    }

    paginationContainer.classList.remove('hidden');

    // Update page info
    const start = (page - 1) * limit + 1;
    const end = Math.min(page * limit, total);
    document.getElementById('pageInfo').textContent = `${start} to ${end} of ${total} users`;

    // Update buttons
    document.getElementById('prevBtn').disabled = page === 1;
    document.getElementById('nextBtn').disabled = page === pages;

    // Render page numbers
    const pageNumbersDiv = document.getElementById('pageNumbers');
    pageNumbersDiv.innerHTML = '';

    for (let i = 1; i <= pages; i++) {
        if (i === page) {
            const btn = document.createElement('button');
            btn.className = 'w-10 h-10 rounded-lg bg-purple-600 text-white font-semibold';
            btn.textContent = i;
            btn.disabled = true;
            pageNumbersDiv.appendChild(btn);
        } else if (i === 1 || i === pages || (i >= page - 1 && i <= page + 1)) {
            const btn = document.createElement('button');
            btn.className = 'w-10 h-10 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 font-medium';
            btn.textContent = i;
            btn.onclick = () => goToPage(i);
            pageNumbersDiv.appendChild(btn);
        } else if (i === 2 && page > 3) {
            const span = document.createElement('span');
            span.textContent = '...';
            span.className = 'px-2 text-gray-600';
            pageNumbersDiv.appendChild(span);
        } else if (i === pages - 1 && page < pages - 2) {
            const span = document.createElement('span');
            span.textContent = '...';
            span.className = 'px-2 text-gray-600';
            pageNumbersDiv.appendChild(span);
        }
    }
}

function goToPage(page) {
    currentPage = page;
    loadUsers();
    document.querySelector('.glass-effect').scrollIntoView({ behavior: 'smooth' });
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        loadUsers();
    }
}

function nextPage() {
    currentPage++;
    loadUsers();
}

// Modal operations
function openAddUserModal() {
    editingUserId = null;
    document.getElementById('userId').value = '';
    document.getElementById('userName').value = '';
    document.getElementById('userEmail').value = '';
    document.getElementById('userRole').value = '';
    document.getElementById('modalTitle').textContent = 'Add New User';
    document.getElementById('userModal').classList.remove('hidden');
}

async function openEditUserModal(userId) {
    editingUserId = userId;
    const response = await fetch(`/api/users/${userId}`);
    
    if (!response.ok) {
        showError('Failed to load user data');
        return;
    }

    const userData = await response.json();
    if (!userData.id) {
        showError('User not found');
        return;
    }

    document.getElementById('userId').value = userData.id;
    document.getElementById('userName').value = userData.name;
    document.getElementById('userEmail').value = userData.email;
    document.getElementById('userRole').value = userData.role;
    document.getElementById('modalTitle').textContent = `Edit User: ${userData.name}`;
    document.getElementById('userModal').classList.remove('hidden');
}

// Note: We need to add a GET endpoint for single user - let me update the API
async function saveUser(event) {
    event.preventDefault();

    const userId = document.getElementById('userId').value;
    const name = document.getElementById('userName').value;
    const email = document.getElementById('userEmail').value;
    const role = document.getElementById('userRole').value;

    if (!name || !email || !role) {
        showError('All fields are required');
        return;
    }

    try {
        let response;
        if (userId) {
            response = await fetch(`/api/users/${userId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, role })
            });
        } else {
            response = await fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, role })
            });
        }

        if (!response.ok) {
            const error = await response.json();
            showError(error.error || 'Failed to save user');
            return;
        }

        showSuccess(userId ? 'User updated successfully' : 'User created successfully');
        closeUserModal();
        currentPage = 1;
        loadUsers();
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

function closeUserModal() {
    document.getElementById('userModal').classList.add('hidden');
    editingUserId = null;
}

function openDeleteModal(userId) {
    deleteTargetId = userId;
    document.getElementById('deleteModal').classList.remove('hidden');
}

async function confirmDelete() {
    if (!deleteTargetId) return;

    try {
        const response = await fetch(`/api/users/${deleteTargetId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            showError(error.error || 'Failed to delete user');
            return;
        }

        showSuccess('User deleted successfully');
        closeDeleteModal();
        currentPage = 1;
        loadUsers();
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.add('hidden');
    deleteTargetId = null;
}

// Export functionality
async function exportUsers(format) {
    try {
        window.location.href = `/api/users/export?format=${format}`;
        showSuccess(`Exporting users as ${format.toUpperCase()}...`);
    } catch (error) {
        showError('Failed to export users: ' + error.message);
    }
}

// UI helpers
function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    const container = document.getElementById('tableContainer');
    if (show) {
        spinner.classList.remove('hidden');
        container.classList.add('hidden');
    } else {
        spinner.classList.add('hidden');
        container.classList.remove('hidden');
    }
}

function showEmptyState() {
    document.getElementById('emptyState').classList.remove('hidden');
    document.getElementById('tableContainer').classList.add('hidden');
    document.getElementById('paginationContainer').classList.add('hidden');
}

function showError(message) {
    const banner = document.getElementById('errorBanner');
    document.getElementById('errorMessage').textContent = message;
    banner.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(hideError, 5000);
}

function hideError() {
    document.getElementById('errorBanner').classList.add('hidden');
}

function showSuccess(message) {
    const toast = document.getElementById('successToast');
    document.getElementById('successMessage').textContent = message;
    toast.classList.remove('hidden');
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
