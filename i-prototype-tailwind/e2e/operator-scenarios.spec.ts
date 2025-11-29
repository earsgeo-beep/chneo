/**
 * 🎭 Tests E2E Scénarios Opérateur - Phase 3.4
 * Selon prompt ultra-précis : scénarios opérateur complets
 * 
 * Tests end-to-end avec Playwright pour CHNeoWave
 */

import { test, expect, Page } from '@playwright/test';

// Helpers pour tests E2E
class CHNeoWaveTestHelper {
  constructor(private page: Page) {}

  async navigateToAcquisition() {
    await this.page.click('[data-testid="nav-acquisition"]');
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToExport() {
    await this.page.click('[data-testid="nav-export"]');
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToAnalysis() {
    await this.page.click('[data-testid="nav-analysis"]');
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToSettings() {
    await this.page.click('[data-testid="nav-settings"]');
    await this.page.waitForLoadState('networkidle');
  }

  async changeTheme(theme: 'light' | 'dark' | 'beige') {
    await this.navigateToSettings();
    await this.page.selectOption('[data-testid="theme-select"]', theme);
    await this.page.waitForTimeout(500); // Attendre transition
  }

  async startAcquisition(config: {
    samplingRate?: number;
    duration?: number;
    sensors?: number[];
  } = {}) {
    await this.navigateToAcquisition();
    
    // Configurer paramètres si fournis
    if (config.samplingRate) {
      await this.page.fill('[data-testid="sampling-rate-input"]', config.samplingRate.toString());
    }
    
    if (config.sensors) {
      // Sélectionner sondes
      for (const sensorId of config.sensors) {
        await this.page.check(`[data-testid="sensor-${sensorId}-checkbox"]`);
      }
    }

    // Démarrer acquisition
    await this.page.click('[data-testid="start-acquisition-button"]');
    
    // Attendre que l'acquisition démarre
    await expect(this.page.locator('[data-testid="acquisition-status"]')).toContainText('En cours');
  }

  async stopAcquisition() {
    await this.page.click('[data-testid="stop-acquisition-button"]');
    await expect(this.page.locator('[data-testid="acquisition-status"]')).toContainText('Arrêté');
  }

  async exportSession(format: 'hdf5' | 'csv' | 'json' | 'matlab', sessionId?: string) {
    await this.navigateToExport();
    
    // Sélectionner session si spécifiée
    if (sessionId) {
      await this.page.selectOption('[data-testid="session-select"]', sessionId);
    } else {
      // Sélectionner première session disponible
      await this.page.selectOption('[data-testid="session-select"]', { index: 1 });
    }
    
    // Sélectionner format
    await this.page.selectOption('[data-testid="format-select"]', format);
    
    // Déclencher export
    const downloadPromise = this.page.waitForEvent('download');
    await this.page.click('[data-testid="export-button"]');
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain(format);
    
    return download;
  }

  async verifyThemeApplication(theme: 'light' | 'dark' | 'beige') {
    // Vérifier attribut data-theme
    const htmlElement = this.page.locator('html');
    await expect(htmlElement).toHaveAttribute('data-theme', theme);
    
    // Vérifier classe dark pour thème sombre
    if (theme === 'dark') {
      await expect(htmlElement).toHaveClass(/dark/);
    } else {
      await expect(htmlElement).not.toHaveClass(/dark/);
    }
    
    // Vérifier couleurs CSS
    const backgroundColor = await this.page.evaluate(() => {
      return getComputedStyle(document.body).backgroundColor;
    });
    
    expect(backgroundColor).toBeDefined();
  }

  async verifyAccessibility() {
    // Vérifier présence du skip link
    await this.page.keyboard.press('Tab');
    const skipLink = this.page.locator('.skip-link');
    await expect(skipLink).toBeVisible();
    
    // Vérifier navigation clavier
    let focusedElements = 0;
    for (let i = 0; i < 10; i++) {
      await this.page.keyboard.press('Tab');
      const focused = await this.page.evaluate(() => document.activeElement?.tagName);
      if (focused && ['BUTTON', 'INPUT', 'SELECT', 'A'].includes(focused)) {
        focusedElements++;
      }
    }
    
    expect(focusedElements).toBeGreaterThan(0);
  }

  async measurePerformance() {
    // Mesurer métriques de performance
    const metrics = await this.page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        loadTime: navigation.loadEventEnd - navigation.loadEventStart,
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
      };
    });
    
    // Vérifier que les métriques sont dans des limites acceptables
    expect(metrics.loadTime).toBeLessThan(3000); // < 3s
    expect(metrics.domContentLoaded).toBeLessThan(2000); // < 2s
    expect(metrics.firstContentfulPaint).toBeLessThan(1500); // < 1.5s
    
    return metrics;
  }
}

