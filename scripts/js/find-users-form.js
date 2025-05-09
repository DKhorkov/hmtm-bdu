document.getElementById('searchForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const query = document.getElementById('queryInput').value;
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/sso/users/${encodeURIComponent(query)}`;
    document.body.appendChild(form);
    form.submit();
});
