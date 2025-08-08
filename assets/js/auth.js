// Authentication related functions
async function startAuth(provider) {
  return apiFetch(`/api/auth/${provider}/start`, { method: 'POST' });
}
