window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.querySelectorAll('#datatablesSimple');
    if (datatablesSimple) {
        [].forEach.call(datatablesSimple, function(data) {
            // do whatever
            new simpleDatatables.DataTable(data);
            });
    }
});
