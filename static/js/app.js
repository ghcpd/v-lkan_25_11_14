const state = {
    page: 1,
    limit: 8,
    totalPages: 1,
    search: '',
    sortBy: 'name',
    sortOrder: 'asc',
    users: [],
};

const elements = {
    tableBody: document.getElementById('userTable'),
    paginationInfo: document.getElementById('paginationInfo'),
    prevPage: document.getElementById('prevPage'),
    nextPage: document.getElementById('nextPage'),
    searchInput: document.getElementById('searchInput'),
    limitSelect: document.getElementById('limitSelect'),
    errorBanner: document.getElementById('errorBanner'),
    errorMessage: document.getElementById('errorMessage'),
    dismissError: document.getElementById('dismissError'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    addUserBtn: document.getElementById('addUserBtn'),
    exportCsvBtn: document.getElementById('exportCsvBtn'),
    exportJsonBtn: document.getElementById('exportJsonBtn'),
    modal: document.getElementById('userModal'),
    confirmModal: document.getElementById('confirmModal'),
    modalTitle: document.getElementById('modalTitle'),
    userForm: document.getElementById('userForm'),
    nameInput: document.getElementById('nameInput'),
    emailInput: document.getElementById('emailInput'),
    roleInput: document.getElementById('roleInput'),
    userIdInput: document.getElementById('userId'),
    confirmMessage: document.getElementById('confirmMessage'),
    confirmDelete: document.getElementById('confirmDelete'),
    emptyState: document.getElementById('emptyState'),
};

let deleteTargetId = null;
let searchDebounce;

const toggleLoading = (show) => {
    if (!elements.loadingOverlay) return;
    elements.loadingOverlay.classList.toggle('invisible', !show);
    elements.loadingOverlay.style.visibility = show ? 'visible' : 'hidden';
    elements.loadingOverlay.style.opacity = show ? '1' : '0';
};

const showError = (message) => {
    elements.errorMessage.textContent = message;
    elements.errorBanner.classList.remove('hidden');
};

const hideError = () => {
    elements.errorBanner.classList.add('hidden');
};

const openModal = () => {
    elements.modal.dataset.open = 'true';
    elements.modal.setAttribute('aria-hidden', 'false');
};

const closeModal = () => {
    elements.modal.dataset.open = 'false';
    elements.modal.setAttribute('aria-hidden', 'true');
    elements.userForm.reset();
    elements.userIdInput.value = '';
};

const openConfirmModal = () => {
    elements.confirmModal.dataset.open = 'true';
    elements.confirmModal.setAttribute('aria-hidden', 'false');
};

const closeConfirmModal = () => {
    elements.confirmModal.dataset.open = 'false';
    elements.confirmModal.setAttribute('aria-hidden', 'true');
    deleteTargetId = null;
};
const renderUsers = () => {
    if (state.users.length === 0) {
        elements.emptyState.classList.remove('hidden');
        elements.tableBody.innerHTML = '';
    } else {
        elements.emptyState.classList.add('hidden');
        const rows = state.users
            .map((user) => {
                return [
                    '<tr class="hover:bg-white/5 transition">',
                    '    <td class="py-4 pr-6">',
                    '        <div class="font-semibold text-white">' + user.name + '</div>',
                    '        <p class="text-xs text-white/50">ID #' + user.id + '</p>',
                    '    </td>',
                    '    <td class="py-4 pr-6">' + user.email + '</td>',
                    '    <td class="py-4 pr-6">' + user.role + '</td>',
                    '    <td class="py-4 text-right">',
                    '        <button class="text-accent hover:underline mr-4" data-edit="' + user.id + '">Edit</button>',
                    '        <button class="text-red-300 hover:underline" data-delete="' + user.id + '" data-name="' + user.name + '">Delete</button>',
                    '    </td>',
                    '</tr>',
                ].join('\n');
            })
            .join('');
        elements.tableBody.innerHTML = rows;
    }

    elements.paginationInfo.textContent =
        'Page ' + state.page + ' of ' + (state.totalPages || 1);
    elements.prevPage.disabled = state.page === 1;
    elements.nextPage.disabled = state.page === state.totalPages;
    elements.prevPage.classList.toggle('opacity-40', elements.prevPage.disabled);
    elements.nextPage.classList.toggle('opacity-40', elements.nextPage.disabled);

    document.querySelectorAll('.sort-btn').forEach((btn) => {
        const active = btn.dataset.sort === state.sortBy;
        btn.classList.toggle('text-white', active);
        btn.classList.toggle('text-white/60', !active);
        const label = btn.dataset.sortLabel || btn.textContent.split(' ')[0];
        btn.dataset.sortLabel = label;
        const arrow = active ? (state.sortOrder === 'asc' ? '▴' : '▾') : '';
        btn.textContent = label + ' ' + arrow;
    });
};
const fetchUsers = async () => {
    toggleLoading(true);
    hideError();
    try {
        const params = new URLSearchParams({
            page: state.page,
            limit: state.limit,
            search: state.search,
            sort_by: state.sortBy,
            order: state.sortOrder,
        });
        const response = await fetch('/api/users?' + params.toString());
        const payload = await response.json();
        if (!response.ok) {
            throw new Error(payload.error || 'Unable to load users');
        }
        state.users = payload.users;
        state.totalPages = payload.total_pages;
        renderUsers();
    } catch (error) {
        showError(error.message);
    } finally {
        toggleLoading(false);
    }
};

const saveUser = async (event) => {
    event.preventDefault();
    const payload = {
        name: elements.nameInput.value.trim(),
        email: elements.emailInput.value.trim(),
        role: elements.roleInput.value.trim(),
    };

    const userId = elements.userIdInput.value;
    const method = userId ? 'PUT' : 'POST';
    const url = userId ? '/api/users/' + userId : '/api/users';

    toggleLoading(true);
    hideError();

    try {
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.error || 'Unable to save user');
        }
        closeModal();
        await fetchUsers();
    } catch (error) {
        showError(error.message);
    } finally {
        toggleLoading(false);
    }
};