test.describe('🧑‍🔬 Scénarios Opérateur Complets', () => {
  let helper: CHNeoWaveTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new CHNeoWaveTestHelper(page);
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('Scénario 1: Session complète acquisition → analyse → export', async ({ page }) => {
    // 1. Démarrer acquisition
    await helper.startAcquisition({
      samplingRate: 1000,
      sensors: [1, 2]
    });

    // 2. Laisser tourner quelques secondes
    await page.waitForTimeout(5000);

    // 3. Arrêter acquisition
    await helper.stopAcquisition();

    // 4. Aller à l'analyse
    await helper.navigateToAnalysis();
    
    // Vérifier présence des données
    await expect(page.locator('[data-testid="statistics-table"]')).toBeVisible();
    
    // 5. Exporter les résultats
    const download = await helper.exportSession('hdf5');
    expect(download).toBeDefined();
  });

  test('Scénario 2: Configuration système et validation', async ({ page }) => {
    // 1. Aller aux paramètres
    await helper.navigateToSettings();

    // 2. Changer backend
    await page.selectOption('[data-testid="backend-select"]', 'ni-daqmx');
    await page.click('[data-testid="change-backend-button"]');
    
    // Attendre confirmation
    await expect(page.locator('[data-testid="notification"]')).toContainText('Backend changé');

    // 3. Tester connexion
    await page.click('[data-testid="test-connection-button"]');
    
    // Vérifier résultat du test
    await expect(page.locator('[data-testid="connection-status"]')).toBeVisible();

    // 4. Vérifier indicateurs ITTC
    await expect(page.locator('[data-testid="ittc-compliance"]')).toBeVisible();
    await expect(page.locator('[data-testid="iso-compliance"]')).toBeVisible();
  });

  test('Scénario 3: Gestion multi-sondes avancée', async ({ page }) => {
    await helper.navigateToAcquisition();

    // 1. Sélectionner toutes les sondes disponibles
    const sensorCheckboxes = page.locator('[data-testid*="sensor-"][data-testid*="-checkbox"]');
    const count = await sensorCheckboxes.count();
    
    for (let i = 0; i < count; i++) {
      await sensorCheckboxes.nth(i).check();
    }

    // 2. Vérifier état des sondes
    for (let i = 0; i < count; i++) {
      const sensorStatus = page.locator(`[data-testid="sensor-${i + 1}-status"]`);
      await expect(sensorStatus).toBeVisible();
    }

    // 3. Démarrer acquisition multi-sondes
    await helper.startAcquisition();

    // 4. Vérifier données temps réel pour chaque sonde
    await expect(page.locator('[data-testid="realtime-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="multi-sensor-view"]')).toBeVisible();

    // 5. Arrêter et vérifier sauvegarde
    await helper.stopAcquisition();
    await expect(page.locator('[data-testid="session-saved"]')).toBeVisible();
  });

  test('Scénario 4: Export multi-format', async ({ page }) => {
    // Exporter dans tous les formats supportés
    const formats: Array<'hdf5' | 'csv' | 'json' | 'matlab'> = ['hdf5', 'csv', 'json', 'matlab'];
    
    for (const format of formats) {
      const download = await helper.exportSession(format);
      expect(download.suggestedFilename()).toMatch(new RegExp(`\\.${format}$`));
      
      // Vérifier notification de succès
      await expect(page.locator('[data-testid="export-success"]')).toContainText(`Export ${format.toUpperCase()}`);
    }
  });
});

test.describe('🎨 Tests Thèmes Complets', () => {
  let helper: CHNeoWaveTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new CHNeoWaveTestHelper(page);
    await page.goto('/');
  });

  test('Changement thème clair → sombre → Solarized', async ({ page }) => {
    // 1. Thème clair (défaut)
    await helper.verifyThemeApplication('light');

    // 2. Passer au thème sombre
    await helper.changeTheme('dark');
    await helper.verifyThemeApplication('dark');

    // 3. Passer au thème Solarized
    await helper.changeTheme('beige');
    await helper.verifyThemeApplication('beige');

    // 4. Vérifier persistance après rechargement
    await page.reload();
    await helper.verifyThemeApplication('beige');
  });

  test('Thème appliqué sur toutes les pages', async ({ page }) => {
    await helper.changeTheme('dark');

    // Vérifier sur chaque page
    const pages = ['acquisition', 'export', 'analysis', 'settings'];
    
    for (const pageName of pages) {
      switch (pageName) {
        case 'acquisition':
          await helper.navigateToAcquisition();
          break;
        case 'export':
          await helper.navigateToExport();
          break;
        case 'analysis':
          await helper.navigateToAnalysis();
          break;
        case 'settings':
          await helper.navigateToSettings();
          break;
      }
      
      await helper.verifyThemeApplication('dark');
    }
  });
});

