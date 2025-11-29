/**
 * Application JavaScript pour le Dashboard d'Instrumentation Maritime
 * Gestion des interactions utilisateur et communication avec l'API
 */

// =============================================================================
// CONFIGURATION ET VARIABLES GLOBALES
// =============================================================================

const API_BASE_URL = 'http://localhost:8001/api';
let currentSection = 'dashboard';
let equipementsData = [];
let servicesData = [];
let charts = {};

// =============================================================================
// INITIALISATION DE L'APPLICATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        // Initialiser la navigation
        initializeNavigation();
        
        // Charger les données initiales
        await loadInitialData();
        
        // Initialiser le dashboard
        await initializeDashboard();
        
        // Initialiser les événements
        initializeEventListeners();
        
        console.log('Application initialisée avec succès');
    } catch (error) {
        console.error('Erreur lors de l\'initialisation:', error);
        showError('Erreur lors du chargement de l\'application');
    }
}

// =============================================================================
// NAVIGATION
// =============================================================================

function initializeNavigation() {
    const navLinks = document.querySelectorAll('[data-section]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            navigateToSection(section);
        });
    });
}

function navigateToSection(section) {
    // Masquer toutes les sections
    document.querySelectorAll('.content-section').forEach(el => {
        el.style.display = 'none';
    });
    
    // Afficher la section demandée
    const targetSection = document.getElementById(`${section}-section`);
    if (targetSection) {
        targetSection.style.display = 'block';
        currentSection = section;
        
        // Mettre à jour la navigation active
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');
        
        // Charger les données spécifiques à la section
        loadSectionData(section);
    }
}

async function loadSectionData(section) {
    switch(section) {
        case 'dashboard':
            await initializeDashboard();
            break;
        case 'equipements':
            await loadEquipements();
            break;
        case 'metrologie':
            // À implémenter
            break;
        case 'projets':
            // À implémenter
            break;
        case 'maintenance':
            // À implémenter
            break;
        case 'rapports':
            // À implémenter
            break;
    }
}

// =============================================================================
// CHARGEMENT DES DONNÉES
// =============================================================================

async function loadInitialData() {
    try {
        // Charger les services
        const servicesResponse = await fetch(`${API_BASE_URL}/services`);
        if (servicesResponse.ok) {
            servicesData = await servicesResponse.json();
            populateServiceFilters();
        }
    } catch (error) {
        console.error('Erreur lors du chargement des données initiales:', error);
    }
}

function populateServiceFilters() {
    const serviceSelect = document.getElementById('filter-service');
    if (serviceSelect) {
        serviceSelect.innerHTML = '<option value="">Tous les services</option>';
        servicesData.forEach(service => {
            const option = document.createElement('option');
            option.value = service.id;
            option.textContent = service.nom;
            serviceSelect.appendChild(option);
        });
    }
}

// =============================================================================
// DASHBOARD
// =============================================================================

async function initializeDashboard() {
    try {
        // Charger les statistiques
        await loadDashboardStats();
        
        // Charger les alertes métrologiques
        await loadAlertesMetrologie();
        
        // Initialiser les graphiques
        await initializeCharts();
        
    } catch (error) {
        console.error('Erreur lors de l\'initialisation du dashboard:', error);
        showError('Erreur lors du chargement du dashboard');
    }
}

async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/dashboard/stats`);
        if (response.ok) {
            const stats = await response.json();
            
            // Mettre à jour les statistiques
            document.getElementById('total-equipements').textContent = stats.total_equipements;
            document.getElementById('equipements-ok').textContent = stats.equipements_ok;
            document.getElementById('equipements-panne').textContent = stats.equipements_panne;
            document.getElementById('verifications-expirees').textContent = stats.verifications_expirees;
        }
    } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
    }
}

async function loadAlertesMetrologie() {
    const loadingElement = document.getElementById('alertes-loading');
    const containerElement = document.getElementById('alertes-container');
    const tbodyElement = document.getElementById('alertes-tbody');
    
    try {
        const response = await fetch(`${API_BASE_URL}/dashboard/alertes-metrologie`);
        if (response.ok) {
            const alertes = await response.json();
            
            // Construire le tableau des alertes
            tbodyElement.innerHTML = '';
            
            if (alertes.length === 0) {
                tbodyElement.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center text-muted">
                            <i class="fas fa-check-circle text-success me-2"></i>
                            Aucune alerte métrologique
                        </td>
                    </tr>
                `;
            } else {
                alertes.forEach(alerte => {
                    const row = document.createElement('tr');
                    
                    const badgeClass = alerte.statut_alerte === 'EXPIRE' ? 'bg-danger' : 'bg-warning';
                    
                    row.innerHTML = `
                        <td>
                            <strong>${alerte.numero}</strong><br>
                            <small class="text-muted">${alerte.description}</small>
                        </td>
                        <td>${alerte.service}</td>
                        <td>${formatDate(alerte.prochaine_verification)}</td>
                        <td>
                            <span class="badge ${badgeClass} alert-badge">
                                ${alerte.statut_alerte}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary btn-action" 
                                    onclick="planifierVerification(${alerte.id_equipement})">
                                <i class="fas fa-calendar-plus me-1"></i>Planifier
                            </button>
                        </td>
                    `;
                    
                    tbodyElement.appendChild(row);
                });
            }
            
            // Afficher le conteneur et masquer le loading
            loadingElement.style.display = 'none';
            containerElement.style.display = 'block';
        }
    } catch (error) {
        console.error('Erreur lors du chargement des alertes:', error);
        loadingElement.innerHTML = `
            <div class="text-center text-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Erreur lors du chargement des alertes
            </div>
        `;
    }
}

