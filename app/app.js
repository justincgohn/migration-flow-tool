// Migration Flow Tool - Main Application

(function() {
    'use strict';

    // State
    let migrationData = null;
    let countyList = null;
    let currentCounty = null;

    // DOM Elements
    const elements = {
        loading: document.getElementById('loading'),
        searchView: document.getElementById('search-view'),
        resultsView: document.getElementById('results-view'),
        searchInput: document.getElementById('county-search'),
        searchResults: document.getElementById('search-results'),
        backBtn: document.getElementById('back-btn'),
        countyName: document.getElementById('county-name'),
        netMigration: document.getElementById('net-migration'),
        agiLeaving: document.getElementById('agi-leaving'),
        agiArriving: document.getElementById('agi-arriving'),
        outflowTable: document.getElementById('outflow-table').querySelector('tbody'),
        inflowTable: document.getElementById('inflow-table').querySelector('tbody'),
        limitedDataNotice: document.getElementById('limited-data-notice'),
        featuredCounties: document.querySelectorAll('.featured-county')
    };

    // Initialize
    async function init() {
        try {
            // Load data files
            const [dataResponse, listResponse] = await Promise.all([
                fetch('data/migration_data.json'),
                fetch('data/county_list.json')
            ]);

            migrationData = await dataResponse.json();
            countyList = await listResponse.json();

            // Hide loading, show app
            elements.loading.classList.add('hidden');

            // Set up event listeners
            setupEventListeners();

            // Check URL for direct county link
            handleInitialRoute();

        } catch (error) {
            console.error('Failed to load data:', error);
            elements.loading.textContent = 'Failed to load data. Please refresh.';
        }
    }

    function setupEventListeners() {
        // Search input
        elements.searchInput.addEventListener('input', handleSearchInput);
        elements.searchInput.addEventListener('focus', handleSearchInput);
        elements.searchInput.addEventListener('keydown', handleSearchKeydown);

        // Click outside to close search results
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                elements.searchResults.classList.remove('active');
            }
        });

        // Back button
        elements.backBtn.addEventListener('click', showSearchView);

        // Featured counties
        elements.featuredCounties.forEach(btn => {
            btn.addEventListener('click', () => {
                const fips = btn.dataset.fips;
                showCounty(fips);
            });
        });

        // Handle browser back/forward
        window.addEventListener('popstate', handleInitialRoute);
    }

    function handleSearchInput() {
        const query = elements.searchInput.value.trim().toLowerCase();

        if (query.length < 2) {
            elements.searchResults.classList.remove('active');
            return;
        }

        // Filter counties
        const matches = countyList
            .filter(c => c.name.toLowerCase().includes(query))
            .slice(0, 10);

        if (matches.length === 0) {
            elements.searchResults.innerHTML = '<div class="search-result-item">No counties found</div>';
        } else {
            elements.searchResults.innerHTML = matches
                .map((c, i) => `<div class="search-result-item" data-fips="${c.fips}" data-index="${i}">${c.name}</div>`)
                .join('');

            // Add click handlers
            elements.searchResults.querySelectorAll('.search-result-item').forEach(item => {
                item.addEventListener('click', () => {
                    const fips = item.dataset.fips;
                    if (fips) showCounty(fips);
                });
            });
        }

        elements.searchResults.classList.add('active');
    }

    function handleSearchKeydown(e) {
        const items = elements.searchResults.querySelectorAll('.search-result-item[data-fips]');
        const selected = elements.searchResults.querySelector('.selected');
        let selectedIndex = selected ? parseInt(selected.dataset.index) : -1;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
            updateSelectedItem(items, selectedIndex);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, 0);
            updateSelectedItem(items, selectedIndex);
        } else if (e.key === 'Enter' && selected) {
            e.preventDefault();
            const fips = selected.dataset.fips;
            if (fips) showCounty(fips);
        } else if (e.key === 'Escape') {
            elements.searchResults.classList.remove('active');
        }
    }

    function updateSelectedItem(items, index) {
        items.forEach((item, i) => {
            item.classList.toggle('selected', i === index);
        });
    }

    function showCounty(fips) {
        const county = migrationData[fips];
        if (!county) {
            console.error('County not found:', fips);
            return;
        }

        currentCounty = county;

        // Update URL
        const slug = county.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
        history.pushState({ fips }, county.name, `#${slug}`);

        // Update page title
        document.title = `${county.name} Migration — Where Are People Moving?`;

        // Clear search
        elements.searchInput.value = '';
        elements.searchResults.classList.remove('active');

        // Display data
        displayCountyData(county);

        // Switch views
        elements.searchView.classList.remove('active');
        elements.resultsView.classList.add('active');

        // Scroll to top
        window.scrollTo(0, 0);
    }

    function displayCountyData(county) {
        const summary = county.summary;

        // County name
        elements.countyName.textContent = county.name;

        // Summary stats
        const netVal = summary.net_migration;
        const netText = netVal >= 0 ? `+${netVal.toLocaleString()}` : netVal.toLocaleString();
        elements.netMigration.textContent = `${netText} households`;
        elements.netMigration.className = `stat-value ${netVal >= 0 ? 'positive' : 'negative'}`;

        elements.agiLeaving.textContent = formatCurrency(summary.avg_agi_leaving);
        elements.agiArriving.textContent = formatCurrency(summary.avg_agi_arriving);

        // Outflow table
        elements.outflowTable.innerHTML = county.outflows
            .slice(0, 5)
            .map((flow, i) => `
                <tr>
                    <td>${i + 1}</td>
                    <td class="county-link" data-fips="${flow.dest_fips}">${flow.destination}</td>
                    <td>${flow.households.toLocaleString()}</td>
                    <td>${formatCurrency(flow.avg_agi)}</td>
                </tr>
            `)
            .join('');

        // Inflow table
        elements.inflowTable.innerHTML = county.inflows
            .slice(0, 5)
            .map((flow, i) => `
                <tr>
                    <td>${i + 1}</td>
                    <td class="county-link" data-fips="${flow.origin_fips}">${flow.origin}</td>
                    <td>${flow.households.toLocaleString()}</td>
                    <td>${formatCurrency(flow.avg_agi)}</td>
                </tr>
            `)
            .join('');

        // Add click handlers for county links
        document.querySelectorAll('.county-link').forEach(link => {
            link.addEventListener('click', () => {
                const fips = link.dataset.fips;
                if (fips && migrationData[fips]) {
                    showCounty(fips);
                }
            });
        });

        // Show limited data notice if needed
        const totalFlows = county.outflows.length + county.inflows.length;
        elements.limitedDataNotice.style.display = totalFlows < 5 ? 'block' : 'none';
    }

    function showSearchView() {
        elements.resultsView.classList.remove('active');
        elements.searchView.classList.add('active');
        history.pushState(null, '', window.location.pathname);
        document.title = 'County Migration Flows — Where Are People Moving?';
        elements.searchInput.focus();
    }

    function handleInitialRoute() {
        const hash = window.location.hash.slice(1);
        if (!hash || !migrationData) {
            elements.searchView.classList.add('active');
            return;
        }

        // Find county by slug
        const slug = hash.toLowerCase();
        for (const [fips, county] of Object.entries(migrationData)) {
            const countySlug = county.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
            if (countySlug === slug) {
                showCounty(fips);
                return;
            }
        }

        // Not found, show search
        elements.searchView.classList.add('active');
    }

    function formatCurrency(value) {
        if (!value || value === 0) return 'N/A';
        return '$' + value.toLocaleString();
    }

    // Start
    init();
})();
