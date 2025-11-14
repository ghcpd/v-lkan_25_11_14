/* Global frontend for User Management Dashboard */

const state = {
  page: 1,
  limit: Number(document.getElementById('limitSelect')?.value || 10),
  search: '',
  sort_by: 'id',
  order: 'asc',
  total: 0,
  users: []
}

const el = {
  tableBody: document.getElementById('tableBody'),
  summary: document.getElementById('tableSummary'),
  pagination: document.getElementById('pagination'),
  searchInput: document.getElementById('searchInput'),
  limitSelect: document.getElementById('limitSelect'),
  btnAdd: document.getElementById('btnAdd'),
  btnExport: document.getElementById('btnExport'),
  modalBackdrop: document.getElementById('modalBackdrop'),
  modalTitle: document.getElementById('modalTitle'),
  modalClose: document.getElementById('modalClose'),
  modalCancel: document.getElementById('modalCancel'),
  modalForm: document.getElementById('modalForm'),
  modalFormStatus: document.getElementById('modalStatus'),
  fName: document.getElementById('fName'),
  fEmail: document.getElementById('fEmail'),
  fRole: document.getElementById('fRole'),
  modalSubtitle: document.getElementById('modalSubtitle'),
  errorBanner: document.getElementById('errorBanner'),
  errorText: document.getElementById('errorBannerText'),
  hideError: document.getElementById('hideError'),
  confirmBackdrop: document.getElementById('confirmBackdrop'),
  confirmText: document.getElementById('confirmText'),
  confirmOK: document.getElementById('confirmOK'),
  confirmCancel: document.getElementById('confirmCancel'),
}

let editingUserId = null
let deleteUserId = null
let searchTimer = null

function showError(message, timeout=8000) {
  el.errorText.innerText = message
  el.errorBanner.classList.remove('hidden')
  window.clearTimeout(el.errorBanner.dismissTimer)
  el.errorBanner.dismissTimer = window.setTimeout(() => {
    el.errorBanner.classList.add('hidden')
  }, timeout)
}

el.hideError.addEventListener('click', () => {
  el.errorBanner.classList.add('hidden')
})

// Helpers

async function fetchUsers() {
  try {
    el.tableBody.innerHTML = '<tr class="text-center text-sm text-slate-500"><td colspan="4" class="p-8">Loading...</td></tr>'
    const params = new URLSearchParams({
      page: String(state.page),
      limit: String(state.limit),
      search: state.search,
      sort_by: state.sort_by,
      order: state.order,
    })
    const res = await fetch(`/api/users?${params.toString()}`)
    if (!res.ok) {
      const payload = await res.json().catch(()=>({error:'Unknown error'}))
      throw new Error(payload.error || 'Failed to fetch users')
    }
    const payload = await res.json()
    state.users = payload.users || payload
    state.total = payload.total || 0
    renderTable()
  } catch(e) {
    console.error(e)
    showError(e.message)
    el.tableBody.innerHTML = '<tr class="text-center text-sm text-red-500"><td colspan="4" class="p-8">Failed to load users</td></tr>'
  }
}

function renderTable() {
  if (!state.users || state.users.length === 0) {
    el.tableBody.innerHTML = '<tr><td colspan="4" class="p-8 text-center text-sm text-slate-500">No users found. Add one using the "Add user" button.</td></tr>'
    el.summary.innerHTML = 'No results'
    el.pagination.innerHTML = ''
    return
  }
  const rows = state.users.map(u => {
    return `<tr class="hover:bg-slate-50 transition-colors border-b">
      <td class="p-4 align-top">
        <div class="font-medium text-slate-800">${escapeHtml(u.name)}</div>
        <div class="text-xs text-slate-500">ID: ${u.id}</div>
      </td>
      <td class="p-4 align-top">
        <div class="text-sm text-slate-700">${escapeHtml(u.email)}</div>
      </td>
      <td class="p-4 align-top">
        <span class="inline-block bg-indigo-100 text-indigo-800 rounded-full text-xs px-3 py-1">${escapeHtml(u.role)}</span>
      </td>
      <td class="p-4 text-right align-top">
        <button data-id="${u.id}" class="editBtn mr-2 text-slate-700 hover:text-indigo-600">Edit</button>
        <button data-id="${u.id}" class="delBtn text-red-600 hover:text-red-800">Delete</button>
      </td>
    </tr>`
  })
  el.tableBody.innerHTML = rows.join('\n')
  el.summary.innerHTML = `Showing ${state.users.length} users — Page ${state.page}`
  renderPagination()
  attachRowEvents()
}