const deleteUser = async () => {
    if (!deleteTargetId) return;
    toggleLoading(true);
    hideError();
    try {
        const response = await fetch('/api/users/' + deleteTargetId, {
            method: 'DELETE',
        });
        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.error || 'Unable to delete user');
        }
        closeConfirmModal();
        await fetchUsers();
    } catch (error) {
        showError(error.message);
    } finally {
        toggleLoading(false);
    }
};
const handleTableClick = (event) => {
    const editBtn = event.target.closest('[data-edit]');
    const deleteBtn = event.target.closest('[data-delete]');

    if (editBtn) {
        const user = state.users.find((u) => String(u.id) === editBtn.dataset.edit);
        if (!user) return;
        elements.modalTitle.textContent = 'Edit user';
        elements.userIdInput.value = user.id;
        elements.nameInput.value = user.name;
        elements.emailInput.value = user.email;
        elements.roleInput.value = user.role;
        openModal();
    }

    if (deleteBtn) {
        deleteTargetId = deleteBtn.dataset.delete;
        elements.confirmMessage.textContent =
            'Delete ' + deleteBtn.dataset.name + '? This action cannot be undone.';
        openConfirmModal();
    }
};

const handleSortClick = (event) => {
    const button = event.target.closest('.sort-btn');
    if (!button) return;
    const selectedSort = button.dataset.sort;
    if (state.sortBy === selectedSort) {
        state.sortOrder = state.sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        state.sortBy = selectedSort;
        state.sortOrder = 'asc';
    }
    state.page = 1;
    fetchUsers();
};

const init = () => {
    elements.userForm.addEventListener('submit', saveUser);
    elements.tableBody.addEventListener('click', handleTableClick);
    document.querySelectorAll('[data-close-modal]').forEach((btn) => {
        btn.addEventListener('click', () => {
            closeModal();
            closeConfirmModal();
        });
    });

    elements.confirmDelete.addEventListener('click', deleteUser);

    elements.addUserBtn.addEventListener('click', () => {
        elements.modalTitle.textContent = 'Add user';
        openModal();
    });

    elements.dismissError.addEventListener('click', hideError);

    elements.prevPage.addEventListener('click', () => {
        if (state.page === 1) return;
        state.page -= 1;
        fetchUsers();
    });

    elements.nextPage.addEventListener('click', () => {
        if (state.page >= state.totalPages) return;
        state.page += 1;
        fetchUsers();
    });

    elements.limitSelect.addEventListener('change', (event) => {
        state.limit = Number(event.target.value);
        state.page = 1;
        fetchUsers();
    });

    elements.searchInput.addEventListener('input', (event) => {
        clearTimeout(searchDebounce);
        const value = event.target.value;
        searchDebounce = setTimeout(() => {
            state.search = value;
            state.page = 1;
            fetchUsers();
        }, 300);
    });

    document.querySelectorAll('.sort-btn').forEach((btn) => {
        btn.addEventListener('click', handleSortClick);
    });

    elements.exportCsvBtn.addEventListener('click', () => {
        window.location.href = '/api/users/export?format=csv';
    });

    elements.exportJsonBtn.addEventListener('click', () => {
        window.location.href = '/api/users/export?format=json';
    });

    fetchUsers();
};

window.addEventListener('DOMContentLoaded', init);