async function initializeCharts() {
    try {
        // Graphique répartition par service
        await createServiceChart();
        
        // Graphique état des équipements
        await createEtatChart();
        
    } catch (error) {
        console.error('Erreur lors de l\'initialisation des graphiques:', error);
    }
}

async function createServiceChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/dashboard/kpi-services`);
        if (response.ok) {
            const kpis = await response.json();
            
            const ctx = document.getElementById('serviceChart').getContext('2d');
            
            if (charts.serviceChart) {
                charts.serviceChart.destroy();
            }
            
            charts.serviceChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: kpis.map(kpi => kpi.service),
                    datasets: [{
                        data: kpis.map(kpi => kpi.total_equipements),
                        backgroundColor: [
                            '#2563eb',
                            '#10b981',
                            '#f59e0b',
                            '#ef4444',
                            '#8b5cf6'
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Erreur lors de la création du graphique services:', error);
    }
}

async function createEtatChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/dashboard/stats`);
        if (response.ok) {
            const stats = await response.json();
            
            const ctx = document.getElementById('etatChart').getContext('2d');
            
            if (charts.etatChart) {
                charts.etatChart.destroy();
            }
            
            charts.etatChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['OK', 'En Panne', 'Maintenance'],
                    datasets: [{
                        label: 'Nombre d\'équipements',
                        data: [
                            stats.equipements_ok,
                            stats.equipements_panne,
                            0 // Maintenance (à ajouter dans l'API)
                        ],
                        backgroundColor: [
                            '#10b981',
                            '#ef4444',
                            '#f59e0b'
                        ],
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Erreur lors de la création du graphique états:', error);
    }
}

// =============================================================================
// GESTION DES ÉQUIPEMENTS
// =============================================================================

async function loadEquipements() {
    const loadingElement = document.getElementById('equipements-loading');
    const containerElement = document.getElementById('equipements-container');
    const tbodyElement = document.getElementById('equipements-tbody');
    
    try {
        const response = await fetch(`${API_BASE_URL}/equipements`);
        if (response.ok) {
            equipementsData = await response.json();
            
            // Construire le tableau des équipements
            tbodyElement.innerHTML = '';
            
            equipementsData.forEach(equipement => {
                const row = document.createElement('tr');
                
                const etatBadge = getEtatBadge(equipement.etat);
                const metrologieBadge = getMetrologieBadge(equipement.statut_metrologique);
                
                row.innerHTML = `
                    <td><strong>${equipement.numero}</strong></td>
                    <td>
                        ${equipement.description}
                        ${equipement.n_inventaire ? `<br><small class="text-muted">Inv: ${equipement.n_inventaire}</small>` : ''}
                    </td>
                    <td>${equipement.marque_type || '-'}</td>
                    <td>${equipement.service ? equipement.service.nom : '-'}</td>
                    <td>${etatBadge}</td>
                    <td>${metrologieBadge}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary btn-action" 
                                    onclick="viewEquipement(${equipement.id_equipement})">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-outline-secondary btn-action" 
                                    onclick="editEquipement(${equipement.id_equipement})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-info btn-action" 
                                    onclick="showMaintenanceHistory(${equipement.id_equipement})">
                                <i class="fas fa-history"></i>
                            </button>
                        </div>
                    </td>
                `;
                
                tbodyElement.appendChild(row);
            });
            
            // Afficher le conteneur et masquer le loading
            loadingElement.style.display = 'none';
            containerElement.style.display = 'block';
        }
    } catch (error) {
        console.error('Erreur lors du chargement des équipements:', error);
        loadingElement.innerHTML = `
            <div class="text-center text-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Erreur lors du chargement des équipements
            </div>
        `;
    }
}

function getEtatBadge(etat) {
    const badges = {
        'OK': '<span class="badge bg-success">OK</span>',
        'EN_PANNE': '<span class="badge bg-danger">En Panne</span>',
        'MAINTENANCE': '<span class="badge bg-warning">Maintenance</span>',
        'REBUT': '<span class="badge bg-secondary">Rebut</span>',
        'REFORME': '<span class="badge bg-dark">Réformé</span>'
    };
    return badges[etat] || `<span class="badge bg-secondary">${etat}</span>`;
}

function getMetrologieBadge(statut) {
    const badges = {
        'CONFORME': '<span class="badge bg-success">Conforme</span>',
        'NON_CONFORME': '<span class="badge bg-danger">Non Conforme</span>',
        'EN_ATTENTE': '<span class="badge bg-warning">En Attente</span>',
        'EXPIRE': '<span class="badge bg-danger">Expiré</span>'
    };
    return badges[statut] || `<span class="badge bg-secondary">${statut}</span>`;
}

// =============================================================================
// ÉVÉNEMENTS ET INTERACTIONS
// =============================================================================

function initializeEventListeners() {
    // Recherche d'équipements
    const searchInput = document.getElementById('search-equipements');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterEquipements, 300));
    }
    
    // Filtres
    const filterService = document.getElementById('filter-service');
    const filterEtat = document.getElementById('filter-etat');
    
    if (filterService) {
        filterService.addEventListener('change', filterEquipements);
    }
    
    if (filterEtat) {
        filterEtat.addEventListener('change', filterEquipements);
    }
}