function attachRowEvents() {
  document.querySelectorAll('.editBtn').forEach(b => {
    b.addEventListener('click', (e) => {
      const id = Number(e.currentTarget.dataset.id)
      const user = state.users.find(x => x.id === id)
      openModal('edit', user)
    })
  })
  document.querySelectorAll('.delBtn').forEach(b => {
    b.addEventListener('click', (e) => {
      deleteUserId = Number(e.currentTarget.dataset.id)
      el.confirmBackdrop.classList.remove('hidden')
      const user = state.users.find(x => x.id === deleteUserId)
      el.confirmText.innerText = `Are you sure you want to delete ${user.name} (${user.email})?`;
    })
  })
}

function renderPagination() {
  const totalPages = Math.max(1, Math.ceil((state.total || 1) / state.limit))
  el.pagination.innerHTML = ''
  const frag = document.createDocumentFragment()
  const prev = document.createElement('button')
  prev.className = 'px-3 py-1 border rounded-md text-sm'
  prev.innerText = 'Prev'
  prev.disabled = state.page <= 1
  prev.addEventListener('click', () => { if (state.page > 1) { state.page--; fetchUsers() }})
  frag.appendChild(prev)

  const mid = document.createElement('div')
  mid.className = 'flex items-center gap-2 px-3 text-sm text-slate-600'
  mid.innerText = `Page ${state.page} / ${totalPages}`
  frag.appendChild(mid)

  const next = document.createElement('button')
  next.className = 'px-3 py-1 border rounded-md text-sm'
  next.innerText = 'Next'
  next.disabled = state.page >= totalPages
  next.addEventListener('click', () => { if (state.page < totalPages) { state.page++; fetchUsers() } })
  frag.appendChild(next)

  el.pagination.appendChild(frag)
}

// Sorting - table header clicks
document.querySelectorAll('th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    const key = th.dataset.sort
    if (state.sort_by === key) state.order = state.order === 'asc' ? 'desc' : 'asc'
    else { state.sort_by = key; state.order = 'asc' }
    fetchUsers()
  })
})

// Limit change
el.limitSelect.addEventListener('change', () => {
  state.limit = Number(el.limitSelect.value)
  state.page = 1
  fetchUsers()
})

// Search debounce
el.searchInput.addEventListener('input', () => {
  const q = el.searchInput.value.trim()
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => {
    state.search = q
    state.page = 1
    fetchUsers()
  }, 380)
})

// Add user
el.btnAdd.addEventListener('click', () => openModal('add'))

function openModal(mode, user=null) {
  editingUserId = user?.id || null
  el.modalBackdrop.classList.remove('hidden')
  if (mode === 'add') {
    el.modalTitle.innerText = 'Add user'
    el.modalSubtitle.innerText = 'Create a new user account '
    el.fName.value = ''
    el.fEmail.value = ''
    el.fRole.value = window.ROLES[0] || ''
    el.modalFormStatus.innerText = ''
  } else {
    el.modalTitle.innerText = 'Edit user'
    el.modalSubtitle.innerText = 'Update user details'
    el.fName.value = user.name
    el.fEmail.value = user.email
    el.fRole.value = user.role
    el.modalFormStatus.innerText = ''
  }
}

el.modalClose.addEventListener('click', closeModal)
el.modalCancel.addEventListener('click', closeModal)