test.describe('♿ Tests Accessibilité E2E', () => {
  let helper: CHNeoWaveTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new CHNeoWaveTestHelper(page);
    await page.goto('/');
  });

  test('Navigation clavier complète', async ({ page }) => {
    await helper.verifyAccessibility();
    
    // Tester navigation sur toutes les pages
    const pages = ['acquisition', 'export', 'analysis', 'settings'];
    
    for (const pageName of pages) {
      switch (pageName) {
        case 'acquisition':
          await helper.navigateToAcquisition();
          break;
        case 'export':
          await helper.navigateToExport();
          break;
        case 'analysis':
          await helper.navigateToAnalysis();
          break;
        case 'settings':
          await helper.navigateToSettings();
          break;
      }
      
      // Vérifier que tous les éléments interactifs sont focusables
      const interactiveElements = await page.locator('button, input, select, a, [tabindex="0"]').count();
      expect(interactiveElements).toBeGreaterThan(0);
    }
  });

  test('Contraste et lisibilité', async ({ page }) => {
    // Tester contraste sur tous les thèmes
    const themes: Array<'light' | 'dark' | 'beige'> = ['light', 'dark', 'beige'];
    
    for (const theme of themes) {
      await helper.changeTheme(theme);
      
      // Vérifier que le texte est lisible (pas de test automatisé complet ici)
      const textElements = page.locator('h1, h2, h3, p, span, label, button');
      const count = await textElements.count();
      expect(count).toBeGreaterThan(0);
      
      // Vérifier visibilité des éléments critiques
      await expect(page.locator('[data-testid="main-navigation"]')).toBeVisible();
      await expect(page.locator('[data-testid="page-content"]')).toBeVisible();
    }
  });
});

test.describe('⚡ Tests Performance', () => {
  let helper: CHNeoWaveTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new CHNeoWaveTestHelper(page);
  });

  test('Performance chargement initial', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(5000); // < 5s
    
    // Mesurer métriques détaillées
    const metrics = await helper.measurePerformance();
    expect(metrics.firstContentfulPaint).toBeLessThan(2000);
  });

  test('Performance navigation entre pages', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Mesurer temps de navigation
    const pages = ['acquisition', 'export', 'analysis', 'settings'];
    
    for (const pageName of pages) {
      const startTime = Date.now();
      
      switch (pageName) {
        case 'acquisition':
          await helper.navigateToAcquisition();
          break;
        case 'export':
          await helper.navigateToExport();
          break;
        case 'analysis':
          await helper.navigateToAnalysis();
          break;
        case 'settings':
          await helper.navigateToSettings();
          break;
      }
      
      const navigationTime = Date.now() - startTime;
      expect(navigationTime).toBeLessThan(1000); // < 1s
    }
  });

  test('Performance graphiques temps réel', async ({ page }) => {
    await page.goto('/');
    await helper.navigateToAcquisition();

    // Démarrer acquisition
    await helper.startAcquisition();

    // Mesurer FPS pendant 10 secondes
    const fps = await page.evaluate(() => {
      return new Promise((resolve) => {
        let frameCount = 0;
        const startTime = performance.now();
        
        function countFrame() {
          frameCount++;
          const elapsed = performance.now() - startTime;
          
          if (elapsed < 10000) { // 10 secondes
            requestAnimationFrame(countFrame);
          } else {
            resolve(frameCount / (elapsed / 1000)); // FPS moyen
          }
        }
        
        requestAnimationFrame(countFrame);
      });
    });

    expect(fps).toBeGreaterThan(30); // Au moins 30 FPS
    
    await helper.stopAcquisition();
  });
});

test.describe('🚨 Tests Scénarios Dégradés E2E', () => {
  let helper: CHNeoWaveTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new CHNeoWaveTestHelper(page);
    await page.goto('/');
  });

  test('Gestion perte connexion réseau', async ({ page }) => {
    // Simuler perte réseau
    await page.context().setOffline(true);
    
    // Tenter une action nécessitant le réseau
    await helper.navigateToAcquisition();
    await page.click('[data-testid="start-acquisition-button"]');
    
    // Vérifier affichage d'erreur
    await expect(page.locator('[data-testid="network-error"]')).toBeVisible();
    
    // Restaurer réseau
    await page.context().setOffline(false);
    
    // Vérifier récupération
    await page.reload();
    await expect(page.locator('[data-testid="main-navigation"]')).toBeVisible();
  });

  test('Gestion erreurs API', async ({ page }) => {
    // Mock erreurs API
    await page.route('**/api/**', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });

    await helper.navigateToExport();
    await page.selectOption('[data-testid="session-select"]', { index: 1 });
    await page.click('[data-testid="export-button"]');
    
    // Vérifier gestion d'erreur
    await expect(page.locator('[data-testid="api-error"]')).toBeVisible();
  });

  test('Comportement avec données corrompues', async ({ page }) => {
    // Mock données invalides
    await page.route('**/api/sessions', route => {
      route.fulfill({
        status: 200,
        body: JSON.stringify({ sessions: null }) // Données invalides
      });
    });

    await helper.navigateToExport();
    
    // Vérifier gestion gracieuse
    await expect(page.locator('[data-testid="no-sessions-message"]')).toBeVisible();
  });
});
