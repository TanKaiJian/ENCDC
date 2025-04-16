let allData = [];
let currentPage = 1;
const rowsPerPage = 10;

function displayTablePage(data, page) {
    const tbody = document.getElementById('facilityTableBody');
    tbody.innerHTML = '';

    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedData = data.slice(start, end);

    paginatedData.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.name}</td>
            <td>${row.amenity}</td>
            <td>${row.state}</td>
            <td>${row.latitude}</td>
            <td>${row.longitude}</td>
        `;
        tbody.appendChild(tr);
    });

    renderPagination(data.length, page);
}

function renderPagination(totalRows, currentPage) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    const pageCount = Math.ceil(totalRows / rowsPerPage);

    const prevButton = document.createElement('button');
    prevButton.textContent = '«';
    prevButton.disabled = currentPage === 1;
    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayTablePage(allData, currentPage);
        }
    });
    pagination.appendChild(prevButton);

    for (let i = 1; i <= pageCount; i++) {
        const button = document.createElement('button');
        button.textContent = i;
        if (i === currentPage) button.classList.add('active');
        button.addEventListener('click', () => {
            currentPage = i;
            displayTablePage(allData, currentPage);
        });
        pagination.appendChild(button);
    }

    const nextButton = document.createElement('button');
    nextButton.textContent = '»';
    nextButton.disabled = currentPage === pageCount;
    nextButton.addEventListener('click', () => {
        if (currentPage < pageCount) {
            currentPage++;
            displayTablePage(allData, currentPage);
        }
    });
    pagination.appendChild(nextButton);
}

function loadTable(filter = '') {
    fetch(`/api/data?filter=${filter}`)
        .then(res => res.json())
        .then(data => {
            allData = data;
            currentPage = 1;
            displayTablePage(allData, currentPage);
        });
}

function loadKPI() {
    fetch('/api/kpi')
        .then(res => res.json())
        .then(data => {
            document.querySelector('.kpi-box:nth-child(1) .kpi-value').textContent = data.total_facilities;
            document.querySelector('.kpi-box:nth-child(2) .kpi-value').textContent = data.clinic_count;
            document.querySelector('.kpi-box:nth-child(3) .kpi-value').textContent = data.pharmacy_count;
        });
}

function refreshMap() {
    const iframe = document.getElementById("mapFrame");
    iframe.src = "/map?" + new Date().getTime();
    loadTable();
    loadKPI();
}

function showClinicsOnly() {
    const iframe = document.getElementById("mapFrame");
    iframe.src = "/map/clinic?" + new Date().getTime();
    loadTable('clinic');
    loadKPI();
}

function showPharmaciesOnly() {
    const iframe = document.getElementById("mapFrame");
    iframe.src = "/map/pharmacy?" + new Date().getTime();
    loadTable('pharmacy');
    loadKPI();
}

window.onload = function () {
    loadTable();
    loadKPI();
};

function toggleMap() {
    const toggle = document.getElementById('mapToggle');
    const iframe = document.getElementById('mapFrame');
    const buttons = document.getElementById('filterButtons');

    if (toggle.checked) {
        iframe.src = "/map/polygon?" + new Date().getTime();
        buttons.style.display = "none";
    } else {
        iframe.src = "/map?" + new Date().getTime();
        buttons.style.display = "flex";
    }
}