function closeModal() {
  editingUserId = null
  el.modalBackdrop.classList.add('hidden')
}

el.modalForm.addEventListener('submit', async (e) => {
  e.preventDefault()
  el.modalFormStatus.innerText = 'Saving...'
  const payload = { name: el.fName.value.trim(), email: el.fEmail.value.trim(), role: el.fRole.value }
  try {
    // Basic validation
    if (!payload.name || !payload.email || !payload.role) throw new Error('All fields are required')
    let res
    el.modalForm.querySelectorAll('button').forEach(b => b.disabled = true)
    if (editingUserId) {
      res = await fetch(`/api/users/${editingUserId}`, {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)})
    } else {
      res = await fetch('/api/users', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)})
    }
    const data = await res.json().catch(() => null)
    if (!res.ok) throw new Error(data && data.error ? data.error : 'Failed to save user')
    // success
    el.modalForm.querySelectorAll('button').forEach(b => b.disabled = false)
    closeModal()
    fetchUsers()
  } catch(err) {
    el.modalFormStatus.innerText = 'Failed: ' + err.message
    showError(err.message)
    el.modalForm.querySelectorAll('button').forEach(b => b.disabled = false)
  }
})

// Delete
el.confirmCancel.addEventListener('click', () => { deleteUserId = null; el.confirmBackdrop.classList.add('hidden') })
el.confirmOK.addEventListener('click', async () => {
  try {
    el.confirmOK.innerText = 'Deleting...'
    const res = await fetch(`/api/users/${deleteUserId}`, {method: 'DELETE'})
    if (!res.ok) {
      const data = await res.json().catch(()=>({error:'Unknown error'}))
      throw new Error(data.error || 'Failed to delete')
    }
    deleteUserId = null
    el.confirmBackdrop.classList.add('hidden')
    el.confirmOK.innerText = 'Delete'
    fetchUsers()
  } catch(err) {
    showError(err.message)
    el.confirmOK.innerText = 'Delete'
  }
})

// Export
el.btnExport.addEventListener('click', async () => {
  try {
    // allow user to pick format quickly
    let desiredFmt = prompt('Export format: csv or json', 'csv') || 'csv'
    desiredFmt = desiredFmt.trim().toLowerCase()
    if (desiredFmt !== 'csv' && desiredFmt !== 'json') {
      showError('Invalid format selected. Choose csv or json')
      return
    }
    const url = `/api/users/export?format=${desiredFmt}`
    el.btnExport.innerText = 'Exporting...'
    el.btnExport.disabled = true
    const res = await fetch(url)
    if (!res.ok) {
      const data = await res.json().catch(()=>({error:'Unknown error'}))
      throw new Error(data.error || 'Export failed')
    }
    const blob = await res.blob()
    const dl = document.createElement('a')
    const objUrl = URL.createObjectURL(blob)
    dl.href = objUrl
    dl.download = `users.${desiredFmt}`
    document.body.appendChild(dl)
    dl.click()
    dl.remove()
    URL.revokeObjectURL(objUrl)
    el.btnExport.innerText = 'Export'
    el.btnExport.disabled = false
  } catch(err) {
    showError(err.message)
    el.btnExport.innerText = 'Export'
    el.btnExport.disabled = false
  }
})

// Utility: escape HTML
function escapeHtml(s){
  if (s === null || s === undefined) return ''
  return s.toString().replace(/[&<>"]+/g, function(tag){
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"':'&quot;' }
    return map[tag] || tag
  })
}

// Small accessibility: allow closing modal on backdrop click
el.modalBackdrop.addEventListener('click', (e) => { if (e.target === el.modalBackdrop) closeModal() })
el.confirmBackdrop.addEventListener('click', (e) => { if (e.target === el.confirmBackdrop) { deleteUserId=null; el.confirmBackdrop.classList.add('hidden') }})

// Initial load
fetchUsers()
