const API_BASE = '/api/users';
let page = 1;
let limit = 10;
let sort_by = 'name';
let order = 'asc';
let search = '';
let total = 0;
let editingUserId = null;
let deletingUserId = null;

const userTableBody = document.getElementById('userTableBody');
const errorBanner = document.getElementById('errorBanner');

function showError(msg) {
  errorBanner.textContent = msg;
  errorBanner.classList.remove('hidden');
}

function clearError() {
  errorBanner.classList.add('hidden');
  errorBanner.textContent = '';
}

async function fetchUsers() {
  clearError();
  userTableBody.innerHTML = `<tr><td colspan="4" class="p-6 text-center text-slate-400">Loading users...</td></tr>`;
  try {
    const params = new URLSearchParams({search: search || '', page, limit, sort_by, order});
    const res = await fetch(`${API_BASE}?${params.toString()}`);
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || 'Failed to fetch users');
      userTableBody.innerHTML = `<tr><td colspan="4" class="p-6 text-center text-slate-400">Error loading users</td></tr>`;
      return;
    }
    renderUsers(data.users);
    total = data.total || data.users.length;
    document.getElementById('totalCount').textContent = `Total: ${total}`;
    document.getElementById('pageIndicator').textContent = page;
  } catch (err) {
    showError(err.message || 'Network error');
    userTableBody.innerHTML = `<tr><td colspan="4" class="p-6 text-center text-slate-400">Network error</td></tr>`;
  }
}

function renderUsers(users) {
  if (!users || users.length === 0) {
    userTableBody.innerHTML = `<tr class=""><td colspan="4" class="p-6 text-center text-slate-400">No users found</td></tr>`;
    return;
  }
  userTableBody.innerHTML = '';
  users.forEach(u => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50';
    tr.innerHTML = `
      <td class="px-6 py-4">${escapeHtml(u.name)}</td>
      <td class="px-6 py-4">${escapeHtml(u.email)}</td>
      <td class="px-6 py-4">${escapeHtml(u.role)}</td>
      <td class="px-6 py-4 text-right">
        <button class="editBtn mr-2 text-sky-600 hover:underline" data-id="${u.id}">Edit</button>
        <button class="deleteBtn text-red-600 hover:underline" data-id="${u.id}">Delete</button>
      </td>
    `;
    userTableBody.appendChild(tr);
  });
  // attach handlers
  document.querySelectorAll('.editBtn').forEach(btn => btn.addEventListener('click', (e) => {
    const id = e.target.dataset.id;
    startEditUser(id);
  }));
  document.querySelectorAll('.deleteBtn').forEach(btn => btn.addEventListener('click', (e) => {
    const id = e.target.dataset.id;
    promptDeleteUser(id);
  }));
}

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/\'/g, "&#039;");
}

// Add/Edit modal handlers
const userModal = document.getElementById('userModal');
const modalTitle = document.getElementById('modalTitle');
const userNameInput = document.getElementById('userName');
const userEmailInput = document.getElementById('userEmail');
const userRoleInput = document.getElementById('userRole');

function showModal() { userModal.classList.remove('hidden'); }
function hideModal() { userModal.classList.add('hidden'); }

// close modal on Escape
window.addEventListener('keydown', (e) => { if (e.key === 'Escape') { hideModal(); hideDeleteModal(); } });

// click backdrop to close
userModal.addEventListener('click', (e) => { if (e.target === userModal) hideModal(); });

document.getElementById('showAddModal').addEventListener('click', () => {
  editingUserId = null;
  modalTitle.textContent = 'Add user';
  userNameInput.value = '';
  userEmailInput.value = '';
  userRoleInput.value = 'viewer';
  showModal();
});

document.getElementById('cancelModal').addEventListener('click', () => { hideModal(); });

async function startEditUser(id) {
  clearError();
  try {
    const res = await fetch(`${API_BASE}?search=&page=1&limit=100&sort_by=id&order=asc`);
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || 'Failed to fetch user');
      return;
    }
    const user = data.users.find(u => u.id === id);
    if (!user) { showError('User not found'); return; }
    editingUserId = id;
    modalTitle.textContent = 'Edit user';
    userNameInput.value = user.name;
    userEmailInput.value = user.email;
    userRoleInput.value = user.role;
    showModal();
  } catch (err) {
    showError(err.message || 'Network error');
  }
}

// Save/New user
document.getElementById('saveUser').addEventListener('click', async () => {
  clearError();
  const name = userNameInput.value.trim();
  const email = userEmailInput.value.trim();
  const role = userRoleInput.value;
  if (!name || !email) { showError('Name and email are required'); return; }
  const saveBtn = document.getElementById('saveUser');
  saveBtn.disabled = true;
  const origText = saveBtn.textContent;
  saveBtn.textContent = 'Saving...';
  try {
    const body = { name, email, role };
    let res;
    if (editingUserId) {
      res = await fetch(`${API_BASE}/${editingUserId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    } else {
      res = await fetch(API_BASE, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    }
    const data = await res.json();
    if (!res.ok) { showError(data.error || 'Failed to save user'); return; }
    hideModal();
    fetchUsers();
  } catch (err) {
    showError(err.message || 'Network error');
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = origText;
  }
});

// Delete handlers
const deleteModal = document.getElementById('deleteModal');
function showDeleteModal() { deleteModal.classList.remove('hidden'); }
function hideDeleteModal() { deleteModal.classList.add('hidden'); }

// backdrop click to close delete modal
deleteModal.addEventListener('click', (e) => { if (e.target === deleteModal) hideDeleteModal(); });

function promptDeleteUser(id) {
  deletingUserId = id;
  showDeleteModal();
}

document.getElementById('cancelDelete').addEventListener('click', () => { hideDeleteModal(); });

document.getElementById('confirmDelete').addEventListener('click', async () => {
  clearError();
  if (!deletingUserId) return;
  try {
    const res = await fetch(`${API_BASE}/${deletingUserId}`, { method: 'DELETE' });
    const data = await res.json();
    if (!res.ok) { showError(data.error || 'Failed to delete user'); return; }
    hideDeleteModal();
    fetchUsers();
  } catch (err) {
    showError(err.message || 'Network error');
  }
});

// Search and controls
document.getElementById('searchBtn').addEventListener('click', () => { search = document.getElementById('searchInput').value.trim(); page = 1; fetchUsers(); });

document.getElementById('limit').addEventListener('change', (e) => { limit = +e.target.value; page = 1; fetchUsers(); });
document.getElementById('sortBy').addEventListener('change', (e) => { sort_by = e.target.value; fetchUsers(); });
document.getElementById('order').addEventListener('change', (e) => { order = e.target.value; fetchUsers(); });

document.getElementById('prevPage').addEventListener('click', () => { if (page > 1) { page -= 1; fetchUsers(); } });
document.getElementById('nextPage').addEventListener('click', () => { const lastPage = Math.ceil(total / limit); if (page < lastPage) { page += 1; fetchUsers(); } });

// Export
document.getElementById('exportCsv').addEventListener('click', () => { window.location = `${API_BASE}/export?format=csv`; });
document.getElementById('exportJson').addEventListener('click', () => { window.location = `${API_BASE}/export?format=json`; });

// init
fetchUsers();