function filterEquipements() {
    const searchTerm = document.getElementById('search-equipements').value.toLowerCase();
    const serviceFilter = document.getElementById('filter-service').value;
    const etatFilter = document.getElementById('filter-etat').value;
    
    const tbody = document.getElementById('equipements-tbody');
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const equipementId = getEquipementIdFromRow(row);
        const equipement = equipementsData.find(eq => eq.id_equipement == equipementId);
        
        if (!equipement) return;
        
        let visible = true;
        
        // Filtre de recherche
        if (searchTerm) {
            const searchableText = `${equipement.numero} ${equipement.description} ${equipement.marque_type || ''}`.toLowerCase();
            visible = visible && searchableText.includes(searchTerm);
        }
        
        // Filtre service
        if (serviceFilter) {
            visible = visible && equipement.service && equipement.service.id == serviceFilter;
        }
        
        // Filtre état
        if (etatFilter) {
            visible = visible && equipement.etat === etatFilter;
        }
        
        row.style.display = visible ? '' : 'none';
    });
}

function resetFilters() {
    document.getElementById('search-equipements').value = '';
    document.getElementById('filter-service').value = '';
    document.getElementById('filter-etat').value = '';
    filterEquipements();
}

// =============================================================================
// ACTIONS SUR LES ÉQUIPEMENTS
// =============================================================================

function viewEquipement(id) {
    const equipement = equipementsData.find(eq => eq.id_equipement === id);
    if (equipement) {
        alert(`Détails de l'équipement:\n\nNuméro: ${equipement.numero}\nDescription: ${equipement.description}\nMarque: ${equipement.marque_type || 'N/A'}\nÉtat: ${equipement.etat}`);
    }
}

function editEquipement(id) {
    alert(`Édition de l'équipement ${id} - Fonctionnalité en cours de développement`);
}

function showMaintenanceHistory(id) {
    alert(`Historique de maintenance pour l'équipement ${id} - Fonctionnalité en cours de développement`);
}

function showAddEquipementModal() {
    alert('Ajout d\'un nouvel équipement - Fonctionnalité en cours de développement');
}

function planifierVerification(id) {
    alert(`Planification de vérification pour l'équipement ${id} - Fonctionnalité en cours de développement`);
}

// =============================================================================
// FONCTIONS UTILITAIRES
// =============================================================================

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
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

function getEquipementIdFromRow(row) {
    // Extraire l'ID depuis les boutons d'action
    const viewButton = row.querySelector('button[onclick*="viewEquipement"]');
    if (viewButton) {
        const onclick = viewButton.getAttribute('onclick');
        const match = onclick.match(/viewEquipement\((\d+)\)/);
        return match ? parseInt(match[1]) : null;
    }
    return null;
}

function showError(message) {
    // Afficher une notification d'erreur
    console.error(message);
    // Ici, on pourrait intégrer un système de notifications toast
}

function showSuccess(message) {
    // Afficher une notification de succès
    console.log(message);
    // Ici, on pourrait intégrer un système de notifications toast
}

// =============================================================================
// ACTIONS GLOBALES
// =============================================================================

async function refreshDashboard() {
    await initializeDashboard();
    showSuccess('Dashboard actualisé');
}

function exportData() {
    // Simuler un export
    const data = {
        equipements: equipementsData,
        services: servicesData,
        export_date: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `instrumentation_maritime_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showSuccess('Export réalisé avec succès');
}
